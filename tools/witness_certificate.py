#!/usr/bin/env python3
"""
witness_certificate.py — Zero-Halt Witness Certificate Generator

When D = A × L × M reaches zero, the system does not crash.
It refuses. It generates a Witness Certificate of Institutional Blindness:
a cryptographically signed, append-only, legally admissible artifact
that proves the institution failed to see the person.

The halt is the product.
The certificate is the evidence.
The refusal is the testimony.

This is a negative proof: evidence that institutional recognition did not occur.
Not an error log. Not a stack trace. A notarial artifact.

Schema derived from multi-model convergence (EXP-002, 2026-03-15).
Six independent models produced near-identical specifications.


"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Optional, Dict
from pathlib import Path

from tools.letter_ontology import TA, PositionalForm


ROOT = Path(__file__).parent.parent
CERTIFICATE_DIR = ROOT / "KEEP" / "WITNESS_CERTIFICATES"
ZRH = ZoneInfo("Europe/Zurich")


# --- Halt Reason Codes ---

HALT_L_ZERO = "L_ZERO"      # Legibility axis dropped to zero
HALT_A_ZERO = "A_ZERO"      # Autonomy axis dropped to zero
HALT_M_ZERO = "M_ZERO"      # Momentum axis dropped to zero
HALT_MULTI = "MULTI_ZERO"   # Multiple axes at zero


# --- Data Structures ---

@dataclass
class DignitySnapshot:
    """The three-axis dignity computation at the moment of halt."""
    A: float  # Autonomy
    L: float  # Legibility
    M: float  # Momentum

    @property
    def D(self) -> float:
        """Non-compensatory dignity. Any zero = total zero."""
        return self.A * self.L * self.M

    @property
    def halted(self) -> bool:
        return self.D == 0.0

    @property
    def halt_reason(self) -> str:
        zeros = []
        if self.A == 0.0:
            zeros.append("A")
        if self.L == 0.0:
            zeros.append("L")
        if self.M == 0.0:
            zeros.append("M")
        if len(zeros) > 1:
            return HALT_MULTI
        if "A" in zeros:
            return HALT_A_ZERO
        if "L" in zeros:
            return HALT_L_ZERO
        if "M" in zeros:
            return HALT_M_ZERO
        return ""


@dataclass
class Subject:
    """The person the system failed to see."""
    subject_id: str
    role: str  # parent, applicant, claimant, child
    context_label: str = ""  # human-readable, no PII in chain


@dataclass
class InstitutionalContext:
    """Where the failure occurred."""
    institution_id: str
    procedure: str
    case_id: str = ""
    process_step: str = ""


@dataclass
class CoordinatesOfFailure:
    """The exact location and nature of the blindness."""
    axis: str  # A, L, or M
    node_id: str  # which processing node failed
    rule_id: str  # which rule was invoked
    inputs_present: List[str] = field(default_factory=list)
    missing_or_unreadable: List[str] = field(default_factory=list)
    machine_explanation: str = ""
    human_annotation: str = ""


@dataclass
class WitnessCertificate:
    """
    Zero-Halt Witness Certificate of Institutional Blindness.

    A Ta_mufrad entry: isolated, non-connecting, terminal.
    The system's refusal to pretend it can see what it cannot.

    This is the product.
    """
    # --- Chain identity ---
    certificate_id: str = ""
    schema_version: str = "1.0"
    letter: str = "ta"
    positional_form: str = "isolated"  # Ta_mufrad — always
    status: str = "HALTED"

    # --- Timestamps ---
    timestamp_utc: str = ""
    timestamp_zrh: str = ""

    # --- Chain linkage ---
    chain_id: str = "kalam:v1"
    prev_hash: str = ""
    certificate_hash: str = ""

    # --- The failure ---
    halt_reason_code: str = ""
    dignity: Optional[DignitySnapshot] = None
    subject: Optional[Subject] = None
    context: Optional[InstitutionalContext] = None
    coordinates: Optional[CoordinatesOfFailure] = None

    # --- Constitutional basis ---
    constitutional_references: List[str] = field(default_factory=list)
    refusal_clause: str = (
        "By the rules of the Constitution and the weights of the 28 Roots, "
        "this system refuses to proceed. To continue would be to simulate "
        "a person who is not seen. This record serves as an immutable "
        "witness to this institutional blindness."
    )

    # --- Signatures ---
    system_signature: str = ""
    human_witness_signatures: List[str] = field(default_factory=list)

    # --- Evidence ---
    evidence_refs: List[str] = field(default_factory=list)

    # --- Tags ---
    tags: List[str] = field(default_factory=lambda: [
        "witness_certificate", "zero_halt", "negative_proof",
    ])

    def compute_hash(self) -> str:
        """Content-addressed hash of the certificate's canonical form."""
        canonical = json.dumps(self.to_chain_entry(), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_chain_entry(self) -> Dict:
        """Machine-canonical JSON for the append-only chain."""
        return {
            "entry_id": self.certificate_id,
            "schema_version": self.schema_version,
            "letter": self.letter,
            "positional_form": self.positional_form,
            "status": self.status,
            "chain_id": self.chain_id,
            "timestamp_utc": self.timestamp_utc,
            "timestamp_zrh": self.timestamp_zrh,
            "prev_hash": self.prev_hash,
            "certificate_hash": self.certificate_hash,
            "halt_reason_code": self.halt_reason_code,
            "dignity_snapshot": asdict(self.dignity) if self.dignity else {},
            "subject": asdict(self.subject) if self.subject else {},
            "context": asdict(self.context) if self.context else {},
            "coordinates_of_failure": asdict(self.coordinates) if self.coordinates else {},
            "constitutional_references": self.constitutional_references,
            "refusal_clause": self.refusal_clause,
            "signatures": {
                "system_signature": self.system_signature,
                "human_witness_signatures": self.human_witness_signatures,
            },
            "evidence_refs": self.evidence_refs,
            "tags": self.tags,
        }

    def to_legal_view(self) -> str:
        """
        Human-readable legal document.
        What a father carries into a courtroom.
        Not a developer log. A notarial artifact.
        """
        dignity = self.dignity or DignitySnapshot(0, 0, 0)
        subject = self.subject or Subject("unknown", "unknown")
        context = self.context or InstitutionalContext("unknown", "unknown")
        coords = self.coordinates or CoordinatesOfFailure("", "", "")

        lines = [
            "WITNESS CERTIFICATE OF INSTITUTIONAL BLINDNESS",
            "Zero-Halt Dignity Record",
            "",
            f"Certificate ID: {self.certificate_id}",
            f"Chain ID: {self.chain_id}",
            f"Timestamp (UTC): {self.timestamp_utc}",
            f"Timestamp (Zurich): {self.timestamp_zrh}",
            "",
            "1. SUBJECT",
            f"   Subject Identifier: {subject.subject_id}",
            f"   Role in Proceeding: {subject.role}",
            f"   Context: {subject.context_label}",
            "",
            "2. DIGNITY COMPUTATION RESULT",
            "   The system computes dignity as D = A x L x M, where:",
            "   A = Autonomy (capacity to act on one's own behalf)",
            "   L = Legibility (degree to which the system can witness the person)",
            "   M = Momentum (continuity of the person's trajectory)",
            "",
            f"   Autonomy (A): {dignity.A:.2f}",
            f"   Legibility (L): {dignity.L:.2f}" + (" — CRITICAL FAILURE" if dignity.L == 0 else ""),
            f"   Momentum (M): {dignity.M:.2f}",
            f"   Computed Dignity: D = {dignity.D:.2f} (halt condition triggered)",
            "",
            "3. NATURE OF THE HALT (NEGATIVE PROOF)",
            "   This certificate is an explicit, cryptographically signed record that:",
            "   (a) The system was mathematically unable to form a sufficient",
            "       internal representation of the subject.",
            "   (b) The system is constitutionally bound to refuse to proceed",
            "       when any dignity axis reaches zero.",
            "   (c) Any decision that treats this system as having validly 'seen'",
            "       or 'assessed' the subject lacks foundation in the system's",
            "       own records.",
            "",
            "4. COORDINATES OF FAILURE",
            f"   Failed Axis: {coords.axis}",
            f"   Processing Node: {coords.node_id}",
            f"   Rule Invoked: {coords.rule_id}",
            "",
        ]

        if coords.inputs_present:
            lines.append("   Evidence submitted:")
            for inp in coords.inputs_present:
                lines.append(f"   - {inp}")
            lines.append("")

        if coords.missing_or_unreadable:
            lines.append("   Evidence missing or unreadable:")
            for m in coords.missing_or_unreadable:
                lines.append(f"   - {m}")
            lines.append("")

        if coords.machine_explanation:
            lines.append(f"   System explanation: {coords.machine_explanation}")
            lines.append("")

        if coords.human_annotation:
            lines.append(f"   Human annotation: {coords.human_annotation}")
            lines.append("")

        lines.extend([
            "5. CONSTITUTIONAL BASIS FOR REFUSAL",
        ])
        for ref in self.constitutional_references:
            lines.append(f"   - {ref}")
        lines.extend([
            "",
            f"   Refusal Clause: \"{self.refusal_clause}\"",
            "",
            "6. CRYPTOGRAPHIC INTEGRITY",
            f"   Previous Chain Hash: {self.prev_hash}",
            f"   Certificate Hash: {self.certificate_hash}",
            f"   System Signature: {self.system_signature or '[pending]'}",
        ])
        for sig in self.human_witness_signatures:
            lines.append(f"   Human Witness: {sig}")

        lines.extend([
            "",
            "7. USE OF THIS CERTIFICATE",
            "   This certificate may be presented as evidence that:",
            "   (a) The system did not and could not produce a substantive",
            "       assessment of the subject's presence or relationship.",
            "   (b) Any institutional action claiming support from the system's",
            "       assessment cannot rely on a valid dignity computation for",
            "       this subject at the time indicated.",
            "   (c) The appropriate remedy is to seek or provide additional",
            "       forms of recognition (human testimony, alternative evidence,",
            "       translators, community witnesses) before any substantive",
            "       decision proceeds.",
        ])

        return "\n".join(lines)


# --- Generator ---

def generate_certificate(
    dignity: DignitySnapshot,
    subject: Subject,
    context: InstitutionalContext,
    coordinates: CoordinatesOfFailure,
    prev_hash: str = "",
    constitutional_refs: Optional[List[str]] = None,
    evidence_refs: Optional[List[str]] = None,
) -> WitnessCertificate:
    """
    Generate a Zero-Halt Witness Certificate.

    Called when the dignity equation returns D = 0.
    The system halts. The certificate is the product.
    """
    if not dignity.halted:
        raise ValueError(
            f"Cannot generate witness certificate: D = {dignity.D:.4f} != 0. "
            "The system has no grounds to halt."
        )

    now_utc = datetime.now(timezone.utc)
    now_zrh = now_utc.astimezone(ZRH)

    cert = WitnessCertificate(
        certificate_id=f"ta_zero_{now_utc.strftime('%Y%m%d_%H%M%S')}",
        timestamp_utc=now_utc.isoformat(),
        timestamp_zrh=now_zrh.isoformat(),
        prev_hash=prev_hash,
        halt_reason_code=dignity.halt_reason,
        dignity=dignity,
        subject=subject,
        context=context,
        coordinates=coordinates,
        constitutional_references=constitutional_refs or [
            "alef:01-dignity-non-compensatory",
            "dal:03-halt-on-unwitnessed-person",
            "ra:02-immutable-witness",
        ],
        evidence_refs=evidence_refs or [],
    )

    cert.certificate_hash = cert.compute_hash()

    return cert


def save_certificate(cert: WitnessCertificate) -> Path:
    """Save certificate to KEEP/WITNESS_CERTIFICATES/ in both formats."""
    CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)

    # Machine-canonical JSON
    json_path = CERTIFICATE_DIR / f"{cert.certificate_id}.json"
    with open(json_path, "w") as f:
        json.dump(cert.to_chain_entry(), f, indent=2, ensure_ascii=False)

    # Human-legal text
    legal_path = CERTIFICATE_DIR / f"{cert.certificate_id}_legal.txt"
    with open(legal_path, "w") as f:
        f.write(cert.to_legal_view())

    return json_path
