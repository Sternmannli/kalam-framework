#!/usr/bin/env python3
"""
signing.py — Ed25519 Multi-Signature Signing CLI for JSON Manifests

Real cryptographic signing for governance artifacts and canonical manifests.
Supports keypair generation, signing, co-signing, verification, and
N-of-M multi-signature threshold checks.

Dependencies: pip install pynacl

Commands:
  gen     — Generate Ed25519 keypair
  sign    — Sign a JSON manifest
  add     — Add a co-signature to an already-signed manifest
  verify  — Verify all signatures on a signed manifest
  multisig-check — Verify N-of-M threshold is met

Usage:
  python signing.py gen --out-dir keys/signer1
  python signing.py sign --key keys/signer1/private.hex --in manifest.json --out signed.json
  python signing.py add --key keys/signer2/private.hex --in signed.json --out signed_2.json
  python signing.py verify --in signed_2.json
  python signing.py multisig-check --in signed_2.json --threshold 2
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    from nacl.exceptions import BadSignatureError
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False


def _require_nacl():
    if not NACL_AVAILABLE:
        print("ERROR: PyNaCl is required. Install with: pip install pynacl", file=sys.stderr)
        sys.exit(1)


def _canonical_json(data: dict) -> bytes:
    """RFC-8785-style canonical JSON: sorted keys, minimal whitespace, UTF-8."""
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode("utf-8")


def gen_keys(out_dir: str):
    """Generate an Ed25519 keypair and write to hex files."""
    _require_nacl()
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    sk = SigningKey.generate()
    vk = sk.verify_key
    priv_hex = sk.encode(encoder=HexEncoder).decode()
    pub_hex = vk.encode(encoder=HexEncoder).decode()
    (p / "private.hex").write_text(priv_hex)
    (p / "public.hex").write_text(pub_hex)
    print(f"Generated keypair in {p}")
    print(f"Public key: {pub_hex}")
    print(f"SECURITY: Keep private.hex safe. Never commit it to git.")


def sign_manifest(key_path: str, manifest_path: str, out_path: str):
    """Sign a JSON manifest with an Ed25519 key."""
    _require_nacl()
    sk_hex = Path(key_path).read_text().strip()
    sk = SigningKey(sk_hex, encoder=HexEncoder)
    pub_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    manifest_bytes = _canonical_json(manifest)
    sig = sk.sign(manifest_bytes).signature.hex()
    signed = {
        "manifest": manifest,
        "signatures": [{"public_key": pub_hex, "signature": sig, "algorithm": "Ed25519"}]
    }
    Path(out_path).write_text(json.dumps(signed, indent=2, ensure_ascii=False))
    print(f"Signed manifest written to {out_path}")
    print(f"Signer public key: {pub_hex}")


def add_signature(existing_path: str, key_path: str, out_path: str):
    """Add another signature to an existing signed manifest."""
    _require_nacl()
    data = json.loads(Path(existing_path).read_text(encoding="utf-8"))
    manifest = data.get("manifest")
    if manifest is None:
        print("ERROR: No 'manifest' field found in input file.", file=sys.stderr)
        sys.exit(1)
    manifest_bytes = _canonical_json(manifest)
    sk_hex = Path(key_path).read_text().strip()
    sk = SigningKey(sk_hex, encoder=HexEncoder)
    pub_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    existing_keys = {s["public_key"] for s in data.get("signatures", [])}
    if pub_hex in existing_keys:
        print(f"WARNING: This key ({pub_hex[:16]}...) has already signed this manifest.", file=sys.stderr)
        sys.exit(1)
    sig = sk.sign(manifest_bytes).signature.hex()
    data.setdefault("signatures", []).append({"public_key": pub_hex, "signature": sig, "algorithm": "Ed25519"})
    Path(out_path).write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Added signature from {pub_hex[:16]}...")
    print(f"Total signatures: {len(data['signatures'])}")


def verify_signed(path: str) -> bool:
    """Verify all signatures on a signed manifest."""
    _require_nacl()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    manifest = data.get("manifest")
    if manifest is None:
        print("ERROR: No 'manifest' field found.", file=sys.stderr)
        return False
    manifest_bytes = _canonical_json(manifest)
    sigs = data.get("signatures", [])
    if not sigs:
        print("WARNING: No signatures found.")
        return False
    all_valid = True
    print(f"Verifying {len(sigs)} signature(s):")
    for i, s in enumerate(sigs):
        pub = s["public_key"]
        sig_bytes = bytes.fromhex(s["signature"])
        vk = VerifyKey(pub, encoder=HexEncoder)
        try:
            vk.verify(manifest_bytes, sig_bytes)
            print(f"  [{i+1}] {pub[:16]}... => VALID")
        except BadSignatureError:
            print(f"  [{i+1}] {pub[:16]}... => INVALID")
            all_valid = False
    if all_valid:
        print(f"Result: ALL {len(sigs)} signatures VALID")
    else:
        print("Result: SOME SIGNATURES INVALID")
    return all_valid


def multisig_check(path: str, threshold: int) -> bool:
    """Check if N-of-M multi-sig threshold is met."""
    _require_nacl()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    manifest = data.get("manifest")
    if manifest is None:
        print("ERROR: No 'manifest' field found.", file=sys.stderr)
        return False
    manifest_bytes = _canonical_json(manifest)
    sigs = data.get("signatures", [])
    valid_count = 0
    for s in sigs:
        pub = s["public_key"]
        sig_bytes = bytes.fromhex(s["signature"])
        vk = VerifyKey(pub, encoder=HexEncoder)
        try:
            vk.verify(manifest_bytes, sig_bytes)
            valid_count += 1
        except BadSignatureError:
            pass
    met = valid_count >= threshold
    print(f"Multi-sig check: {valid_count}/{len(sigs)} valid, threshold={threshold} => {'MET' if met else 'NOT MET'}")
    return met


def main():
    parser = argparse.ArgumentParser(description="Ed25519 Multi-Signature Signing CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("gen", help="Generate Ed25519 keypair")
    p_gen.add_argument("--out-dir", default="keys/", help="Directory to write keys")

    p_sign = sub.add_parser("sign", help="Sign a JSON manifest")
    p_sign.add_argument("--key", required=True, help="Path to private.hex")
    p_sign.add_argument("--in", required=True, dest="infile")
    p_sign.add_argument("--out", required=True, dest="outfile")

    p_add = sub.add_parser("add", help="Add co-signature to existing signed manifest")
    p_add.add_argument("--key", required=True)
    p_add.add_argument("--in", required=True, dest="infile")
    p_add.add_argument("--out", required=True, dest="outfile")

    p_verify = sub.add_parser("verify", help="Verify all signatures")
    p_verify.add_argument("--in", required=True, dest="infile")

    p_multi = sub.add_parser("multisig-check", help="Check N-of-M threshold")
    p_multi.add_argument("--in", required=True, dest="infile")
    p_multi.add_argument("--threshold", required=True, type=int)

    args = parser.parse_args()

    if args.cmd == "gen":
        gen_keys(args.out_dir)
    elif args.cmd == "sign":
        sign_manifest(args.key, args.infile, args.outfile)
    elif args.cmd == "add":
        add_signature(args.infile, args.key, args.outfile)
    elif args.cmd == "verify":
        sys.exit(0 if verify_signed(args.infile) else 1)
    elif args.cmd == "multisig-check":
        sys.exit(0 if multisig_check(args.infile, args.threshold) else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
