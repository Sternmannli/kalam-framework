#!/usr/bin/env python3
"""
gap004_mediator.py — GAP#004 Conflict Resolution Engine
Version: 2.0

Linked Rules:  (dignity-first),  (right to remedy)

v1.0: Surfaces individual vs collective dignity tension without resolving it.
v2.0: Adds resolution architecture — not to CLOSE the gap, but to give it teeth:
  1. Collective D integration (GAP#004-A metric)
  2. Weakest-voice-first ordering (anti-gaming, P#010)
  3. Witness scale checkpoint (escalate unwitnessed conflicts)
  4. Collective shelter (group-level remedy path)
  5. Network pattern connection (cross-user intelligence)

The gap is still non-resolvable. But now the system can:
  - Measure the tension (Collective D)
  - Prioritize the minority (weakest-voice-first)
  - Track whether anyone has SEEN the conflict (witness scale)
  - Offer remedies to the group, not just individuals (collective shelter)
  - Detect when the same conflict repeats across donors (network)


"""

import re
import uuid
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


# ═══════════════════════════════════════════════════
# SIGNAL PATTERNS (v1.0, unchanged)
# ═══════════════════════════════════════════════════

INDIVIDUAL_SIGNALS = [
    (r'\bone (person|user|user|participant)\b', "Single individual referenced"),
    (r'\bpersonal (data|information|history)\b', "Personal data involved"),
    (r'\bspecific (case|situation|context)\b', "Specific individual context"),
    (r'\bmy (situation|case|experience)\b', "First-person individual claim"),
    (r'\bexception\b', "Exception to general rule requested"),
    (r'\bunique (circumstance|need|case)\b', "Unique individual circumstance"),
    (r'\bprivacy\b', "Privacy concern"),
    (r'\bconsent\b', "Consent question"),
    (r'\bopt[- ](in|out)\b', "Individual choice mechanism"),
    (r'\bremove (me|my)\b', "Request for individual removal"),
]

COLLECTIVE_SIGNALS = [
    (r'\b(all|every|each) (user|user|participant|person)\b', "Collective action affects all"),
    (r'\bgroup\b', "Group referenced"),
    (r'\bcommunity\b', "Community referenced"),
    (r'\bcollective\b', "Collective action"),
    (r'\bmajority\b', "Majority decision"),
    (r'\bpolicy\b', "Policy affecting multiple people"),
    (r'\bstandard\b', "Standard applied to group"),
    (r'\buniform\b', "Uniform treatment"),
    (r'\bfairness\b', "Fairness claim across group"),
    (r'\bequal (treatment|access)\b', "Equal treatment claim"),
    (r'\bcohort\b', "Cohort-level action"),
    (r'\bfor the (good|benefit|sake) of\b', "Collective benefit justification"),
]

DIRECT_TENSION_PATTERNS = [
    r'\b(individual|personal)\b.*\bvs.?\b.*\b(group|collective|community)\b',
    r'\b(exception|special case)\b.*\b(fairness|equal|standard)\b',
    r'\bone person.*affects.*everyone',
    r'\b(privacy|consent)\b.*\b(aggregate|collective|shared)\b',
    r'\b(individual choice|personal preference)\b.*\b(community|group|system)\b',
]


# ═══════════════════════════════════════════════════
# RESOLUTION MODES (v2.0)
# ═══════════════════════════════════════════════════

class ResolutionMode(Enum):
    """
    How the conflict is being held.
    Not "resolved" — held. The gap stays open.
    """
    UNPROCESSED = "unprocessed"           # Detected but not yet assessed
    SURFACE_ONLY = "surface_only"         # v1.0 behavior: ticket generated, administrator notified
    MEASURED = "measured"                 # Collective D computed, tension quantified
    WEAKEST_PRIORITIZED = "weakest_first" # Weakest voice identified and surfaced first
    WITNESSED = "witnessed"               # Administrator has seen the conflict (W-3+)
    SHELTERED = "sheltered"               # Group remedy offered
    HELD = "held"                         # Administrator chose to hold the tension


# ═══════════════════════════════════════════════════
# DATA STRUCTURES (v1.0 + v2.0 additions)
# ═══════════════════════════════════════════════════

@dataclass
class TensionSide:
    label: str
    signals: list
    strength: float


@dataclass
class CollectiveMeasurement:
    """v2.0: Quantified collective dignity measurement."""
    D_collective: float       # From check_collective_dignity
    mean_D: float
    variance: float
    variance_penalty: float
    cohort_size: int
    safety_gate: bool         # True if D_collective < 0.5
    weakest_D: float          # Lowest individual D in cohort
    weakest_index: int        # Index of weakest member


@dataclass
class WeakestVoice:
    """
    v2.0: The weakest voice in the conflict.
    P#010: "The weakest voice goes first."
    Anti-gaming: systems optimize for high-scorers.
    This reverses the optimization direction.
    """
    index: int                # Position in cohort
    D_score: float            # Their dignity score
    failed_components: list   # Which A/L/M components failed
    question: str             # Administrator question focused on this voice


@dataclass
class CollectiveRemedy:
    """
    v2.0: Group-level remedy (extends shelter.py to collectives).
    : Right to remedy applies to groups too.
    """
    remedy_type: str          # "variance_reduction", "weakest_uplift", "policy_review"
    target: str               # "cohort", "weakest_member", "policy"
    description: str
    proportionate: bool       # Is the remedy proportionate to the harm?


@dataclass
class ConflictTicket:
    """Extended conflict ticket with v2.0 resolution architecture."""
    ticket_id: str
    timestamp: str
    severity: str
    direct_tension: bool
    individual: TensionSide
    collective: TensionSide
    questions: list
    input_summary: str
    linked_gap: str = "GAP#004"
    linked_covenant: str = " (DIGNITY FIRST)"
    resolution: str = "NONE — administrator review required"
    status: str = "OPEN"
    # v2.0 fields
    resolution_mode: str = "unprocessed"
    collective_measurement: Optional[CollectiveMeasurement] = None
    weakest_voice: Optional[WeakestVoice] = None
    collective_remedies: List[CollectiveRemedy] = field(default_factory=list)
    witness_level: int = 0    # W-0 through W-5
    mycelium_pattern_id: str = ""  # If linked to cross-user pattern

    def display(self):
        print(f"\n{'='*60}")
        print(f"GAP#004 CONFLICT TICKET — {self.severity}")
        print(f"{'='*60}")
        print(f"Ticket:   {self.ticket_id}")
        print(f"Time:     {self.timestamp}")
        print(f"Gap:      {self.linked_gap}")
        print(f"Mode:     {self.resolution_mode}")
        print(f"Witness:  W-{self.witness_level}")
        print(f"Status:   {self.status}")
        if self.direct_tension:
            print(f"\n  DIRECT TENSION detected")
        print(f"\n  Individual signals ({len(self.individual.signals)}):")
        for s in self.individual.signals:
            print(f"    - {s}")
        print(f"\n  Collective signals ({len(self.collective.signals)}):")
        for s in self.collective.signals:
            print(f"    - {s}")
        if self.collective_measurement:
            cm = self.collective_measurement
            print(f"\n  Collective D: {cm.D_collective:.3f}")
            print(f"  Variance:     {cm.variance:.4f}")
            print(f"  Weakest D:    {cm.weakest_D:.3f} (index {cm.weakest_index})")
            if cm.safety_gate:
                print(f"  SAFETY_GATE TRIGGERED (D_collective < 0.5)")
        if self.weakest_voice:
            wv = self.weakest_voice
            print(f"\n  WEAKEST VOICE (P#010: weakest goes first):")
            print(f"    D={wv.D_score:.3f}, failed: {wv.failed_components}")
            print(f"    Q: {wv.question}")
        if self.collective_remedies:
            print(f"\n  Collective remedies ():")
            for r in self.collective_remedies:
                print(f"    [{r.remedy_type}] {r.description}")
        print(f"\n  Administrator questions (hold the gap, do not close it):")
        for i, q in enumerate(self.questions, 1):
            print(f"    {i}. {q}")
        print(f"\n  Resolution: {self.resolution}")
        print(f"{'='*60}\n")

    def to_dict(self) -> dict:
        d = {
            "ticket_id": self.ticket_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "linked_gap": self.linked_gap,
            "linked_covenant": self.linked_covenant,
            "direct_tension": self.direct_tension,
            "individual_signals": self.individual.signals,
            "collective_signals": self.collective.signals,
            "individual_strength": self.individual.strength,
            "collective_strength": self.collective.strength,
            "steward_questions": self.questions,
            "input_summary": self.input_summary,
            "resolution": self.resolution,
            "resolution_mode": self.resolution_mode,
            "status": self.status,
            "witness_level": self.witness_level,
            "mycelium_pattern_id": self.mycelium_pattern_id,
        }
        if self.collective_measurement:
            cm = self.collective_measurement
            d["collective_D"] = cm.D_collective
            d["collective_variance"] = cm.variance
            d["weakest_D"] = cm.weakest_D
            d["safety_gate"] = cm.safety_gate
        if self.weakest_voice:
            d["weakest_voice_D"] = self.weakest_voice.D_score
            d["weakest_voice_question"] = self.weakest_voice.question
        if self.collective_remedies:
            d["remedies"] = [
                {"type": r.remedy_type, "target": r.target, "description": r.description}
                for r in self.collective_remedies
            ]
        return d


# ═══════════════════════════════════════════════════
# CORE DETECTION (v1.0, preserved)
# ═══════════════════════════════════════════════════

def _generate_questions(individual: TensionSide, collective: TensionSide, direct: bool) -> list:
    questions = [
        "Whose dignity is primary here — and what does that mean for "
        "the person whose dignity is secondary?"
    ]
    if individual.signals:
        questions.append(
            "If the individual's participation is constrained to protect the collective, "
            "what does the individual lose — and is that loss visible in the ledger?"
        )
    else:
        questions.append(
            "No individual signals detected, but collective action implies individual impact. "
            "Who is the specific person most affected by this collective decision?"
        )
    if collective.signals:
        questions.append(
            "If the collective's integrity is constrained to protect the individual, "
            "what does the community lose — and who bears that cost?"
        )
    if direct:
        questions.append(
            "The input contains explicit tension language. "
            "Is this tension already known to both affected parties? "
            "Have they been witnessed?"
        )
    ind_texts = [s for s in individual.signals]
    col_texts = [s for s in collective.signals]
    if any('Privacy' in s or 'consent' in s.lower() for s in ind_texts):
        questions.append(
            "Privacy or consent is involved. Can the individual's data be separated from "
            "the collective action without diminishing either?"
        )
    if any('Majority' in s or 'Policy' in s for s in col_texts):
        questions.append(
            "A majority decision or policy is referenced. What is the opt-out path for the minority? "
            "If there is none, is that a void rule violation?"
        )
    if any('Exception' in s for s in ind_texts) and any('Equal' in s or 'Standard' in s for s in col_texts):
        questions.append(
            "An exception request exists alongside an equal treatment claim. "
            "Is the exception request itself a dignity claim? "
            "Does honouring it undermine the equal treatment claim for others?"
        )
    questions.append(
        "GAP#004 has no resolution path. This ticket is the gap made visible. "
        "What would it mean to hold this tension rather than resolve it?"
    )
    return questions


def _assess_severity(individual: TensionSide, collective: TensionSide, direct: bool) -> str:
    if direct:
        return "HIGH"
    total = len(individual.signals) + len(collective.signals)
    both = individual.signals and collective.signals
    col_only = collective.signals and not individual.signals
    if both and total >= 4:
        return "HIGH"
    elif col_only and len(collective.signals) >= 2:
        # WALKTHROUGH-001 fix: collective signals with ZERO individual signals
        # means the harm is hidden — individuals are invisible precisely because
        # the bias operates at the group level. This is MORE dangerous, not less.
        return "HIGH"
    elif both and total >= 2:
        return "MEDIUM"
    elif col_only:
        return "MEDIUM"
    elif total >= 1:
        return "LOW"
    return "LOW"


def surface_conflict(text: str) -> Optional[ConflictTicket]:
    """v1.0 core: detect individual vs collective tension signals."""
    ind_signals = []
    for pattern, desc in INDIVIDUAL_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            ind_signals.append(desc)
    col_signals = []
    for pattern, desc in COLLECTIVE_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            col_signals.append(desc)
    direct = any(re.search(p, text, re.IGNORECASE) for p in DIRECT_TENSION_PATTERNS)

    # Enhanced detection: if collective signals and universal language, trigger
    if not direct and not (ind_signals and col_signals):
        if col_signals and re.search(r'\b(all|every|each)\b', text, re.IGNORECASE):
            pass  # allow to continue
        else:
            return None

    ind = TensionSide("individual", ind_signals, min(1.0, len(ind_signals)/5))
    col = TensionSide("collective", col_signals, min(1.0, len(col_signals)/5))
    severity = _assess_severity(ind, col, direct)
    questions = _generate_questions(ind, col, direct)
    return ConflictTicket(
        ticket_id=f"GAP004-{str(uuid.uuid4())[:8].upper()}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        severity=severity,
        direct_tension=direct,
        individual=ind,
        collective=col,
        questions=questions,
        input_summary=text[:80].replace('\n', ' '),
        resolution_mode=ResolutionMode.SURFACE_ONLY.value,
    )


# ═══════════════════════════════════════════════════
# v2.0: CONFLICT RESOLUTION ENGINE
# ═══════════════════════════════════════════════════

class ConflictEngine:
    """
    Gives GAP#004 teeth without closing the gap.

    The engine takes a ConflictTicket and enriches it with:
    1. Collective D measurement (how bad is the inequality?)
    2. Weakest voice identification (who is most harmed?)
    3. Collective remedies (what can be offered to the group?)
    4. Witness tracking (has anyone SEEN this conflict?)

    The gap remains open. The engine makes it visible, measurable,
    and actionable — but never resolved. Resolution is the administrator's.
    """

    def __init__(self):
        self._tickets: List[ConflictTicket] = []
        self._witnessed: dict = {}  # ticket_id → witness_level

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ── 1. MEASURE: Collective D ──

    def measure(
        self,
        ticket: ConflictTicket,
        individual_scores: List[float],
    ) -> ConflictTicket:
        """
        Enrich ticket with collective dignity measurement.
        Uses GAP#004-A formula: D_collective = mean(D_i) × (1 - variance_penalty)
        """
        if not individual_scores:
            return ticket

        n = len(individual_scores)
        mean_d = sum(individual_scores) / n
        variance = sum((s - mean_d) ** 2 for s in individual_scores) / n
        variance_penalty = min(1.0, variance * 4)
        d_collective = mean_d * (1 - variance_penalty)

        weakest_d = min(individual_scores)
        weakest_idx = individual_scores.index(weakest_d)

        ticket.collective_measurement = CollectiveMeasurement(
            D_collective=round(d_collective, 4),
            mean_D=round(mean_d, 4),
            variance=round(variance, 4),
            variance_penalty=round(variance_penalty, 4),
            cohort_size=n,
            safety_gate=d_collective < 0.5,
            weakest_D=round(weakest_d, 4),
            weakest_index=weakest_idx,
        )
        ticket.resolution_mode = ResolutionMode.MEASURED.value

        # If safety gate triggers, escalate severity
        if d_collective < 0.5:
            ticket.severity = "HIGH"

        return ticket

    # ── 2. WEAKEST VOICE FIRST (P#010) ──

    def prioritize_weakest(
        self,
        ticket: ConflictTicket,
        individual_scores: Optional[List[float]] = None,
        failed_components: Optional[List[List[str]]] = None,
    ) -> ConflictTicket:
        """
        Identify and surface the weakest voice first.

        P#010: "The weakest voice goes first."
        Systems optimize for high-scorers. This reverses the direction.
        The person most affected by the collective decision speaks first.
        """
        if not individual_scores:
            # No cohort data — use signal analysis
            if not ticket.individual.signals and ticket.collective.signals:
                ticket.weakest_voice = WeakestVoice(
                    index=-1,
                    D_score=0.0,
                    failed_components=["invisible"],
                    question=(
                        "No individual voice detected. The weakest voice is the one "
                        "not speaking. Who is silenced by this collective action?"
                    ),
                )
            ticket.resolution_mode = ResolutionMode.WEAKEST_PRIORITIZED.value
            return ticket

        weakest_d = min(individual_scores)
        weakest_idx = individual_scores.index(weakest_d)
        components = (
            failed_components[weakest_idx]
            if failed_components and weakest_idx < len(failed_components)
            else []
        )

        ticket.weakest_voice = WeakestVoice(
            index=weakest_idx,
            D_score=round(weakest_d, 4),
            failed_components=components,
            question=(
                f"Member {weakest_idx} has the lowest dignity score ({weakest_d:.3f}). "
                f"What would this decision look like from their position? "
                f"Can the collective action proceed without further harming them?"
            ),
        )

        # Insert weakest-voice question at position 0 (before all other questions)
        ticket.questions.insert(0, ticket.weakest_voice.question)
        ticket.resolution_mode = ResolutionMode.WEAKEST_PRIORITIZED.value
        return ticket

    # ── 3. COLLECTIVE SHELTER ( for groups) ──

    def generate_remedies(self, ticket: ConflictTicket) -> ConflictTicket:
        """
        Generate group-level remedies.
        : Right to remedy applies to groups too.
        """
        remedies = []
        cm = ticket.collective_measurement

        if cm and cm.variance > 0.1:
            remedies.append(CollectiveRemedy(
                remedy_type="variance_reduction",
                target="cohort",
                description=(
                    f"Dignity variance is {cm.variance:.4f}. "
                    f"Review why treatment differs across cohort members. "
                    f"Reduce variance before proceeding."
                ),
                proportionate=True,
            ))

        if cm and cm.weakest_D < 0.3:
            remedies.append(CollectiveRemedy(
                remedy_type="weakest_uplift",
                target="weakest_member",
                description=(
                    f"Weakest member D={cm.weakest_D:.3f} is critically low. "
                    f"Individual shelter recommended before group decision proceeds."
                ),
                proportionate=True,
            ))

        if cm and cm.safety_gate:
            remedies.append(CollectiveRemedy(
                remedy_type="policy_review",
                target="policy",
                description=(
                    f"Collective D={cm.D_collective:.3f} below threshold (0.5). "
                    f"Sealed gate triggered. The collective action must be suspended "
                    f"until dignity is restored across the cohort."
                ),
                proportionate=True,
            ))

        if ticket.direct_tension and not cm:
            remedies.append(CollectiveRemedy(
                remedy_type="tension_acknowledgement",
                target="cohort",
                description=(
                    "Direct tension detected between individual and collective dignity. "
                    "Both parties should be informed that the tension is held — "
                    "not resolved — and that neither side's claim is dismissed."
                ),
                proportionate=True,
            ))

        ticket.collective_remedies = remedies
        if remedies:
            ticket.resolution_mode = ResolutionMode.SHELTERED.value
        return ticket

    # ── 4. WITNESS CHECKPOINT ──

    def witness(self, ticket: ConflictTicket, level: int = 0) -> ConflictTicket:
        """
        Set witness level for the conflict.
        W-0: UNSEEN, W-1: PASSED, W-2: FLAGGED, W-3: SEEN (irreversible)
        """
        current = self._witnessed.get(ticket.ticket_id, 0)
        # W-3+ is irreversible — can only go up
        new_level = max(current, level)
        self._witnessed[ticket.ticket_id] = new_level
        ticket.witness_level = new_level
        if new_level >= 3:
            ticket.resolution_mode = ResolutionMode.WITNESSED.value
        return ticket

    def steward_sees(self, ticket: ConflictTicket) -> ConflictTicket:
        """Mark conflict as seen by administrator (W-3, irreversible)."""
        return self.witness(ticket, level=3)

    def steward_holds(self, ticket: ConflictTicket) -> ConflictTicket:
        """Mark conflict as actively held by administrator (W-4)."""
        ticket = self.witness(ticket, level=4)
        ticket.resolution_mode = ResolutionMode.HELD.value
        ticket.resolution = "HELD — administrator chose to hold the tension"
        return ticket

    # ── 5. FULL PIPELINE ──

    def process(
        self,
        text: str,
        individual_scores: Optional[List[float]] = None,
        failed_components: Optional[List[List[str]]] = None,
    ) -> Optional[ConflictTicket]:
        """
        Full pipeline: detect → measure → prioritize → remedy.

        This is the v2.0 entry point. It runs the complete
        resolution engine on a text input.
        """
        ticket = surface_conflict(text)
        if ticket is None:
            return None

        if individual_scores:
            ticket = self.measure(ticket, individual_scores)
            ticket = self.prioritize_weakest(ticket, individual_scores, failed_components)
        else:
            ticket = self.prioritize_weakest(ticket)

        ticket = self.generate_remedies(ticket)
        # Start at W-2 (FLAGGED) — detection counts as flagging
        ticket = self.witness(ticket, level=2)

        self._tickets.append(ticket)
        return ticket

    # ── STATE ──

    @property
    def tickets_count(self) -> int:
        return len(self._tickets)

    @property
    def open_tickets(self) -> List[ConflictTicket]:
        return [t for t in self._tickets if t.status == "OPEN"]

    @property
    def unwitnessed_tickets(self) -> List[ConflictTicket]:
        """Tickets below W-3 — administrator hasn't seen them yet."""
        return [t for t in self._tickets if t.witness_level < 3]

    @property
    def last_ticket(self) -> Optional[ConflictTicket]:
        return self._tickets[-1] if self._tickets else None


# ═══════════════════════════════════════════════════
# STANDALONE (v1.0 compatibility)
# ═══════════════════════════════════════════════════

def check_and_surface(text: str) -> dict:
    from tools.dignity_check import check_dignity
    dignity = check_dignity(text)
    conflict = surface_conflict(text)
    return {
        "dignity_passed": dignity.passed,
        "D_score": dignity.D,
        "dignity_audit": dignity.audit_object() if not dignity.passed else None,
        "gap004_detected": conflict is not None,
        "gap004_ticket": conflict.to_dict() if conflict else None
    }


def main():
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python3 gap004_mediator.py \"decision or event text\"")
        return
    output_json = '--json' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print("No text provided.")
        return
    text = args[0]
    engine = ConflictEngine()
    ticket = engine.process(text)
    if ticket is None:
        print("No individual/collective dignity tension detected.")
        return
    if output_json:
        print(json.dumps(ticket.to_dict(), indent=2))
    else:
        ticket.display()


if __name__ == "__main__":
    main()
