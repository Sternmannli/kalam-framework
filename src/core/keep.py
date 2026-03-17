#!/usr/bin/env python3
"""
keep.py — kalam KEEP Module v1.0
Memory and Storage. Governs what the system holds, how long, and how it releases.

Covenant obligations:
  COV#010 — Must honor retention policies. No artifact silently discarded.
  COV#012 — All stored artifacts must be named in the manifest.

Core operations: store, retrieve, expire, lock, append
Append-only for canonical artifacts. No overwrite.

[operator · GO: [child-1]-[child-2]-[child-3]-]
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict

ROOT = Path(__file__).parent.parent
KEEP_DIR = ROOT / "KEEP"
LEDGER_FILE = KEEP_DIR / "ledger.json"

@dataclass
class Receipt:
    artifact_id: str
    operation: str
    timestamp: str
    hash: str
    steward: str = "[founder]"
    reason: str = ""

@dataclass
class Artifact:
    id: str
    content: str
    retention_policy: str  # "permanent", "thermal", "session"
    hash: str
    created: str
    locked: bool = False
    expired: bool = False
    expire_reason: str = ""
    history: list = field(default_factory=list)

def _sha(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()

def _now():
    return datetime.now(timezone.utc).isoformat()

def _load_ledger():
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE) as f:
            return json.load(f)
    return {"artifacts": {}, "receipts": []}

def _save_ledger(ledger):
    KEEP_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def store(artifact_id, content, retention_policy="permanent", steward="[founder]"):
    """Store an artifact. Generates a receipt. Never overwrites."""
    ledger = _load_ledger()

    if artifact_id in ledger["artifacts"]:
        existing = ledger["artifacts"][artifact_id]
        if not existing.get("expired", False):
            raise ValueError(
                f"Artifact {artifact_id} already exists and is not expired. "
                f"Use append() for additions or expire() first. No overwrite. (COV#010)"
            )

    h = _sha(content)
    now = _now()

    artifact = {
        "id": artifact_id,
        "content": content,
        "retention_policy": retention_policy,
        "hash": h,
        "created": now,
        "locked": False,
        "expired": False,
        "expire_reason": "",
        "history": [],
    }

    receipt = {
        "artifact_id": artifact_id,
        "operation": "store",
        "timestamp": now,
        "hash": h,
        "steward": steward,
        "reason": "",
    }

    ledger["artifacts"][artifact_id] = artifact
    ledger["receipts"].append(receipt)
    _save_ledger(ledger)
    return receipt

def retrieve(artifact_id):
    """Retrieve an artifact by ID. Returns None if not found."""
    ledger = _load_ledger()
    artifact = ledger["artifacts"].get(artifact_id)
    if artifact is None:
        return None
    if artifact.get("expired", False):
        return None  # Expired artifacts are not retrievable
    return artifact

def expire(artifact_id, reason, steward="[founder]"):
    """Expire an artifact with an explicit reason. Silent expiry is a dignity violation."""
    if not reason or not reason.strip():
        raise ValueError("Expiry requires explicit reason. Silent expiry is a dignity violation. (COV#010)")

    ledger = _load_ledger()
    artifact = ledger["artifacts"].get(artifact_id)
    if artifact is None:
        raise KeyError(f"Artifact {artifact_id} not found.")
    if artifact.get("locked", False):
        raise PermissionError(f"Artifact {artifact_id} is locked. Cannot expire.")

    now = _now()
    artifact["expired"] = True
    artifact["expire_reason"] = reason

    receipt = {
        "artifact_id": artifact_id,
        "operation": "expire",
        "timestamp": now,
        "hash": artifact["hash"],
        "steward": steward,
        "reason": reason,
    }

    ledger["receipts"].append(receipt)
    _save_ledger(ledger)
    return receipt

def lock(artifact_id, steward="[founder]"):
    """Lock an artifact. Prevents modification, not retrieval."""
    ledger = _load_ledger()
    artifact = ledger["artifacts"].get(artifact_id)
    if artifact is None:
        raise KeyError(f"Artifact {artifact_id} not found.")

    now = _now()
    artifact["locked"] = True

    receipt = {
        "artifact_id": artifact_id,
        "operation": "lock",
        "timestamp": now,
        "hash": artifact["hash"],
        "steward": steward,
        "reason": "",
    }

    ledger["receipts"].append(receipt)
    _save_ledger(ledger)
    return receipt

def append(artifact_id, delta, steward="[founder]"):
    """Append-only mode for ledger entries. Never overwrites."""
    ledger = _load_ledger()
    artifact = ledger["artifacts"].get(artifact_id)
    if artifact is None:
        raise KeyError(f"Artifact {artifact_id} not found.")
    if artifact.get("locked", False):
        raise PermissionError(f"Artifact {artifact_id} is locked. Cannot append.")
    if artifact.get("expired", False):
        raise ValueError(f"Artifact {artifact_id} is expired. Cannot append.")

    now = _now()
    old_hash = artifact["hash"]

    # Append to content
    artifact["content"] += "\n" + delta
    artifact["hash"] = _sha(artifact["content"])
    artifact["history"].append({
        "operation": "append",
        "timestamp": now,
        "old_hash": old_hash,
        "new_hash": artifact["hash"],
        "delta_hash": _sha(delta),
    })

    receipt = {
        "artifact_id": artifact_id,
        "operation": "append",
        "timestamp": now,
        "hash": artifact["hash"],
        "steward": steward,
        "reason": "",
    }

    ledger["receipts"].append(receipt)
    _save_ledger(ledger)
    return receipt

def list_artifacts(include_expired=False):
    """List all artifacts in the KEEP ledger."""
    ledger = _load_ledger()
    results = []
    for aid, artifact in ledger["artifacts"].items():
        if not include_expired and artifact.get("expired", False):
            continue
        results.append({
            "id": aid,
            "retention_policy": artifact["retention_policy"],
            "locked": artifact["locked"],
            "expired": artifact["expired"],
            "created": artifact["created"],
        })
    return results

def receipt_count():
    """Return total number of receipts."""
    ledger = _load_ledger()
    return len(ledger["receipts"])
