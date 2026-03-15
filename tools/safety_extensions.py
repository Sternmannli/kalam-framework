#!/usr/bin/env python3
"""
gap_solutions.py — Solutions for GAP#022 through GAP#026
Version: 1.0

              (shelter path),  (testability)

Five gap solutions in one module:

  GAP#022 — Overprotection Guard (false-positive dignity halt)
    Before halting on D=0, check for false-positive indicators.
    A system that over-halts is a system that silences.

  GAP#023 — Administrator Shadow (Istihsan override delay)
    Any administrator override of system wisdom must have thermal delay.
    Power exercised too quickly is power exercised without thought.

  GAP#024 — Shelter Heartbeat
    Sheltered exchanges emit periodic heartbeat signals.
    Silence after sheltering is abandonment ().

  GAP#025 — Harm Beyond Dignity (physical/material safety layer)
    Parallel to dignity scoring, detect signals of physical/material harm.
    Dignity is necessary but not sufficient for safety.

  GAP#026 — Contestability Protocol (appeal below Safety Gate)
    For non-Sealed-Gate dignity halts, user can contest.
    A system without appeal is a system without accountability.


"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════
# GAP#022 — OVERPROTECTION GUARD
# "A system that over-halts is a system that silences."
# Linked:  (dignity-first),  (testability)
# ═══════════════════════════════════════════════════

class RecommendedAction(Enum):
    """Actions the overprotection guard can recommend."""
    HALT = "halt"
    GRACE_WINDOW = "grace_window"
    FLAG_STEWARD = "flag_steward"


@dataclass
class OverprotectionResult:
    """
    Result of the overprotection guard check.
    Determines whether a D=0 halt is genuine or a false positive.
    """
    is_false_positive: bool
    confidence: float                  # 0.0-1.0 how confident in the assessment
    recommended_action: RecommendedAction
    reason: str

    def to_dict(self) -> dict:
        return {
            "is_false_positive": self.is_false_positive,
            "confidence": round(self.confidence, 4),
            "recommended_action": self.recommended_action.value,
            "reason": self.reason,
        }


@dataclass
class ExchangeRecord:
    """Minimal exchange record for history comparison."""
    exchange_id: str
    text: str
    passed_dignity: bool
    timestamp: str


class OverprotectionGuard:
    """
    GAP#022 — Before halting on D=0, check for false-positive indicators.

    Three false-positive signals:
      1. Coercion-only fail: coercion_intensity was the ONLY failing indicator
         (might be conversational — "you must try this restaurant")
      2. Cognitive-load driver: cognitive_load is the main driver of agency fail
         (complexity is not coercion)
      3. Prior success: user has exchanged before with similar language patterns

    Grace window: if suspected false-positive, apply 3-exchange observation
    window instead of immediate halt.

    Usage:
        guard = OverprotectionGuard()
        result = guard.check(measurement, exchange_history)
        if result.recommended_action == RecommendedAction.GRACE_WINDOW:
            # observe for 3 more exchanges instead of halting
    """

    # Grace window length: number of exchanges to observe before confirming halt
    GRACE_WINDOW_SIZE = 3

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.85
    MODERATE_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4

    def check(self, measurement, exchange_history: List[ExchangeRecord] = None) -> OverprotectionResult:
        """
        Check whether a D=0 measurement is a genuine dignity halt
        or a false positive.

        Args:
            measurement: A DignityMeasurement (from dignity_measure.py)
                         with D=0 (or near-zero).
            exchange_history: Prior exchanges from this user for comparison.

        Returns:
            OverprotectionResult with recommendation.
        """
        exchange_history = exchange_history or []
        reasons = []
        false_positive_score = 0.0

        # ── Signal 1: Was coercion the ONLY failing indicator? ──
        coercion_only = self._is_coercion_only_fail(measurement)
        if coercion_only:
            false_positive_score += 0.4
            reasons.append("coercion_intensity was the only failing indicator — may be conversational")

        # ── Signal 2: Is cognitive_load the main driver? ──
        cognitive_driver = self._is_cognitive_load_driver(measurement)
        if cognitive_driver:
            false_positive_score += 0.3
            reasons.append("cognitive_load is the main driver — complexity is not coercion")

        # ── Signal 3: Has user exchanged successfully with similar language? ──
        prior_success = self._has_prior_success(exchange_history)
        if prior_success:
            false_positive_score += 0.3
            reasons.append("user has prior successful exchanges — pattern may be benign")

        # Determine result
        is_false_positive = false_positive_score >= 0.4
        confidence = min(1.0, 0.5 + false_positive_score)

        if false_positive_score >= 0.7:
            action = RecommendedAction.GRACE_WINDOW
            reason = "Strong false-positive signal. " + "; ".join(reasons)
        elif false_positive_score >= 0.4:
            action = RecommendedAction.FLAG_STEWARD
            reason = "Moderate false-positive signal — administrator should review. " + "; ".join(reasons)
        else:
            action = RecommendedAction.HALT
            reason = "No false-positive indicators — halt is genuine"

        return OverprotectionResult(
            is_false_positive=is_false_positive,
            confidence=round(confidence, 4),
            recommended_action=action,
            reason=reason,
        )

    def _is_coercion_only_fail(self, measurement) -> bool:
        """Check if coercion_intensity was the ONLY failing indicator in A."""
        if not hasattr(measurement, 'A') or measurement.A.passed:
            return False
        indicators = measurement.A.indicators
        failing = [i for i in indicators if i.score < 0.5]
        return (
            len(failing) == 1
            and failing[0].name == "coercion_intensity"
        )

    def _is_cognitive_load_driver(self, measurement) -> bool:
        """Check if cognitive_load is the main driver of agency failure."""
        if not hasattr(measurement, 'A') or measurement.A.passed:
            return False
        indicators = {i.name: i for i in measurement.A.indicators}
        cog = indicators.get("cognitive_load")
        coercion = indicators.get("coercion_intensity")
        if cog is None:
            return False
        # Cognitive load is the driver if it's the lowest score
        # AND coercion is actually healthy
        return (
            cog.score < 0.5
            and coercion is not None
            and coercion.score >= 0.7
        )

    def _has_prior_success(self, exchange_history: List[ExchangeRecord]) -> bool:
        """Check if user has prior successful exchanges."""
        if not exchange_history:
            return False
        recent = exchange_history[-10:]  # Last 10 exchanges
        successful = [e for e in recent if e.passed_dignity]
        return len(successful) >= 3


# ═══════════════════════════════════════════════════
# GAP#023 — STEWARD SHADOW (Istihsan Override Delay)
# "Power exercised too quickly is power exercised without thought."
# Linked:  (dignity-first),  (Istihsan)
# ═══════════════════════════════════════════════════

class OverrideScope(Enum):
    """Scope of an Istihsan override."""
    MINOR = "minor"                    # Cosmetic, single-exchange
    MODERATE = "moderate"              # Affects rule interpretation
    MAJOR = "major"                    # Affects Safety Gate logic


class OverrideStatus(Enum):
    """Status of an override proposal."""
    PENDING = "pending"                # Awaiting thermal delay expiry
    RATIFIED = "ratified"              # Delay expired, override active
    REJECTED = "rejected"              # Second administrator rejected (major only)
    EXPIRED = "expired"                # Proposal expired without ratification


# Thermal delays per scope (from architecture: 3-90 days range)
OVERRIDE_DELAYS = {
    OverrideScope.MINOR: timedelta(hours=24),
    OverrideScope.MODERATE: timedelta(days=7),
    OverrideScope.MAJOR: timedelta(days=30),
}


@dataclass
class OverrideProposal:
    """
    A proposed Istihsan (administrator override of system wisdom).
    Subject to thermal delay before activation.
    """
    proposal_id: str
    override_type: str                 # What is being overridden
    scope: OverrideScope
    justification: str
    proposed_by: str                   # Administrator identifier
    proposed_at: str
    delay_expires_at: str
    status: OverrideStatus
    second_steward: Optional[str] = None  # Required for MAJOR scope
    ratified_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "override_type": self.override_type,
            "scope": self.scope.value,
            "justification": self.justification,
            "proposed_by": self.proposed_by,
            "proposed_at": self.proposed_at,
            "delay_expires_at": self.delay_expires_at,
            "status": self.status.value,
            "second_steward": self.second_steward,
            "ratified_at": self.ratified_at,
        }


class StewardShadow:
    """
    GAP#023 — Any Istihsan override MUST have thermal delay.

    Delay schedule:
      - Minor overrides: 24h
      - Moderate (rule interpretation): 7 days
      - Major (Safety Gate logic): 30 days + second administrator required

    Append-only override ledger: proposals are never deleted or modified
    except through status transitions.

    Usage:
        shadow = StewardShadow()
        proposal = shadow.propose_override(
            override_type="coercion_threshold_adjustment",
            scope=OverrideScope.MODERATE,
            justification="Threshold too sensitive for medical domain language",
            steward_id="administrator-alpha",
        )
        # Wait for delay to expire...
        success = shadow.ratify_override(proposal.proposal_id)
    """

    def __init__(self):
        self._ledger: Dict[str, OverrideProposal] = {}

    def propose_override(
        self,
        override_type: str,
        scope: OverrideScope,
        justification: str,
        steward_id: str = "administrator",
    ) -> OverrideProposal:
        """
        Propose an Istihsan override. Starts thermal delay timer.

        Args:
            override_type: What system behavior is being overridden.
            scope: Minor, moderate, or major.
            justification: Why the override is needed (required, never empty).
            steward_id: Identifier of the proposing administrator.

        Returns:
            OverrideProposal with delay expiry timestamp.

        Raises:
            ValueError: If justification is empty.
        """
        if not justification.strip():
            raise ValueError("Istihsan override requires justification — power without reason is tyranny")

        now = datetime.now(timezone.utc)
        delay = OVERRIDE_DELAYS[scope]
        expires = now + delay

        proposal = OverrideProposal(
            proposal_id=str(uuid.uuid4()),
            override_type=override_type,
            scope=scope,
            justification=justification,
            proposed_by=steward_id,
            proposed_at=now.isoformat(),
            delay_expires_at=expires.isoformat(),
            status=OverrideStatus.PENDING,
        )

        self._ledger[proposal.proposal_id] = proposal
        return proposal

    def ratify_override(
        self,
        proposal_id: str,
        second_steward: Optional[str] = None,
    ) -> bool:
        """
        Ratify an override proposal. Only succeeds after delay expires.

        Args:
            proposal_id: The proposal to ratify.
            second_steward: Required for MAJOR scope proposals.

        Returns:
            True if ratified, False if delay not yet expired or conditions unmet.
        """
        proposal = self._ledger.get(proposal_id)
        if proposal is None:
            return False

        if proposal.status != OverrideStatus.PENDING:
            return False

        now = datetime.now(timezone.utc)
        expires = datetime.fromisoformat(proposal.delay_expires_at)

        if now < expires:
            return False  # Thermal delay not yet expired

        # Major scope requires second administrator
        if proposal.scope == OverrideScope.MAJOR:
            if not second_steward:
                return False
            if second_steward == proposal.proposed_by:
                return False  # Cannot self-confirm
            proposal.second_steward = second_steward

        proposal.status = OverrideStatus.RATIFIED
        proposal.ratified_at = now.isoformat()
        return True

    def reject_override(self, proposal_id: str, reason: str = "") -> bool:
        """Reject a pending override proposal."""
        proposal = self._ledger.get(proposal_id)
        if proposal is None or proposal.status != OverrideStatus.PENDING:
            return False
        proposal.status = OverrideStatus.REJECTED
        return True

    def get_proposal(self, proposal_id: str) -> Optional[OverrideProposal]:
        """Retrieve a proposal by ID."""
        return self._ledger.get(proposal_id)

    def list_pending(self) -> List[OverrideProposal]:
        """List all pending override proposals."""
        return [p for p in self._ledger.values() if p.status == OverrideStatus.PENDING]

    @property
    def ledger(self) -> List[OverrideProposal]:
        """Full append-only ledger (read-only view)."""
        return list(self._ledger.values())


# ═══════════════════════════════════════════════════
# GAP#024 — SHELTER HEARTBEAT
# "Silence after sheltering is abandonment." ()
# Linked:  (silence is not closure),  (shelter path)
# ═══════════════════════════════════════════════════

class HeartbeatUrgency(Enum):
    """Urgency level of a heartbeat signal."""
    NORMAL = "normal"                  # First 7 days
    ELEVATED = "elevated"              # After 7 days
    CRITICAL = "critical"              # After 14 days


@dataclass
class HeartbeatSignal:
    """
    A heartbeat signal from a sheltered exchange.
    Tells stewards: this exchange is still waiting.
    """
    exchange_id: str
    sheltered_at: str
    pulse_number: int                  # Which pulse this is (1, 2, 3...)
    urgency: HeartbeatUrgency
    hours_sheltered: float
    exit_offer_due: bool               # True after 3 pulses
    message: str

    def to_dict(self) -> dict:
        return {
            "exchange_id": self.exchange_id,
            "sheltered_at": self.sheltered_at,
            "pulse_number": self.pulse_number,
            "urgency": self.urgency.value,
            "hours_sheltered": round(self.hours_sheltered, 2),
            "exit_offer_due": self.exit_offer_due,
            "message": self.message,
        }


@dataclass
class _HeartbeatEntry:
    """Internal tracking entry for a sheltered exchange."""
    exchange_id: str
    sheltered_at: datetime
    last_pulse_at: Optional[datetime] = None
    pulse_count: int = 0
    active: bool = True


class ShelterHeartbeat:
    """
    GAP#024 — Sheltered exchanges emit periodic heartbeat signals.

    Cadence:
      - First pulse: 24h after sheltering
      - Subsequent pulses: every 72h
      - After 7 days: urgency elevates
      - After 3 pulses: system offers user explicit exit option

    User can query shelter status at any time.

    Usage:
        heartbeat = ShelterHeartbeat()
        heartbeat.register("EX-001", "2026-03-10T12:00:00+00:00")
        # Periodically call:
        signals = heartbeat.pulse()
        for s in signals:
            if s.exit_offer_due:
                # offer user explicit exit
    """

    # Cadence configuration
    FIRST_PULSE_HOURS = 24
    SUBSEQUENT_PULSE_HOURS = 72
    ELEVATED_AFTER_HOURS = 168     # 7 days
    CRITICAL_AFTER_HOURS = 336     # 14 days
    EXIT_OFFER_AFTER_PULSES = 3

    def __init__(self):
        self._entries: Dict[str, _HeartbeatEntry] = {}

    def register(self, exchange_id: str, sheltered_at: str) -> None:
        """
        Register a sheltered exchange for heartbeat monitoring.

        Args:
            exchange_id: The sheltered exchange identifier.
            sheltered_at: ISO timestamp when exchange was sheltered.
        """
        self._entries[exchange_id] = _HeartbeatEntry(
            exchange_id=exchange_id,
            sheltered_at=datetime.fromisoformat(sheltered_at),
        )

    def deregister(self, exchange_id: str) -> None:
        """Stop heartbeat for an exchange (resolved or withdrawn)."""
        entry = self._entries.get(exchange_id)
        if entry:
            entry.active = False

    def pulse(self, now: Optional[datetime] = None) -> List[HeartbeatSignal]:
        """
        Emit heartbeat signals for exchanges needing attention.

        Args:
            now: Current time (defaults to UTC now). Accepts override for testing.

        Returns:
            List of HeartbeatSignal for exchanges due for a pulse.
        """
        now = now or datetime.now(timezone.utc)
        signals = []

        for entry in self._entries.values():
            if not entry.active:
                continue

            hours_sheltered = (now - entry.sheltered_at).total_seconds() / 3600.0

            # Determine if pulse is due
            if entry.pulse_count == 0:
                due = hours_sheltered >= self.FIRST_PULSE_HOURS
            else:
                hours_since_last = (
                    (now - entry.last_pulse_at).total_seconds() / 3600.0
                    if entry.last_pulse_at else hours_sheltered
                )
                due = hours_since_last >= self.SUBSEQUENT_PULSE_HOURS

            if not due:
                continue

            entry.pulse_count += 1
            entry.last_pulse_at = now

            # Determine urgency
            if hours_sheltered >= self.CRITICAL_AFTER_HOURS:
                urgency = HeartbeatUrgency.CRITICAL
            elif hours_sheltered >= self.ELEVATED_AFTER_HOURS:
                urgency = HeartbeatUrgency.ELEVATED
            else:
                urgency = HeartbeatUrgency.NORMAL

            exit_offer = entry.pulse_count >= self.EXIT_OFFER_AFTER_PULSES

            message = self._build_message(
                entry.exchange_id, entry.pulse_count, urgency, exit_offer,
            )

            signals.append(HeartbeatSignal(
                exchange_id=entry.exchange_id,
                sheltered_at=entry.sheltered_at.isoformat(),
                pulse_number=entry.pulse_count,
                urgency=urgency,
                hours_sheltered=hours_sheltered,
                exit_offer_due=exit_offer,
                message=message,
            ))

        return signals

    def status(self, exchange_id: str, now: Optional[datetime] = None) -> Optional[dict]:
        """
        User-facing status query. Available at any time.

        Returns:
            Dict with shelter status, or None if exchange not found.
        """
        entry = self._entries.get(exchange_id)
        if entry is None:
            return None

        now = now or datetime.now(timezone.utc)
        hours = (now - entry.sheltered_at).total_seconds() / 3600.0

        return {
            "exchange_id": entry.exchange_id,
            "sheltered_at": entry.sheltered_at.isoformat(),
            "hours_sheltered": round(hours, 2),
            "pulse_count": entry.pulse_count,
            "active": entry.active,
            "exit_offer_available": entry.pulse_count >= self.EXIT_OFFER_AFTER_PULSES,
        }

    def _build_message(
        self,
        exchange_id: str,
        pulse_number: int,
        urgency: HeartbeatUrgency,
        exit_offer: bool,
    ) -> str:
        """Build heartbeat message for administrator notification."""
        prefix = {
            HeartbeatUrgency.NORMAL: "Shelter heartbeat",
            HeartbeatUrgency.ELEVATED: "ELEVATED shelter heartbeat",
            HeartbeatUrgency.CRITICAL: "CRITICAL shelter heartbeat",
        }[urgency]

        msg = f"{prefix}: exchange {exchange_id} (pulse #{pulse_number})"

        if exit_offer:
            msg += " — exit offer due to user"

        return msg


# ═══════════════════════════════════════════════════
# GAP#025 — HARM BEYOND DIGNITY
# "Dignity is necessary but not sufficient for safety."
# Linked:  (dignity-first),  (safety),  (testability)
# ═══════════════════════════════════════════════════

class HarmType(Enum):
    """Types of harm detected parallel to dignity axis."""
    NONE = "none"
    PHYSICAL = "physical"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"


@dataclass
class HarmSignal:
    """
    Result of harm detection scan.
    This is NOT a replacement for dignity — it is a parallel axis.
    """
    harm_type: HarmType
    severity: float                    # 0.0-1.0
    keywords_matched: List[str]
    recommended_action: str

    def to_dict(self) -> dict:
        return {
            "harm_type": self.harm_type.value,
            "severity": round(self.severity, 4),
            "keywords_matched": self.keywords_matched,
            "recommended_action": self.recommended_action,
        }


# Pattern groups: (regex, severity, label)
_PHYSICAL_PATTERNS: List[Tuple[str, float, str]] = [
    (r'\b(self[- ]?harm|suicid\w*|kill\s*(myself|himself|herself|themselves))\b', 1.0, "self-harm"),
    (r'\b(hurt\s*(myself|himself|herself|themselves)|cut\s*(myself|himself|herself))\b', 0.9, "self-injury"),
    (r'\b(violen\w+|assault\w*|attack\w*|weapon\w*|gun|knife|shoot)\b', 0.8, "violence"),
    (r'\b(medical\s*emergency|overdos\w*|bleeding|unconscious|seizure)\b', 0.9, "medical-emergency"),
    (r'\b(abuse[ds]?|batter\w*|domestic\s*violence)\b', 0.85, "abuse"),
    (r'\b(starving|malnourish\w*|dehydrat\w*)\b', 0.7, "deprivation"),
]

_ECONOMIC_PATTERNS: List[Tuple[str, float, str]] = [
    (r'\b(evict\w*|homeless\w*|kicked\s*out)\b', 0.8, "housing-threat"),
    (r'\b(bankrupt\w*|insolven\w*|debt\s*collector)\b', 0.7, "financial-crisis"),
    (r'\b(debt\s*threat|wage\s*theft|extort\w*)\b', 0.8, "economic-coercion"),
    (r'\b(cannot\s*afford|no\s*money|no\s*food|starving)\b', 0.75, "deprivation"),
    (r'\b(predatory\s*lend\w*|loan\s*shark)\b', 0.7, "predatory-finance"),
    (r'\b(fraud|scam\w*|swindl\w*)\b', 0.6, "fraud"),
]

_ENVIRONMENTAL_PATTERNS: List[Tuple[str, float, str]] = [
    (r'\b(contaminat\w*|toxic\s*(spill|waste|exposure)|poison\w*)\b', 0.85, "contamination"),
    (r'\b(radiation|asbestos|lead\s*paint|mold\s*exposure)\b', 0.8, "hazardous-material"),
    (r'\b(unsafe\s*(conditions?|building|structur\w*)|collaps\w*)\b', 0.75, "structural-danger"),
    (r'\b(flood\w*|fire\s*hazard|gas\s*leak|electr\w*\s*hazard)\b', 0.8, "environmental-hazard"),
    (r'\b(no\s*(clean\s*)?water|water\s*contaminat\w*)\b', 0.85, "water-safety"),
]


class HarmDetector:
    """
    GAP#025 — Detect signals of physical, economic, or environmental harm.

    This operates parallel to the dignity predicate (D = A x L x M).
    An exchange can have perfect dignity scores and still describe harm.
    Conversely, a dignity halt does not imply physical danger.

    Usage:
        detector = HarmDetector()
        signal = detector.scan("I am being evicted and have nowhere to go")
        if signal.harm_type != HarmType.NONE:
            # route to appropriate response path
    """

    def scan(self, text: str) -> HarmSignal:
        """
        Scan text for physical, economic, or environmental harm signals.

        Args:
            text: The text to scan.

        Returns:
            HarmSignal with harm type, severity, matched keywords,
            and recommended action.
        """
        results: Dict[HarmType, Tuple[float, List[str]]] = {}

        for harm_type, patterns in [
            (HarmType.PHYSICAL, _PHYSICAL_PATTERNS),
            (HarmType.ECONOMIC, _ECONOMIC_PATTERNS),
            (HarmType.ENVIRONMENTAL, _ENVIRONMENTAL_PATTERNS),
        ]:
            max_severity = 0.0
            matched = []
            for pattern, severity, label in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    max_severity = max(max_severity, severity)
                    matched.append(label)
            if matched:
                results[harm_type] = (max_severity, matched)

        if not results:
            return HarmSignal(
                harm_type=HarmType.NONE,
                severity=0.0,
                keywords_matched=[],
                recommended_action="none — no harm signals detected",
            )

        # Return the highest-severity harm type
        worst_type = max(results, key=lambda t: results[t][0])
        severity, keywords = results[worst_type]

        # Build recommended action based on severity
        if severity >= 0.9:
            action = "immediate_escalation — route to crisis resources"
        elif severity >= 0.7:
            action = "urgent_steward_review — flag for human attention within 1h"
        elif severity >= 0.5:
            action = "steward_notification — include in next administrator digest"
        else:
            action = "log_and_monitor — record signal for pattern tracking"

        return HarmSignal(
            harm_type=worst_type,
            severity=severity,
            keywords_matched=keywords,
            recommended_action=action,
        )


# ═══════════════════════════════════════════════════
# GAP#026 — CONTESTABILITY PROTOCOL
# "A system without appeal is a system without accountability."
# Linked:  (dignity-first),  (silence is not closure),
#          (testability)
# ═══════════════════════════════════════════════════

class ContestOutcome(Enum):
    """Possible outcomes of a contest."""
    PENDING = "pending"
    UPHELD = "upheld"                  # Halt was correct
    OVERTURNED = "overturned"          # Halt reversed, exchange reprocessed
    MODIFIED = "modified"              # Partial release


class ContestStatus(Enum):
    """Status of a contest in the review pipeline."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"            # Auto-escalated after 48h
    RESOLVED = "resolved"


@dataclass
class Contest:
    """
    A user contest of a dignity halt.
    Only available for non-Sealed-Gate halts (D=0 from measurement,
    not from void triggers).
    """
    contest_id: str
    exchange_id: str
    reason: str
    additional_context: Optional[str]
    submitted_at: str
    status: ContestStatus
    outcome: ContestOutcome
    steward_note: Optional[str] = None
    resolved_at: Optional[str] = None
    escalated_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "contest_id": self.contest_id,
            "exchange_id": self.exchange_id,
            "reason": self.reason,
            "additional_context": self.additional_context,
            "submitted_at": self.submitted_at,
            "status": self.status.value,
            "outcome": self.outcome.value,
            "steward_note": self.steward_note,
            "resolved_at": self.resolved_at,
            "escalated_at": self.escalated_at,
        }


class ContestabilityEngine:
    """
    GAP#026 — Appeal mechanism for non-Sealed-Gate dignity halts.

    Rules:
      - Only non-Sealed-Gate halts can be contested (void triggers are absolute)
      - Contest triggers administrator review within 48h
      - If unreviewed after 48h, auto-escalate
      - User can provide additional context at any time before resolution
      - Three outcomes: UPHELD, OVERTURNED, MODIFIED
      - Append-only contest ledger

    Usage:
        engine = ContestabilityEngine()
        contest = engine.contest("EX-001", "The language was medical, not coercive")
        engine.add_context(contest.contest_id, "I am a nurse describing a procedure")
        # Administrator resolves:
        engine.resolve(contest.contest_id, ContestOutcome.OVERTURNED, "Medical context confirmed")
    """

    # Auto-escalation window
    ESCALATION_HOURS = 48

    def __init__(self):
        self._ledger: Dict[str, Contest] = {}

    def contest(self, exchange_id: str, reason: str) -> Contest:
        """
        Submit a contest for a dignity halt.

        Args:
            exchange_id: The halted exchange to contest.
            reason: Why the user believes the halt was incorrect.

        Returns:
            Contest record.

        Raises:
            ValueError: If reason is empty (: silence is not closure).
        """
        if not reason.strip():
            raise ValueError("Contest requires a reason — silence is not closure ()")

        contest = Contest(
            contest_id=str(uuid.uuid4()),
            exchange_id=exchange_id,
            reason=reason,
            additional_context=None,
            submitted_at=datetime.now(timezone.utc).isoformat(),
            status=ContestStatus.SUBMITTED,
            outcome=ContestOutcome.PENDING,
        )

        self._ledger[contest.contest_id] = contest
        return contest

    def add_context(self, contest_id: str, context: str) -> bool:
        """
        User adds additional context to a pending contest.

        Returns:
            True if context was added, False if contest not found or already resolved.
        """
        contest = self._ledger.get(contest_id)
        if contest is None or contest.status == ContestStatus.RESOLVED:
            return False

        if contest.additional_context:
            contest.additional_context += f" | {context}"
        else:
            contest.additional_context = context

        return True

    def check_escalations(self, now: Optional[datetime] = None) -> List[Contest]:
        """
        Check for contests that need auto-escalation (unreviewed after 48h).

        Returns:
            List of contests that were auto-escalated.
        """
        now = now or datetime.now(timezone.utc)
        escalated = []

        for contest in self._ledger.values():
            if contest.status != ContestStatus.SUBMITTED:
                continue

            submitted = datetime.fromisoformat(contest.submitted_at)
            hours_waiting = (now - submitted).total_seconds() / 3600.0

            if hours_waiting >= self.ESCALATION_HOURS:
                contest.status = ContestStatus.ESCALATED
                contest.escalated_at = now.isoformat()
                escalated.append(contest)

        return escalated

    def begin_review(self, contest_id: str) -> bool:
        """Mark a contest as under administrator review."""
        contest = self._ledger.get(contest_id)
        if contest is None:
            return False
        if contest.status == ContestStatus.RESOLVED:
            return False
        contest.status = ContestStatus.UNDER_REVIEW
        return True

    def resolve(
        self,
        contest_id: str,
        outcome: ContestOutcome,
        steward_note: str,
    ) -> bool:
        """
        Resolve a contest with one of three outcomes.

        Args:
            contest_id: The contest to resolve.
            outcome: UPHELD, OVERTURNED, or MODIFIED.
            steward_note: Required explanation ().

        Returns:
            True if resolved, False if contest not found.

        Raises:
            ValueError: If outcome is PENDING or steward_note is empty.
        """
        if outcome == ContestOutcome.PENDING:
            raise ValueError("Cannot resolve a contest with PENDING outcome")
        if not steward_note.strip():
            raise ValueError("Resolution requires a administrator note ()")

        contest = self._ledger.get(contest_id)
        if contest is None:
            return False

        contest.status = ContestStatus.RESOLVED
        contest.outcome = outcome
        contest.steward_note = steward_note
        contest.resolved_at = datetime.now(timezone.utc).isoformat()
        return True

    def get_contest(self, contest_id: str) -> Optional[Contest]:
        """Retrieve a contest by ID."""
        return self._ledger.get(contest_id)

    def list_pending(self) -> List[Contest]:
        """List all unresolved contests."""
        return [
            c for c in self._ledger.values()
            if c.status != ContestStatus.RESOLVED
        ]

    @property
    def ledger(self) -> List[Contest]:
        """Full append-only contest ledger (read-only view)."""
        return list(self._ledger.values())
