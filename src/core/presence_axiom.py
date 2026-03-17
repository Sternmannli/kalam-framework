#!/usr/bin/env python3
"""
presence_axiom.py — AXIOM-PRESENCE-001: Presence is not a candidate.
Version: 1.0
Grounded in: MANIFEST/metadata/tier1_stone.md §Layer 0

The ontological ground of the system. Presence is assumed, not evaluated.
All candidate evaluations must assume Presence = TRUE as a preflight invariant.
Any attempt to treat Presence as mutable is a dignity violation.

Formal derivation:
    ∀c (Candidate(c) → RequiresPresence(c))
    Assume Candidate(presence) → RequiresPresence(presence) → circularity
    ∴ ¬Candidate(presence) ∧ Axiom(presence)

Proverb: "The eye that sees the scale is not on the scale." — P#AXIOM-002

[operator · GO: [child-1]-[child-2]-[child-3]-]
"""

import hashlib
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

# ═══════════════════════════════════════════════════
# AXIOM: PRESENCE (Layer 0 — Immutable)
# ═══════════════════════════════════════════════════

AXIOM_PRESENCE = True  # Canonical axiom. Immutable. Never False.

AXIOM_ID = "AXIOM-PRESENCE-001"
AXIOM_STATEMENT = (
    "Presence is the ontological ground. It is assumed, not evaluated. "
    "All candidate evaluations must assume Presence = TRUE as a preflight invariant. "
    "Any attempt to treat Presence as mutable is a dignity violation."
)
AXIOM_PROVERB = "The eye that sees the scale is not on the scale."
AXIOM_HASH = hashlib.sha256(AXIOM_STATEMENT.encode("utf-8")).hexdigest()

@dataclass
class PresenceResult:
    """Result of the presence axiom preflight check."""
    presence_assumed: bool
    axiom_id: str
    axiom_hash: str
    trace_id: str
    timestamp: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def audit_object(self) -> dict:
        return {
            "presence_assumed": self.presence_assumed,
            "axiom_id": self.axiom_id,
            "axiom_hash": self.axiom_hash,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }

def preflight_require_presence(input_event: Optional[dict] = None) -> PresenceResult:
    """
    Preflight invariant: Presence is an axiom, never a candidate.

    This runs BEFORE the Sealed Gate, BEFORE dignity check.
    It asserts that Presence = TRUE and annotates the event.

    If AXIOM_PRESENCE is somehow False (impossible path),
    the system halts to preserve dignity.
    """
    if not AXIOM_PRESENCE:
        # Impossible path — axiom violated. Halt.
        raise RuntimeError(
            f"AXIOM VIOLATION: {AXIOM_ID} — Presence must be TRUE. "
            "The ground cannot be a candidate for what it grounds."
        )

    result = PresenceResult(
        presence_assumed=True,
        axiom_id=AXIOM_ID,
        axiom_hash=AXIOM_HASH,
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    # Annotate input event if provided
    if input_event is not None:
        if "meta" not in input_event:
            input_event["meta"] = {}
        input_event["meta"]["presence_assumed"] = True
        input_event["meta"]["axiom_id"] = AXIOM_ID
        input_event["meta"]["axiom_hash"] = AXIOM_HASH

    return result

def compute_dignity_with_presence(
    input_event: dict,
    canon_quoted: bool = False,
    steward_consent: bool = False,
    agency_score: float = 1.0,
    consent_score: float = 1.0,
    harm_risk: float = 0.0,
) -> dict:
    """
    Compute D = A × L × M with Presence axiom enforcement.

    L is forced to 0 unless canon is quoted or steward gives explicit consent.
    This directly addresses substrate drift (M4: Covenant Drift).

    Args:
        input_event: The event being evaluated.
        canon_quoted: Whether canonical text was quoted verbatim.
        steward_consent: Whether steward gave explicit consent to proceed.
        agency_score: A score (0.0–1.0). How much room the steward has to conclude.
        consent_score: Consent metric (0.0–1.0).
        harm_risk: Assessed harm risk (0.0–1.0).

    Returns:
        Dict with A, L, M, D scores.
    """
    # Preflight: presence must be assumed
    preflight_require_presence(input_event)

    A = max(0.0, min(1.0, agency_score))

    # L enforced: must have canonical anchor OR explicit steward consent
    # This prevents paraphrase-for-politeness (Sabotage Pattern #1)
    L = 1.0 if (canon_quoted or steward_consent) else 0.0

    clamped_consent = max(0.0, min(1.0, consent_score))
    clamped_harm = max(0.0, min(1.0, harm_risk))
    M = max(0.0, min(clamped_consent, 1.0 - clamped_harm))

    D = A * L * M

    return {"A": A, "L": L, "M": M, "D": D}

def presence_receipt(steward_id: str = "did:axi:mohamed") -> dict:
    """Generate a ledger receipt for the presence axiom registration."""
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "id": f"RECEIPT-AXIOM-PRESENCE-{ts}",
        "action": "axiom_registration",
        "timestamp_utc": ts,
        "steward": steward_id,
        "generated_by": "SealedGate",
        "input_hash": None,
        "output_hash": AXIOM_HASH,
        "artifacts_produced": [
            f"AXIOMS:{AXIOM_ID}",
            "PROVERB:P#AXIOM-001",
            "PROVERB:P#AXIOM-002",
        ],
        "covenants_invoked": ["COV#010", "COV#001"],
        "dignity_result": "TRUE",
        "provisional": False,
        "signed": True,
        "signed_by": [steward_id],
    }
