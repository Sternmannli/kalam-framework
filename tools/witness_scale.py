#!/usr/bin/env python3
"""
oracle.py — The Oracle (Self-Audit Layer)
Version: 1.0

Linked Rules:  (dignity-first),  (verification),  (mycelial wisdom)

"Who watches the dignity watchers?"

The Oracle is the system's answer to its own greatest self-identified risk.
It combines three mechanisms:
  1. Witness Scale (W-0 through W-5) — tracks what has been seen
  2. Proprioception Check — detects if the relay is functioning
  3. Self-Audit Cycle — periodic structural health check

The Oracle does not solve GAP#019. It makes it measurable and visible.
An honest gap is more useful than a confident invention.


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional
from enum import Enum


# ═══════════════════════════════════════════════════
# WITNESS SCALE (W-0 through W-5)
# ═══════════════════════════════════════════════════

class WitnessLevel(Enum):
    """Six levels measuring the relationship between system and administrator."""
    UNSEEN = 0      # W-0: Exists in registry, never referenced
    PASSED = 1      # W-1: System processed it, no administrator contact
    FLAGGED = 2     # W-2: System surfaced it, administrator has not responded
    SEEN = 3        # W-3: Administrator has acknowledged it
    HELD = 4        # W-4: Administrator has returned to it across sessions
    EMBODIED = 5    # W-5: Administrator used it to make a system-changing decision


@dataclass
class WitnessTransition:
    """A single W-Scale transition, logged append-only."""
    element_id: str
    from_level: WitnessLevel
    to_level: WitnessLevel
    session_id: str
    context: str
    timestamp: str


@dataclass
class WitnessRecord:
    """Witness state for a single element."""
    element_id: str
    element_type: str       # "proverb", "anomaly", "rule", "gap", "wisdom"
    level: WitnessLevel
    first_registered: str
    last_transition: str
    transition_count: int
    sessions_seen: int


class WitnessScale:
    """
    The W-Scale: measures not the content, but the relationship between
    the system and its administrator around that content.

    Rules:
      1. W-Scale is non-decreasing — once W-3, cannot fall below W-3
      2. Transitions are append-only ()
      3. W-Scale does not measure quality — only witnessing
      4. Interacts with Decay: nothing should decay unseen
      5. Applies to all registry elements
    """

    def __init__(self, thermal_delay_cycles: int = 10):
        self._elements: Dict[str, WitnessRecord] = {}
        self._transitions: List[WitnessTransition] = []
        self._thermal_delay = thermal_delay_cycles
        self._cycle = 0

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def register(self, element_id: str, element_type: str = "unknown") -> WitnessRecord:
        """Register a new element at W-0 (UNSEEN)."""
        if element_id in self._elements:
            return self._elements[element_id]

        record = WitnessRecord(
            element_id=element_id,
            element_type=element_type,
            level=WitnessLevel.UNSEEN,
            first_registered=self._now(),
            last_transition=self._now(),
            transition_count=0,
            sessions_seen=0,
        )
        self._elements[element_id] = record
        return record

    def transition(self, element_id: str, to_level: WitnessLevel,
                   session_id: str = "", context: str = "") -> Optional[WitnessRecord]:
        """
        Transition an element to a new witness level.

        Rule 1: Non-decreasing — once at W-3+, cannot go below W-3.
        """
        record = self._elements.get(element_id)
        if record is None:
            return None

        # Non-decreasing rule: W-3+ is irreversible
        if record.level.value >= WitnessLevel.SEEN.value and to_level.value < WitnessLevel.SEEN.value:
            return record  # Silently refuse downgrade

        # No-op if same level
        if record.level == to_level:
            return record

        # Cannot go backwards at all (append-only principle)
        if to_level.value < record.level.value:
            return record

        # Log transition (append-only, )
        transition = WitnessTransition(
            element_id=element_id,
            from_level=record.level,
            to_level=to_level,
            session_id=session_id,
            context=context,
            timestamp=self._now(),
        )
        self._transitions.append(transition)

        record.level = to_level
        record.last_transition = self._now()
        record.transition_count += 1
        if to_level.value >= WitnessLevel.SEEN.value:
            record.sessions_seen += 1

        return record

    def process(self, element_id: str, element_type: str = "unknown") -> WitnessRecord:
        """Mark an element as processed by the system (W-0 → W-1)."""
        if element_id not in self._elements:
            self.register(element_id, element_type)
        record = self._elements[element_id]
        if record.level == WitnessLevel.UNSEEN:
            self.transition(element_id, WitnessLevel.PASSED, context="system_processed")
        return record

    def flag(self, element_id: str, context: str = "") -> Optional[WitnessRecord]:
        """Surface an element for administrator attention (→ W-2)."""
        return self.transition(element_id, WitnessLevel.FLAGGED, context=context or "system_flagged")

    def steward_sees(self, element_id: str, session_id: str = "") -> Optional[WitnessRecord]:
        """Administrator acknowledges an element (→ W-3)."""
        return self.transition(element_id, WitnessLevel.SEEN,
                               session_id=session_id, context="steward_acknowledged")

    def steward_holds(self, element_id: str, session_id: str = "") -> Optional[WitnessRecord]:
        """Administrator returns to an element across sessions (→ W-4)."""
        return self.transition(element_id, WitnessLevel.HELD,
                               session_id=session_id, context="steward_returned")

    def steward_embodies(self, element_id: str, session_id: str = "",
                         decision: str = "") -> Optional[WitnessRecord]:
        """Administrator uses element to change the system (→ W-5)."""
        return self.transition(element_id, WitnessLevel.EMBODIED,
                               session_id=session_id, context=f"steward_decision: {decision}")

    def tick(self) -> List[str]:
        """
        Advance one cycle. Return element IDs that need surfacing.

        Critical Threshold Rule: elements at W-0/W-1 beyond thermal delay
        trigger a surfacing event.
        """
        self._cycle += 1
        needs_surfacing = []

        for eid, record in self._elements.items():
            if record.level.value <= WitnessLevel.PASSED.value:
                # How many cycles since registration?
                # Simplified: use transition_count as proxy for age
                # In production, compare timestamps
                if self._cycle > self._thermal_delay:
                    needs_surfacing.append(eid)

        # Auto-flag elements that need surfacing
        for eid in needs_surfacing:
            self.flag(eid, context=f"thermal_delay_exceeded_cycle_{self._cycle}")

        return needs_surfacing

    def get(self, element_id: str) -> Optional[WitnessRecord]:
        """Get witness record for an element."""
        return self._elements.get(element_id)

    def distribution(self) -> Dict[str, int]:
        """Count elements at each witness level."""
        counts = {level.name: 0 for level in WitnessLevel}
        for record in self._elements.values():
            counts[record.level.name] += 1
        return counts

    def unwatched(self) -> List[WitnessRecord]:
        """All elements at W-0 or W-1 (automation territory)."""
        return [r for r in self._elements.values()
                if r.level.value <= WitnessLevel.PASSED.value]

    def witnessed(self) -> List[WitnessRecord]:
        """All elements at W-3+ (administrator has witnessed)."""
        return [r for r in self._elements.values()
                if r.level.value >= WitnessLevel.SEEN.value]

    @property
    def total_elements(self) -> int:
        return len(self._elements)

    @property
    def total_transitions(self) -> int:
        return len(self._transitions)

    @property
    def cycle(self) -> int:
        return self._cycle


# ═══════════════════════════════════════════════════
# PROPRIOCEPTION CHECK
# ═══════════════════════════════════════════════════

class RelayStatus(Enum):
    """Status of the administrator → system → system relay."""
    HEALTHY = "healthy"         # All layers functioning
    DEGRADED = "degraded"       # Some loss of fidelity
    INTERRUPTED = "interrupted"  # Relay broken — halt condition


@dataclass
class ProprioceptionResult:
    """Result of a proprioception check."""
    status: RelayStatus
    correction_trace: bool      # system correction delta present?
    response_fidelity: bool     # system reflects administrator's intent?
    steward_recognition: bool   # administrator can find themselves in output?
    halt_required: bool         # SEALED_GATE_TIER halt?
    details: str
    timestamp: str


def check_proprioception(
    has_correction_trace: bool,
    has_response_fidelity: bool,
    has_steward_recognition: bool,
) -> ProprioceptionResult:
    """
    Check if the relay is functioning.

    Three detection signals:
      1. system correction trace — message carries correction delta
      2. system response fidelity — response reflects original intent
      3. Administrator recognition — administrator finds themselves in output

    If all three fail → INTERRUPTED (halt condition).
    If any one fails → DEGRADED (warning).
    """
    signals = [has_correction_trace, has_response_fidelity, has_steward_recognition]
    passing = sum(signals)

    if passing == 3:
        status = RelayStatus.HEALTHY
        halt = False
        details = "Relay functioning: all three proprioception signals present"
    elif passing == 0:
        status = RelayStatus.INTERRUPTED
        halt = True
        details = "PROPRIOCEPTION LOSS: relay interrupted, no signals detected — HALT REQUIRED"
    else:
        status = RelayStatus.DEGRADED
        halt = False
        failed = []
        if not has_correction_trace:
            failed.append("correction_trace")
        if not has_response_fidelity:
            failed.append("response_fidelity")
        if not has_steward_recognition:
            failed.append("steward_recognition")
        details = f"Relay degraded: missing {', '.join(failed)}"

    return ProprioceptionResult(
        status=status,
        correction_trace=has_correction_trace,
        response_fidelity=has_response_fidelity,
        steward_recognition=has_steward_recognition,
        halt_required=halt,
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ═══════════════════════════════════════════════════
# SELF-AUDIT CYCLE (The Oracle)
# ═══════════════════════════════════════════════════

class AuditSeverity(Enum):
    CLEAR = "clear"         # No issues found
    ADVISORY = "advisory"   # Minor concerns
    WARNING = "warning"     # Structural concern
    CRITICAL = "critical"   # Immediate attention required
    HALT = "halt"           # System must stop


@dataclass
class AuditFinding:
    """A single finding from a self-audit."""
    check_name: str
    severity: AuditSeverity
    description: str
    recommendation: str


@dataclass
class OracleReport:
    """Complete self-audit report."""
    cycle: int
    findings: List[AuditFinding]
    highest_severity: str
    witness_distribution: Dict[str, int]
    unwatched_count: int
    proprioception: str
    colonial_creep_risk: float  # 0-1 estimated drift risk
    overall_health: str         # "healthy", "degraded", "critical", "halted"
    timestamp: str

    def summary(self) -> str:
        lines = [f"ORACLE REPORT — Cycle {self.cycle} — {self.overall_health.upper()}"]
        lines.append(f"  Proprioception: {self.proprioception}")
        lines.append(f"  Unwatched elements: {self.unwatched_count}")
        lines.append(f"  Colonial creep risk: {self.colonial_creep_risk:.1%}")
        for f in self.findings:
            icon = {"clear": ".", "advisory": "~", "warning": "!", "critical": "!!", "halt": "X"}
            lines.append(f"  [{icon.get(f.severity.value, '?')}] {f.check_name}: {f.description}")
        return "\n".join(lines)


class Oracle:
    """
    The Oracle — self-audit layer for the kalam system.

    Addresses GAP#019 by making the Oracle Problem measurable.
    Does not claim to solve it — holds the gap honestly.

    Usage:
        oracle = Oracle()

        # Register elements as they enter the system
        oracle.witness.process("P#0001", "proverb")
        oracle.witness.steward_sees("P#0001", "session-42")

        # Run periodic self-audit
        report = oracle.audit(
            dignity_scores=[0.8, 0.7, 0.9],
            drift_rate=-0.02,
            drift_level="stable",
            srvp_score=0.85,
            voice_score=0.9,
            breath_paused=False,
            violations_count=0,
        )
    """

    def __init__(self, thermal_delay_cycles: int = 10):
        self.witness = WitnessScale(thermal_delay_cycles=thermal_delay_cycles)
        self._audit_cycle = 0
        self._reports: List[OracleReport] = []
        self._last_proprioception = None

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def check_relay(self, correction_trace: bool, response_fidelity: bool,
                    steward_recognition: bool) -> ProprioceptionResult:
        """Run proprioception check."""
        result = check_proprioception(correction_trace, response_fidelity, steward_recognition)
        self._last_proprioception = result
        return result

    def audit(
        self,
        dignity_scores: List[float] = None,
        drift_rate: float = 0.0,
        drift_level: str = "stable",
        srvp_score: float = 1.0,
        voice_score: float = 1.0,
        breath_paused: bool = False,
        violations_count: int = 0,
        lock_rate: float = 1.0,
        latency_dignity_rate: float = 1.0,
    ) -> OracleReport:
        """
        Run a full self-audit cycle.

        Checks:
          1. Witness Scale health — are elements being seen?
          2. Proprioception — is the relay functioning?
          3. Dignity drift — is D declining?
          4. Colonial Creep risk — estimated drift between text and behavior
          5. Voice integrity — is Axi voice being maintained?
          6. System stress — is the system overwhelmed?
          7. Lock Test health — are proverbs maintaining quality?
          8. Latency dignity — is T_d being respected?
        """
        self._audit_cycle += 1
        findings = []

        # Tick the witness scale
        surfaced = self.witness.tick()

        # ── Check 1: Witness Scale Health ──
        dist = self.witness.distribution()
        total = self.witness.total_elements
        unwatched = len(self.witness.unwatched())

        if total > 0:
            unwatched_ratio = unwatched / total
            if unwatched_ratio > 0.8:
                findings.append(AuditFinding(
                    "witness_scale", AuditSeverity.CRITICAL,
                    f"{unwatched_ratio:.0%} of elements unwatched ({unwatched}/{total})",
                    "Administrator engagement needed — system operating mostly unseen",
                ))
            elif unwatched_ratio > 0.5:
                findings.append(AuditFinding(
                    "witness_scale", AuditSeverity.WARNING,
                    f"{unwatched_ratio:.0%} of elements unwatched",
                    "Increase administrator review frequency",
                ))
            elif surfaced:
                findings.append(AuditFinding(
                    "witness_scale", AuditSeverity.ADVISORY,
                    f"{len(surfaced)} elements surfaced beyond thermal delay",
                    "Review surfaced elements",
                ))

        # ── Check 2: Proprioception ──
        prop_status = "unknown"
        if self._last_proprioception:
            prop_status = self._last_proprioception.status.value
            if self._last_proprioception.halt_required:
                findings.append(AuditFinding(
                    "proprioception", AuditSeverity.HALT,
                    "PROPRIOCEPTION LOSS — relay interrupted",
                    "System must halt. Restore administrator → system → system relay.",
                ))
            elif self._last_proprioception.status == RelayStatus.DEGRADED:
                findings.append(AuditFinding(
                    "proprioception", AuditSeverity.WARNING,
                    f"Relay degraded: {self._last_proprioception.details}",
                    "Investigate missing proprioception signals",
                ))

        # ── Check 3: Dignity Drift ──
        if drift_level == "critical":
            findings.append(AuditFinding(
                "dignity_drift", AuditSeverity.CRITICAL,
                f"Critical dignity drift: dD/dt={drift_rate:.4f}",
                "Immediate review — dignity declining rapidly",
            ))
        elif drift_level == "declining":
            findings.append(AuditFinding(
                "dignity_drift", AuditSeverity.WARNING,
                f"Dignity declining: dD/dt={drift_rate:.4f}",
                "Monitor and investigate cause of decline",
            ))

        # ── Check 4: Colonial Creep Risk ──
        # Estimated from multiple signals: drift, voice degradation,
        # unwatched elements, low SRVP scores
        creep_signals = []
        if drift_rate < -0.05:
            creep_signals.append(0.3)
        if voice_score < 0.7:
            creep_signals.append(0.2)
        if total > 0 and unwatched / max(total, 1) > 0.5:
            creep_signals.append(0.2)
        if srvp_score < 0.5:
            creep_signals.append(0.3)

        creep_risk = min(1.0, sum(creep_signals))
        if creep_risk >= 0.5:
            findings.append(AuditFinding(
                "colonial_creep", AuditSeverity.WARNING,
                f"Colonial Creep risk elevated: {creep_risk:.0%}",
                "Invisible drift between rule text and system behavior detected",
            ))
        elif creep_risk >= 0.3:
            findings.append(AuditFinding(
                "colonial_creep", AuditSeverity.ADVISORY,
                f"Colonial Creep risk moderate: {creep_risk:.0%}",
                "Monitor for rule-behavior divergence",
            ))

        # ── Check 5: Voice Integrity ──
        if voice_score < 0.5:
            findings.append(AuditFinding(
                "voice_integrity", AuditSeverity.WARNING,
                f"Voice score low: {voice_score:.2f}",
                "Axi voice rules being violated frequently",
            ))

        # ── Check 6: System Stress ──
        if breath_paused:
            findings.append(AuditFinding(
                "system_stress", AuditSeverity.WARNING,
                "System is paused (BREATH halted)",
                "Investigate pause reason and resume when safe",
            ))
        if violations_count > 5:
            findings.append(AuditFinding(
                "dignity_violations", AuditSeverity.WARNING,
                f"{violations_count} dignity violations recorded",
                "Review recent exchanges for systematic failures",
            ))

        # ── Check 7: Lock Test Health ──
        if lock_rate < 0.3:
            findings.append(AuditFinding(
                "lock_test", AuditSeverity.ADVISORY,
                f"Low proverb lock rate: {lock_rate:.0%}",
                "Proverb quality may be declining",
            ))

        # ── Check 8: Latency Dignity ──
        if latency_dignity_rate < 0.8:
            findings.append(AuditFinding(
                "latency_dignity", AuditSeverity.WARNING,
                f"Latency dignity rate: {latency_dignity_rate:.0%}",
                "System responding too fast — T_d not being respected",
            ))

        # Determine overall health
        severities = [f.severity for f in findings]
        if AuditSeverity.HALT in severities:
            overall = "halted"
            highest = "halt"
        elif AuditSeverity.CRITICAL in severities:
            overall = "critical"
            highest = "critical"
        elif AuditSeverity.WARNING in severities:
            overall = "degraded"
            highest = "warning"
        elif AuditSeverity.ADVISORY in severities:
            overall = "healthy"
            highest = "advisory"
        else:
            overall = "healthy"
            highest = "clear"

        report = OracleReport(
            cycle=self._audit_cycle,
            findings=findings,
            highest_severity=highest,
            witness_distribution=dist,
            unwatched_count=unwatched,
            proprioception=prop_status,
            colonial_creep_risk=round(creep_risk, 4),
            overall_health=overall,
            timestamp=self._now(),
        )
        self._reports.append(report)
        return report

    @property
    def audit_cycle(self) -> int:
        return self._audit_cycle

    @property
    def last_report(self) -> Optional[OracleReport]:
        return self._reports[-1] if self._reports else None

    @property
    def reports_count(self) -> int:
        return len(self._reports)
