#!/usr/bin/env python3
"""
letter_ontology.py — Arabic Letter Ontology for kalam Chain Architecture

The 28 Arabic letters as a functional taxonomy for chain entries.
Not metaphor. Not decoration. A typed algebra over an append-only chain.

Properties implemented (ranked by multi-model consensus, EXP-002):
  1. Connection rules (join/non-join) — UNANIMOUS 6/6
  2. Positional transformation (initial/medial/final/isolated) — UNANIMOUS 6/6
  3. Phonetic origin (somatic grounding) — 5/6
  4. Numerical value (Abjad ordering) — 4/6
  5. Elemental correspondence — narrative only

First three letters formalized (Alef, Ba, Ta) as load-bearing architecture.
Remaining 25 letters: taxonomy defined, enforcement pending.

"The sword is not sharpened by striking water, but by refusing to cut the air."


"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Set


# --- Positional Forms ---

class PositionalForm(Enum):
    """The four shapes a letter takes depending on its position."""
    ISOLATED = "isolated"   # Mufrad — stands alone, non-composable
    INITIAL = "initial"     # Starts a sequence
    MEDIAL = "medial"       # Bridges within a sequence
    FINAL = "final"         # Terminates a sequence


# --- Somatic Origin ---

class SomaticOrigin(Enum):
    """Where in the body the letter is produced."""
    THROAT = "throat"       # Deep infrastructure, identity, kernel
    TONGUE = "tongue"       # Reasoning, transformation, logic
    LIPS = "lips"           # Interface, expression, output
    TEETH = "teeth"         # Boundaries, constraints, validation


# --- Letter Definition ---

@dataclass(frozen=True)
class Letter:
    """A single Arabic letter with all architecturally relevant properties."""
    name: str               # English transliteration
    arabic: str             # Arabic glyph
    abjad_value: int        # Numerical weight (ordering, not meaning)
    connects_forward: bool  # Can join to the next letter/entry
    somatic_origin: SomaticOrigin
    allowed_forms: Set[PositionalForm]
    system_role: str        # Architectural function
    description: str        # One-line purpose


# --- The First Three Letters (Formalized by Multi-Model Consensus) ---

ALEF = Letter(
    name="alef",
    arabic="ا",
    abjad_value=1,
    connects_forward=False,  # NON-CONNECTOR: constitutional circuit breaker
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.ISOLATED},  # Always isolated, never in sequence
    system_role="sovereignty",
    description="Constitutional invariant. Write-once. Referenced by all, modified by none.",
)

BA = Letter(
    name="ba",
    arabic="ب",
    abjad_value=2,
    connects_forward=True,   # CONNECTOR: flow, intake, processing
    somatic_origin=SomaticOrigin.LIPS,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="gateway",
    description="Flow control. Intake, processing, commitment. Shape changes with position.",
)

TA = Letter(
    name="ta",
    arabic="ت",
    abjad_value=400,
    connects_forward=True,   # CONNECTOR during collection; becomes NON-CONNECTOR on halt
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={
        PositionalForm.INITIAL,   # Bind witnesses
        PositionalForm.MEDIAL,    # Collect attestations, compute dignity
        PositionalForm.FINAL,     # Commit testimony (dignity valid)
        PositionalForm.ISOLATED,  # HALT: Ta_mufrad (dignity invalid, D=0)
    },
    system_role="testimony",
    description="Witness attestation and halt instrument. Terminal transformation on D=0.",
)


# --- Non-Connector Letters (Sovereignty Layer) ---
# These letters refuse to join forward. They are constitutional circuit breakers.

DAL = Letter(
    name="dal",
    arabic="د",
    abjad_value=4,
    connects_forward=False,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.ISOLATED},
    system_role="boundary",
    description="The boundary. Where the system ends and the human begins.",
)

DHAL = Letter(
    name="dhal",
    arabic="ذ",
    abjad_value=700,
    connects_forward=False,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.ISOLATED},
    system_role="distinction",
    description="The distinction. Marks qualitative difference between elements.",
)

RA = Letter(
    name="ra",
    arabic="ر",
    abjad_value=200,
    connects_forward=False,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.ISOLATED},
    system_role="witness",
    description="The witness. Records without interfering. Immutable observation.",
)

ZAY = Letter(
    name="zay",
    arabic="ز",
    abjad_value=7,
    connects_forward=False,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.ISOLATED},
    system_role="precision",
    description="Precision marker. Exact measurement, no approximation.",
)

WAW = Letter(
    name="waw",
    arabic="و",
    abjad_value=6,
    connects_forward=False,
    somatic_origin=SomaticOrigin.LIPS,
    allowed_forms={PositionalForm.ISOLATED},
    system_role="conjunction",
    description="The conjunction. Marks parallel existence without merging.",
)


# --- Connector Letters (Remaining, taxonomy defined) ---

JIM = Letter(
    name="jim",
    arabic="ج",
    abjad_value=3,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="gathering",
    description="Gathering. Collects related elements into coherent groups.",
)

HA_SMALL = Letter(
    name="ha_small",
    arabic="ح",
    abjad_value=8,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="containment",
    description="Containment. Holds without compressing. Safe enclosure.",
)

KHA = Letter(
    name="kha",
    arabic="خ",
    abjad_value=600,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="selection",
    description="Selection. Chooses one path from many. Routing.",
)

SIN = Letter(
    name="sin",
    arabic="س",
    abjad_value=60,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="flow",
    description="Smooth flow. Continuous processing without interruption.",
)

SHIN = Letter(
    name="shin",
    arabic="ش",
    abjad_value=300,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="branching",
    description="Branching. Splits flow into parallel paths.",
)

SAD = Letter(
    name="sad",
    arabic="ص",
    abjad_value=90,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="truth",
    description="Truth assertion. Marks verified, canonical content.",
)

DAD = Letter(
    name="dad",
    arabic="ض",
    abjad_value=800,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="uniqueness",
    description="Uniqueness. The letter unique to Arabic. Marks irreducible identity.",
)

TAA = Letter(
    name="taa",
    arabic="ط",
    abjad_value=9,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="weight",
    description="Weight. Marks entries with gravitational significance.",
)

DHAA = Letter(
    name="dhaa",
    arabic="ظ",
    abjad_value=900,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="visibility",
    description="Visibility. Makes the hidden apparent. Surfaces what is buried.",
)

AIN = Letter(
    name="ain",
    arabic="ع",
    abjad_value=70,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="depth",
    description="Depth. Deep knowledge, lived experience, the well.",
)

GHAIN = Letter(
    name="ghain",
    arabic="غ",
    abjad_value=1000,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="absence",
    description="Absence. Marks what is missing. The gap as signal.",
)

FA = Letter(
    name="fa",
    arabic="ف",
    abjad_value=80,
    connects_forward=True,
    somatic_origin=SomaticOrigin.LIPS,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="opening",
    description="Opening. First disclosure. The crack in the sealed door.",
)

QAF = Letter(
    name="qaf",
    arabic="ق",
    abjad_value=100,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="anchor",
    description="Anchor. Fixes a point that does not drift.",
)

KAF = Letter(
    name="kaf",
    arabic="ك",
    abjad_value=20,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="likeness",
    description="Likeness. Pattern matching. Recognizes similarity across contexts.",
)

LAM = Letter(
    name="lam",
    arabic="ل",
    abjad_value=30,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="binding",
    description="Binding. Creates obligation between elements. The rule connector.",
)

MIM = Letter(
    name="mim",
    arabic="م",
    abjad_value=40,
    connects_forward=True,
    somatic_origin=SomaticOrigin.LIPS,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="memory",
    description="Memory. Initiation, connection, and sealing of the chain.",
)

NUN = Letter(
    name="nun",
    arabic="ن",
    abjad_value=50,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="self",
    description="Self. The soul of the entry. Identity at the deepest register.",
)

HA_BIG = Letter(
    name="ha_big",
    arabic="ه",
    abjad_value=5,
    connects_forward=True,
    somatic_origin=SomaticOrigin.THROAT,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="breath",
    description="Breath. The pause. The system's respiratory cycle.",
)

YA = Letter(
    name="ya",
    arabic="ي",
    abjad_value=10,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TONGUE,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="hand",
    description="Hand. Agency. The reaching out. The giving.",
)

THA = Letter(
    name="tha",
    arabic="ث",
    abjad_value=500,
    connects_forward=True,
    somatic_origin=SomaticOrigin.TEETH,
    allowed_forms={PositionalForm.INITIAL, PositionalForm.MEDIAL, PositionalForm.FINAL},
    system_role="persistence",
    description="Persistence. That which endures through repetition.",
)


# --- Registry ---

ALL_LETTERS: Dict[str, Letter] = {
    letter.name: letter for letter in [
        ALEF, BA, TA, THA, JIM, HA_SMALL, KHA, DAL, DHAL, RA, ZAY,
        SIN, SHIN, SAD, DAD, TAA, DHAA, AIN, GHAIN, FA, QAF, KAF,
        LAM, MIM, NUN, HA_BIG, WAW, YA,
    ]
}

NON_CONNECTORS: Set[str] = {
    name for name, letter in ALL_LETTERS.items() if not letter.connects_forward
}

CONNECTORS: Set[str] = {
    name for name, letter in ALL_LETTERS.items() if letter.connects_forward
}


# --- Somatic Layers ---

def letters_by_origin(origin: SomaticOrigin) -> List[Letter]:
    """Return all letters from a given somatic origin (body layer)."""
    return [l for l in ALL_LETTERS.values() if l.somatic_origin == origin]


THROAT_LAYER = letters_by_origin(SomaticOrigin.THROAT)   # Core/identity/kernel
TONGUE_LAYER = letters_by_origin(SomaticOrigin.TONGUE)   # Reasoning/transformation
LIPS_LAYER = letters_by_origin(SomaticOrigin.LIPS)       # Interface/expression
TEETH_LAYER = letters_by_origin(SomaticOrigin.TEETH)     # Boundaries/constraints


# --- Connection Validation ---

def can_join(entry_letter: str, next_letter: str) -> bool:
    """
    Check if an entry tagged with entry_letter can join forward
    to an entry tagged with next_letter.

    Non-connectors terminate chains. After a non-connector,
    a new chain segment must be explicitly initiated.
    """
    letter = ALL_LETTERS.get(entry_letter)
    if letter is None:
        return False
    return letter.connects_forward


def validate_positional_form(letter_name: str, form: PositionalForm) -> bool:
    """Check if a letter is allowed in the given positional form."""
    letter = ALL_LETTERS.get(letter_name)
    if letter is None:
        return False
    return form in letter.allowed_forms


def is_halt_capable(letter_name: str) -> bool:
    """Check if a letter can undergo terminal transformation to isolated."""
    letter = ALL_LETTERS.get(letter_name)
    if letter is None:
        return False
    # A letter is halt-capable if it normally connects but can also be isolated
    return (
        letter.connects_forward
        and PositionalForm.ISOLATED in letter.allowed_forms
    )


# --- Summary ---

def ontology_summary() -> str:
    """Return a human-readable summary of the letter ontology."""
    lines = [
        "kalam Letter Ontology v1.0",
        f"Total letters: {len(ALL_LETTERS)}",
        f"Non-connectors (circuit breakers): {len(NON_CONNECTORS)} — {', '.join(sorted(NON_CONNECTORS))}",
        f"Connectors: {len(CONNECTORS)}",
        f"Halt-capable (terminal transformation): {sum(1 for n in ALL_LETTERS if is_halt_capable(n))}",
        "",
        "Somatic layers:",
        f"  Throat (kernel):     {len(THROAT_LAYER)} letters",
        f"  Tongue (reasoning):  {len(TONGUE_LAYER)} letters",
        f"  Lips (interface):    {len(LIPS_LAYER)} letters",
        f"  Teeth (constraint):  {len(TEETH_LAYER)} letters",
    ]
    return "\n".join(lines)
