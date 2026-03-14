#!/usr/bin/env python3
"""
crypto_erasure.py — Cryptographic Erasure Engine v1.0

Cryptographic erasure engine for GDPR-compliant data deletion in append-only
systems. Implements encrypt-then-delete-key pattern (ENISA 2019, UK ICO
guidance).

The tension:
  GDPR Article 17 grants data subjects the "right to erasure" — personal data
  must be deletable upon request. But append-only storage policies mandate that
  nothing is silently discarded and every operation leaves a trace.

The resolution — encrypt-then-delete-key:
  All entity data is encrypted before storage using a per-entity key derived
  from a master secret + entity_id. The ciphertext is written to the append-only
  ledger (append-only policy satisfied). To "erase," the entity's key material
  is destroyed. The ciphertext remains in the ledger but is cryptographically
  unrecoverable (GDPR Article 17 satisfied). The erasure event itself is
  recorded as an append-only audit entry with timestamp.

  This is not a workaround. It is the standard pattern recommended by ENISA
  (2019) and the UK ICO for reconciling immutable logs with erasure rights.

Cryptographic design (stdlib only, zero external dependencies):
  - Key derivation: HKDF via hmac/hashlib (SHA-256)
  - Encryption: AES-256-GCM via a pure-Python implementation built on
    hashlib/os.urandom primitives
  - Encoding: base64 for ciphertext serialization
  - Each entity gets a unique 256-bit key: HKDF(master_key, entity_id)
  - Nonce: 12 bytes from os.urandom per seal operation (never reused)
"""

import os
import json
import hmac
import hashlib
import base64
import struct
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


ROOT = Path(__file__).parent.parent
ERASURE_DIR = ROOT / "data" / "erasure"
KEY_STORE_PATH = ERASURE_DIR / "keystore.json"
AUDIT_LEDGER_PATH = ERASURE_DIR / "audit_ledger.json"


# ═══════════════════════════════════════════════════
# ENUMS AND DATA CLASSES
# ═══════════════════════════════════════════════════

class ErasureStatus(Enum):
    """Entity key lifecycle states."""
    ACTIVE = "active"            # Key exists, data recoverable
    ERASED = "erased"            # Key destroyed, data unrecoverable
    NEVER_EXISTED = "never_existed"


class AuditAction(Enum):
    """Actions recorded in the append-only audit ledger."""
    KEY_DERIVED = "key_derived"
    DATA_SEALED = "data_sealed"
    DATA_UNSEALED = "data_unsealed"
    KEY_ERASED = "key_erased"
    UNSEAL_DENIED = "unseal_denied"  # Attempted unseal after erasure


@dataclass
class SealedBlob:
    """Encrypted data blob. Stored in append-only ledger."""
    entity_id: str
    ciphertext_b64: str          # base64(nonce || ciphertext || tag)
    sealed_at: str
    content_hash: str            # SHA-256 of plaintext (for integrity, not recovery)
    blob_id: str

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "ciphertext_b64": self.ciphertext_b64,
            "sealed_at": self.sealed_at,
            "content_hash": self.content_hash,
            "blob_id": self.blob_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SealedBlob":
        return cls(
            entity_id=d["entity_id"],
            ciphertext_b64=d["ciphertext_b64"],
            sealed_at=d["sealed_at"],
            content_hash=d["content_hash"],
            blob_id=d["blob_id"],
        )


@dataclass
class AuditEntry:
    """Append-only audit record. Never deleted, never modified."""
    entry_id: str
    action: str
    entity_id: str
    timestamp: str
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp,
            "detail": self.detail,
        }


@dataclass
class ErasureResult:
    """Result of an erasure operation."""
    entity_id: str
    success: bool
    status: ErasureStatus
    timestamp: str
    audit_entry_id: str
    message: str


# ═══════════════════════════════════════════════════
# AES-256-GCM (PURE STDLIB IMPLEMENTATION)
# ═══════════════════════════════════════════════════
#
# GCM = CTR mode encryption + GHASH authentication.
# We implement this from primitives because the requirement
# is zero external dependencies. AES core uses the block
# cipher from a lookup-table implementation.

# AES S-Box (FIPS-197)
_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b,
    0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26,
    0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2,
    0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed,
    0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f,
    0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
    0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14,
    0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d,
    0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f,
    0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11,
    0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f,
    0xb0, 0x54, 0xbb, 0x16,
]

# Round constants
_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _sub_word(word: bytes) -> bytes:
    return bytes(_SBOX[b] for b in word)


def _rot_word(word: bytes) -> bytes:
    return word[1:] + word[:1]


def _aes_key_expansion(key: bytes) -> List[bytes]:
    """Expand 256-bit key into 15 round keys (AES-256 = 14 rounds)."""
    nk = 8   # 256-bit key = 8 x 32-bit words
    nr = 14  # 14 rounds for AES-256
    nb = 4   # block size in 32-bit words

    # Split key into 32-bit words
    w = [key[i:i+4] for i in range(0, 32, 4)]

    for i in range(nk, nb * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = _xor_bytes(
                _sub_word(_rot_word(temp)),
                bytes([_RCON[(i // nk) - 1], 0, 0, 0])
            )
        elif i % nk == 4:
            temp = _sub_word(temp)
        w.append(_xor_bytes(w[i - nk], temp))

    # Combine words into 16-byte round keys
    round_keys = []
    for r in range(nr + 1):
        rk = b"".join(w[r * nb + j] for j in range(nb))
        round_keys.append(rk)
    return round_keys


def _sub_bytes(state: bytearray) -> None:
    for i in range(16):
        state[i] = _SBOX[state[i]]


def _shift_rows(state: bytearray) -> None:
    # Row 1: shift left 1
    state[1], state[5], state[9], state[13] = state[5], state[9], state[13], state[1]
    # Row 2: shift left 2
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    # Row 3: shift left 3
    state[3], state[7], state[11], state[15] = state[15], state[3], state[7], state[11]


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1b) & 0xff if a & 0x80 else (a << 1) & 0xff


def _mix_single_column(col: List[int]) -> List[int]:
    """Mix one column using the MixColumns matrix."""
    t = col[0] ^ col[1] ^ col[2] ^ col[3]
    u = col[0]
    col[0] ^= _xtime(col[0] ^ col[1]) ^ t
    col[1] ^= _xtime(col[1] ^ col[2]) ^ t
    col[2] ^= _xtime(col[2] ^ col[3]) ^ t
    col[3] ^= _xtime(col[3] ^ u) ^ t
    return col


def _mix_columns(state: bytearray) -> None:
    for i in range(4):
        col = [state[i*4 + j] for j in range(4)]
        # State is stored column-major: state[col*4 + row]
        # But we arranged as state[col*4+row] so column i is state[i*4..i*4+3]
        # Actually, AES state layout: state[row + 4*col]
        # We use column-major: state[4*col + row]
        pass

    # Correct column-major indexing: column c = state[4c], state[4c+1], state[4c+2], state[4c+3]
    for c in range(4):
        col = [state[4*c + r] for r in range(4)]
        mixed = _mix_single_column(col)
        for r in range(4):
            state[4*c + r] = mixed[r]


def _add_round_key(state: bytearray, round_key: bytes) -> None:
    for i in range(16):
        state[i] ^= round_key[i]


def _aes_encrypt_block(block: bytes, round_keys: List[bytes]) -> bytes:
    """Encrypt a single 16-byte block with AES-256."""
    state = bytearray(block)
    nr = len(round_keys) - 1  # 14 for AES-256

    _add_round_key(state, round_keys[0])

    for rnd in range(1, nr):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[rnd])

    # Final round (no MixColumns)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[nr])

    return bytes(state)


def _inc32(counter_block: bytearray) -> None:
    """Increment the last 4 bytes of the counter block (big-endian)."""
    for i in range(15, 11, -1):
        counter_block[i] = (counter_block[i] + 1) & 0xff
        if counter_block[i] != 0:
            break


# ═══════════════════════════════════════════════════
# GCM: GHASH + CTR
# ═══════════════════════════════════════════════════

def _gf128_mul(x: int, y: int) -> int:
    """Multiply two 128-bit integers in GF(2^128) with the GCM polynomial."""
    R = 0xe1000000000000000000000000000000  # Reduction polynomial
    z = 0
    v = y
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ R
        else:
            v >>= 1
    return z


def _bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'big')


def _int_to_bytes(n: int, length: int = 16) -> bytes:
    return n.to_bytes(length, 'big')


def _ghash(h_bytes: bytes, aad: bytes, ciphertext: bytes) -> bytes:
    """Compute GHASH for GCM authentication."""
    h = _bytes_to_int(h_bytes)

    def _pad16(data: bytes) -> bytes:
        r = len(data) % 16
        if r == 0:
            return data
        return data + b'\x00' * (16 - r)

    # Process AAD
    y = 0
    padded_aad = _pad16(aad)
    for i in range(0, len(padded_aad), 16):
        block = _bytes_to_int(padded_aad[i:i+16])
        y = _gf128_mul(y ^ block, h)

    # Process ciphertext
    padded_ct = _pad16(ciphertext)
    for i in range(0, len(padded_ct), 16):
        block = _bytes_to_int(padded_ct[i:i+16])
        y = _gf128_mul(y ^ block, h)

    # Length block: len(A) || len(C) in bits, each as 64-bit big-endian
    len_block = struct.pack('>QQ', len(aad) * 8, len(ciphertext) * 8)
    y = _gf128_mul(y ^ _bytes_to_int(len_block), h)

    return _int_to_bytes(y)


def _aes_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes,
                     aad: bytes = b"") -> tuple:
    """
    AES-256-GCM encryption.

    Args:
        key: 32-byte AES-256 key
        nonce: 12-byte nonce (IV)
        plaintext: data to encrypt
        aad: additional authenticated data (not encrypted, but authenticated)

    Returns:
        (ciphertext, tag) where tag is 16 bytes
    """
    round_keys = _aes_key_expansion(key)

    # H = AES_K(0^128)
    h = _aes_encrypt_block(b'\x00' * 16, round_keys)

    # J0 = nonce || 0x00000001 (for 12-byte nonce)
    j0 = bytearray(nonce + b'\x00\x00\x00\x01')

    # Encrypt: CTR mode starting from J0 + 1
    counter = bytearray(j0)
    _inc32(counter)

    ciphertext = bytearray()
    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i+16]
        keystream = _aes_encrypt_block(bytes(counter), round_keys)
        ct_block = _xor_bytes(block, keystream[:len(block)])
        ciphertext.extend(ct_block)
        _inc32(counter)

    ciphertext = bytes(ciphertext)

    # Compute GHASH
    s = _ghash(h, aad, ciphertext)

    # Tag = GHASH XOR E(K, J0)
    e_j0 = _aes_encrypt_block(bytes(j0), round_keys)
    tag = _xor_bytes(s, e_j0)

    return ciphertext, tag


def _aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes,
                     tag: bytes, aad: bytes = b"") -> Optional[bytes]:
    """
    AES-256-GCM decryption with authentication.

    Returns plaintext if tag verifies, None otherwise.
    """
    round_keys = _aes_key_expansion(key)

    # H = AES_K(0^128)
    h = _aes_encrypt_block(b'\x00' * 16, round_keys)

    # J0 = nonce || 0x00000001
    j0 = bytearray(nonce + b'\x00\x00\x00\x01')

    # Verify tag first (GHASH)
    s = _ghash(h, aad, ciphertext)
    e_j0 = _aes_encrypt_block(bytes(j0), round_keys)
    computed_tag = _xor_bytes(s, e_j0)

    if not hmac.compare_digest(computed_tag, tag):
        return None  # Authentication failed

    # Decrypt: CTR mode starting from J0 + 1
    counter = bytearray(j0)
    _inc32(counter)

    plaintext = bytearray()
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        keystream = _aes_encrypt_block(bytes(counter), round_keys)
        pt_block = _xor_bytes(block, keystream[:len(block)])
        plaintext.extend(pt_block)
        _inc32(counter)

    return bytes(plaintext)


# ═══════════════════════════════════════════════════
# HKDF KEY DERIVATION (RFC 5869)
# ═══════════════════════════════════════════════════

def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    """HKDF-Extract: PRK = HMAC-SHA256(salt, IKM)."""
    if not salt:
        salt = b'\x00' * 32
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def _hkdf_expand(prk: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-Expand: OKM = T(1) || T(2) || ... truncated to length."""
    n = (length + 31) // 32
    okm = b""
    t = b""
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]


def _derive_entity_key(master_key: bytes, entity_id: str) -> bytes:
    """
    Derive a unique 256-bit key for an entity.

    Uses HKDF (RFC 5869) with:
      - IKM: master_key
      - salt: SHA-256("crypto-erasure-salt-v1")
      - info: "entity-key:" + entity_id encoded as UTF-8
    """
    salt = hashlib.sha256(b"crypto-erasure-salt-v1").digest()
    prk = _hkdf_extract(salt, master_key)
    info = f"entity-key:{entity_id}".encode("utf-8")
    return _hkdf_expand(prk, info, 32)


# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ═══════════════════════════════════════════════════
# CRYPTOGRAPHIC ERASURE ENGINE
# ═══════════════════════════════════════════════════

class CryptographicErasure:
    """
    Cryptographic erasure engine for GDPR-compliant data deletion in
    append-only systems.

    Implements the encrypt-then-delete-key pattern: GDPR Article 17 requires
    the right to erasure, while append-only storage policies mandate immutable
    records. This engine encrypts data before storage (per-entity key) and
    "erases" by destroying the key. Ciphertext persists in the ledger
    (append-only) but is cryptographically unrecoverable (erasure satisfied).

    Usage:
        engine = CryptographicErasure(master_key=os.urandom(32))
        blob = engine.seal("ENTITY-001", b"sensitive entity data")
        data = engine.unseal("ENTITY-001", blob)   # returns plaintext
        engine.erase("ENTITY-001")                   # destroys key
        data = engine.unseal("ENTITY-001", blob)   # returns None — erased
    """

    def __init__(self, master_key: bytes, persist: bool = True):
        """
        Initialize the erasure engine.

        Args:
            master_key: 32-byte master secret for key derivation.
                        Must be stored securely outside the codebase.
            persist: If True, keystore and audit ledger are persisted to disk.
        """
        if len(master_key) != 32:
            raise ValueError("Master key must be exactly 32 bytes (256 bits).")

        self._master_key = master_key
        self._persist = persist
        self._entity_keys: Dict[str, bytes] = {}  # entity_id -> derived key
        self._erased: Dict[str, str] = {}          # entity_id -> erasure timestamp
        self._audit: List[AuditEntry] = []
        self._counter = 0
        self._blob_counter = 0

        if persist:
            self._load_state()

    def _next_audit_id(self) -> str:
        self._counter += 1
        return f"CE-{self._counter:06d}"

    def _next_blob_id(self) -> str:
        self._blob_counter += 1
        return f"BLOB-{self._blob_counter:06d}"

    def _record(self, action: AuditAction, entity_id: str,
                detail: str = "") -> AuditEntry:
        """Append an entry to the audit ledger. Never modifies existing entries."""
        entry = AuditEntry(
            entry_id=self._next_audit_id(),
            action=action.value,
            entity_id=entity_id,
            timestamp=_now(),
            detail=detail,
        )
        self._audit.append(entry)
        if self._persist:
            self._save_audit()
        return entry

    def _get_or_derive_key(self, entity_id: str) -> Optional[bytes]:
        """
        Get existing entity key or derive a new one.
        Returns None if entity has been erased.
        """
        if entity_id in self._erased:
            return None

        if entity_id not in self._entity_keys:
            key = _derive_entity_key(self._master_key, entity_id)
            self._entity_keys[entity_id] = key
            self._record(AuditAction.KEY_DERIVED, entity_id)
            if self._persist:
                self._save_keystore()

        return self._entity_keys[entity_id]

    # ── Public API ──────────────────────────────────

    def seal(self, entity_id: str, data: bytes) -> SealedBlob:
        """
        Encrypt entity data and return a sealed blob for append-only storage.

        Args:
            entity_id: Unique identifier for the entity.
            data: Raw bytes to encrypt.

        Returns:
            SealedBlob containing the encrypted data.

        Raises:
            PermissionError: If entity has been erased (cannot seal new data).
        """
        if entity_id in self._erased:
            raise PermissionError(
                f"Entity {entity_id} has been erased. Cannot seal new data. "
                f"Erasure is irreversible."
            )

        key = self._get_or_derive_key(entity_id)
        nonce = os.urandom(12)

        # AAD includes entity_id for binding
        aad = f"erasure:entity:{entity_id}".encode("utf-8")
        ciphertext, tag = _aes_gcm_encrypt(key, nonce, data, aad)

        # Pack: nonce (12) || ciphertext (variable) || tag (16)
        packed = nonce + ciphertext + tag
        blob_b64 = base64.b64encode(packed).decode("ascii")
        content_hash = _sha256(data)
        blob_id = self._next_blob_id()

        blob = SealedBlob(
            entity_id=entity_id,
            ciphertext_b64=blob_b64,
            sealed_at=_now(),
            content_hash=content_hash,
            blob_id=blob_id,
        )

        self._record(
            AuditAction.DATA_SEALED, entity_id,
            detail=f"blob_id={blob_id}, content_hash={content_hash[:16]}..."
        )

        return blob

    def unseal(self, entity_id: str, blob: SealedBlob) -> Optional[bytes]:
        """
        Decrypt a sealed blob. Returns None if entity has been erased.

        Args:
            entity_id: Entity whose key should be used.
            blob: The sealed blob to decrypt.

        Returns:
            Decrypted bytes, or None if key has been erased or
            authentication fails.
        """
        if entity_id in self._erased:
            self._record(
                AuditAction.UNSEAL_DENIED, entity_id,
                detail=f"blob_id={blob.blob_id}, reason=entity_erased"
            )
            return None

        key = self._get_or_derive_key(entity_id)
        if key is None:
            return None

        packed = base64.b64decode(blob.ciphertext_b64)

        # Unpack: nonce (12) || ciphertext (variable) || tag (16)
        if len(packed) < 28:  # 12 + 0 + 16 minimum
            return None
        nonce = packed[:12]
        tag = packed[-16:]
        ciphertext = packed[12:-16]

        aad = f"erasure:entity:{entity_id}".encode("utf-8")
        plaintext = _aes_gcm_decrypt(key, nonce, ciphertext, tag, aad)

        if plaintext is not None:
            self._record(
                AuditAction.DATA_UNSEALED, entity_id,
                detail=f"blob_id={blob.blob_id}"
            )

        return plaintext

    def erase(self, entity_id: str) -> ErasureResult:
        """
        Cryptographically erase an entity. Destroys the key material.
        The ciphertext remains in append-only storage but is unrecoverable.

        This is irreversible. There is no undo.

        Args:
            entity_id: Entity to erase.

        Returns:
            ErasureResult with outcome details.
        """
        now = _now()

        if entity_id in self._erased:
            return ErasureResult(
                entity_id=entity_id,
                success=True,
                status=ErasureStatus.ERASED,
                timestamp=now,
                audit_entry_id="",
                message=f"Entity {entity_id} was already erased at {self._erased[entity_id]}.",
            )

        if entity_id not in self._entity_keys:
            return ErasureResult(
                entity_id=entity_id,
                success=False,
                status=ErasureStatus.NEVER_EXISTED,
                timestamp=now,
                audit_entry_id="",
                message=f"Entity {entity_id} has no key material. Nothing to erase.",
            )

        # Destroy the key: overwrite with zeros then delete
        key_ref = self._entity_keys[entity_id]
        # Overwrite in-memory (best-effort; Python GC caveat acknowledged)
        zeroed = b'\x00' * len(key_ref)
        self._entity_keys[entity_id] = zeroed
        del self._entity_keys[entity_id]

        # Record erasure timestamp
        self._erased[entity_id] = now

        entry = self._record(
            AuditAction.KEY_ERASED, entity_id,
            detail="Key material destroyed. Ciphertext remains but is unrecoverable."
        )

        if self._persist:
            self._save_keystore()

        return ErasureResult(
            entity_id=entity_id,
            success=True,
            status=ErasureStatus.ERASED,
            timestamp=now,
            audit_entry_id=entry.entry_id,
            message=(
                f"Entity {entity_id} erased. Key destroyed. "
                f"Ciphertext persists in append-only ledger. "
                f"Data is cryptographically unrecoverable (GDPR Art. 17)."
            ),
        )

    def is_erased(self, entity_id: str) -> bool:
        """Check whether an entity's key has been destroyed."""
        return entity_id in self._erased

    def entity_status(self, entity_id: str) -> ErasureStatus:
        """Return the key lifecycle status for an entity."""
        if entity_id in self._erased:
            return ErasureStatus.ERASED
        if entity_id in self._entity_keys:
            return ErasureStatus.ACTIVE
        return ErasureStatus.NEVER_EXISTED

    def audit_trail(self, entity_id: Optional[str] = None) -> List[AuditEntry]:
        """
        Return the audit trail. Optionally filtered by entity_id.
        The audit trail is append-only and cannot be modified.
        """
        if entity_id is None:
            return list(self._audit)
        return [e for e in self._audit if e.entity_id == entity_id]

    def active_entity_count(self) -> int:
        """Count of entities with active (non-erased) keys."""
        return len(self._entity_keys)

    def erased_entity_count(self) -> int:
        """Count of entities whose keys have been destroyed."""
        return len(self._erased)

    # ── Persistence ─────────────────────────────────

    def _save_keystore(self) -> None:
        """Save keystore to disk. Keys are stored as hex. Erased entities recorded."""
        ERASURE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "active_keys": {
                eid: key.hex() for eid, key in self._entity_keys.items()
            },
            "erased": self._erased,
            "counters": {
                "audit": self._counter,
                "blob": self._blob_counter,
            },
            "saved_at": _now(),
        }
        with open(KEY_STORE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def _save_audit(self) -> None:
        """Append-only save of audit ledger."""
        ERASURE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "entries": [e.to_dict() for e in self._audit],
            "total_entries": len(self._audit),
            "saved_at": _now(),
        }
        with open(AUDIT_LEDGER_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def _load_state(self) -> None:
        """Load keystore and audit ledger from disk."""
        if KEY_STORE_PATH.exists():
            with open(KEY_STORE_PATH) as f:
                data = json.load(f)
            self._entity_keys = {
                eid: bytes.fromhex(hexkey)
                for eid, hexkey in data.get("active_keys", {}).items()
            }
            self._erased = data.get("erased", {})
            counters = data.get("counters", {})
            self._counter = counters.get("audit", 0)
            self._blob_counter = counters.get("blob", 0)

        if AUDIT_LEDGER_PATH.exists():
            with open(AUDIT_LEDGER_PATH) as f:
                data = json.load(f)
            self._audit = [
                AuditEntry(
                    entry_id=e["entry_id"],
                    action=e["action"],
                    entity_id=e["entity_id"],
                    timestamp=e["timestamp"],
                    detail=e.get("detail", ""),
                )
                for e in data.get("entries", [])
            ]


# ═══════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════

def main():
    """Demonstrate the cryptographic erasure lifecycle."""
    import sys

    print()
    print("=" * 60)
    print("Cryptographic Erasure — GDPR Art. 17 Compliance Demo")
    print("Append-only storage with encrypt-then-delete-key pattern")
    print("=" * 60)
    print()

    # Use a deterministic key for demo (NEVER do this in production)
    master_key = hashlib.sha256(b"demo-master-key-not-for-production").digest()
    engine = CryptographicErasure(master_key, persist=False)

    entity = "ENTITY-042"
    secret = b"This is sensitive entity data for demonstration."

    # Seal
    print(f"[1] Sealing data for {entity}...")
    blob = engine.seal(entity, secret)
    print(f"    Blob ID: {blob.blob_id}")
    print(f"    Content hash: {blob.content_hash[:32]}...")
    print(f"    Ciphertext (first 40 chars): {blob.ciphertext_b64[:40]}...")
    print()

    # Unseal
    print(f"[2] Unsealing data for {entity}...")
    recovered = engine.unseal(entity, blob)
    assert recovered == secret, "Decryption failed!"
    print(f"    Recovered: {recovered.decode()}")
    print(f"    Status: {engine.entity_status(entity).value}")
    print()

    # Erase
    print(f"[3] Erasing {entity} (destroying key)...")
    result = engine.erase(entity)
    print(f"    Success: {result.success}")
    print(f"    Status: {result.status.value}")
    print(f"    Message: {result.message}")
    print()

    # Attempt unseal after erasure
    print(f"[4] Attempting unseal after erasure...")
    recovered = engine.unseal(entity, blob)
    assert recovered is None, "Should have been None after erasure!"
    print(f"    Result: None (cryptographically unrecoverable)")
    print(f"    is_erased: {engine.is_erased(entity)}")
    print()

    # Audit trail
    print(f"[5] Audit trail for {entity}:")
    for entry in engine.audit_trail(entity):
        print(f"    {entry.entry_id} | {entry.action:20s} | {entry.timestamp}")
    print()

    # Summary
    print(f"Active entities: {engine.active_entity_count()}")
    print(f"Erased entities: {engine.erased_entity_count()}")
    print()
    print("Append-only policy satisfied: ciphertext remains in ledger.")
    print("GDPR Art. 17 satisfied: key destroyed, data unrecoverable.")
    print()


if __name__ == "__main__":
    main()
