#!/usr/bin/env python3
"""
chain_validator.py — Connection Rules Validator for kalam Chain

Enforces the Arabic letter connection rules as chain composition constraints.
Not metaphor. Deterministic validation.

Rules (formalized by multi-model consensus, EXP-002):

  ALEF (Non-Connector / Sovereignty):
    A.1 — Write-once. Reject modification unless supersession with quorum.
    A.2 — Accepts inbound references only. No outbound joins.
    A.3 — Always isolated. No positional variants.

  BA (Connector / Gateway):
    B.1 — Joins forward to any letter. Cannot modify Alef payloads.
    B.2 — Ba_i must emit session_id. Ba_m must reference session_id.
         Ba_f must provide commit_hash.
    B.3 — Ba_i cannot follow a non-connector without explicit re-initiation.
    B.4 — Ba_f + non-connector = sealed envelope (hard boundary).

  TA (Connector with Halt / Testimony):
    T.1 — Connects during collection (Ta_i, Ta_m). Becomes non-connector
         (Ta_mufrad) on D=0.
    T.2 — Ta_mufrad accepts no forward joins. Terminal.
    T.3 — Ta_mufrad requires dual signatures (system + human witness).
    T.4 — Ta_mufrad generates two views: chain JSON + legal document.


"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from tools.letter_ontology import (
    ALL_LETTERS, NON_CONNECTORS, PositionalForm,
    validate_positional_form, can_join, is_halt_capable,
)
from tools.witness_certificate import (
    DignitySnapshot, generate_certificate,
    Subject, InstitutionalContext, CoordinatesOfFailure,
)


class ValidationError(Exception):
    """Raised when a chain entry violates connection rules."""
    pass


class EntryType(Enum):
    STANDARD = "standard"
    SUPERSESSION = "supersession"
    HALT = "halt"


@dataclass
class ChainEntry:
    """A single entry on the append-only chain, tagged with a letter."""
    entry_id: str
    letter: str                    # Letter name from ontology
    positional_form: PositionalForm
    entry_type: EntryType = EntryType.STANDARD
    session_id: str = ""
    commit_hash: str = ""
    prev_entry_id: str = ""
    prev_hash: str = ""
    payload: dict = None
    has_quorum: bool = False       # For supersession of Alef entries
    system_signature: str = ""
    human_witness_signatures: list = None
    dignity_snapshot: Optional[DignitySnapshot] = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
        if self.human_witness_signatures is None:
            self.human_witness_signatures = []


def validate_entry(
    entry: ChainEntry,
    chain_state: Dict,
    prev_entry: Optional[ChainEntry] = None,
) -> List[str]:
    """
    Validate a new chain entry against the letter connection rules.

    Returns empty list if valid. Returns list of violation descriptions if invalid.

    chain_state should contain:
      - "alef_ids": set of existing Alef entry IDs
      - "open_sessions": set of active session IDs
      - "halt_threshold": float (constitutional value, e.g. 0.0001)
    """
    violations = []

    # --- Basic: letter must exist in ontology ---
    letter_def = ALL_LETTERS.get(entry.letter)
    if letter_def is None:
        violations.append(f"Unknown letter: {entry.letter}")
        return violations

    # --- Basic: positional form must be allowed for this letter ---
    if not validate_positional_form(entry.letter, entry.positional_form):
        violations.append(
            f"Letter '{entry.letter}' does not allow form '{entry.positional_form.value}'. "
            f"Allowed: {[f.value for f in letter_def.allowed_forms]}"
        )

    # === ALEF RULES ===
    if entry.letter == "alef":
        # A.1 — Write-once
        alef_ids = chain_state.get("alef_ids", set())
        if entry.entry_id in alef_ids and entry.entry_type != EntryType.SUPERSESSION:
            violations.append("A.1 — Alef is write-once. Cannot modify without supersession.")

        # A.1 — Supersession requires quorum
        if entry.entry_type == EntryType.SUPERSESSION and not entry.has_quorum:
            violations.append("A.1 — Alef supersession requires constitutional quorum.")

        # A.3 — Must be isolated
        if entry.positional_form != PositionalForm.ISOLATED:
            violations.append("A.3 — Alef must always be isolated (Mufrad).")

    # === BA RULES ===
    if entry.letter == "ba":
        # B.2 — Initial must emit session_id
        if entry.positional_form == PositionalForm.INITIAL:
            if not entry.session_id:
                violations.append("B.2 — Ba_i must emit a session_id.")

        # B.2 — Medial must reference session_id
        if entry.positional_form == PositionalForm.MEDIAL:
            if not entry.session_id:
                violations.append("B.2 — Ba_m must reference a valid session_id.")
            open_sessions = chain_state.get("open_sessions", set())
            if entry.session_id and entry.session_id not in open_sessions:
                violations.append(
                    f"B.2 — Ba_m references session '{entry.session_id}' "
                    "which is not in open_sessions."
                )

        # B.2 — Final must provide commit_hash
        if entry.positional_form == PositionalForm.FINAL:
            if not entry.commit_hash:
                violations.append("B.2 — Ba_f must provide a commit_hash.")

        # B.3 — Cannot follow a non-connector without re-initiation
        if prev_entry and prev_entry.letter in NON_CONNECTORS:
            if entry.positional_form != PositionalForm.INITIAL:
                violations.append(
                    "B.3 — After a non-connector, Ba must be Initial "
                    "(explicit re-initiation required)."
                )

    # === TA RULES ===
    if entry.letter == "ta":
        # T.1 — Isolated form = halt
        if entry.positional_form == PositionalForm.ISOLATED:
            # Must have dignity snapshot showing D=0
            if entry.dignity_snapshot is None:
                violations.append("T.1 — Ta_mufrad requires a dignity_snapshot.")
            elif not entry.dignity_snapshot.halted:
                violations.append(
                    f"T.1 — Ta_mufrad requires D=0 but got "
                    f"D={entry.dignity_snapshot.D:.4f}."
                )

            # T.3 — Dual signatures required
            if not entry.system_signature:
                violations.append("T.3 — Ta_mufrad requires system signature.")
            if not entry.human_witness_signatures:
                violations.append(
                    "T.3 — Ta_mufrad requires at least one human witness signature."
                )

    # === GENERAL CONNECTION RULES ===
    # After a non-connector, only Initial forms may follow
    if prev_entry and prev_entry.letter in NON_CONNECTORS:
        if entry.positional_form not in (PositionalForm.INITIAL, PositionalForm.ISOLATED):
            violations.append(
                f"Connection rule — Previous entry '{prev_entry.letter}' is a "
                "non-connector. Next entry must be Initial or Isolated "
                "(new chain segment)."
            )

    # A halted entry (Ta_mufrad) cannot be followed
    if prev_entry and prev_entry.entry_type == EntryType.HALT:
        violations.append(
            "T.2 — Ta_mufrad (halted) accepts no forward joins. "
            "Chain segment is terminal. Start a new segment."
        )

    return violations


def validate_and_append(
    entry: ChainEntry,
    chain: List[ChainEntry],
    chain_state: Dict,
) -> ChainEntry:
    """
    Validate a new entry and append it to the chain if valid.
    Raises ValidationError if any connection rule is violated.
    """
    prev_entry = chain[-1] if chain else None
    violations = validate_entry(entry, chain_state, prev_entry)

    if violations:
        raise ValidationError(
            f"Entry '{entry.entry_id}' violates {len(violations)} rule(s):\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    # Update chain state
    if entry.letter == "alef":
        chain_state.setdefault("alef_ids", set()).add(entry.entry_id)

    if entry.letter == "ba" and entry.positional_form == PositionalForm.INITIAL:
        chain_state.setdefault("open_sessions", set()).add(entry.session_id)

    if entry.letter == "ba" and entry.positional_form == PositionalForm.FINAL:
        chain_state.get("open_sessions", set()).discard(entry.session_id)

    if entry.positional_form == PositionalForm.ISOLATED and entry.letter == "ta":
        entry.entry_type = EntryType.HALT

    chain.append(entry)
    return entry
