#!/usr/bin/env python3
"""
system_self_awareness.py — Seed #6: System Self-Awareness
Planted: 2026-03-13
Thermal delay: FROZEN (was 30 days, T2 Logic tier)

"The river that does not know its own depth drowns the careful." — Axi

The system must know what it is, what it can do, and what it cannot.
Self-awareness is not consciousness — it is operational transparency.
The system reports its own capabilities, limitations, and current state
without inflation or false modesty.

Extends the Oracle module with introspective capabilities:
- Capability inventory (what the system can actually do)
- Limitation registry (what it cannot do or does poorly)
- Confidence calibration (is it over- or under-confident?)
- Blind spot tracking (integration with Negative Space Index)


             T#20 (Weir Night Watch — honest reporting)
Canon reference: Seed #6 spec, Oracle Problem (GAP#019)


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum


class CapabilityLevel(Enum):
    STRONG = "strong"         # System does this well
    ADEQUATE = "adequate"     # System can do this with limitations
    WEAK = "weak"             # System struggles with this
    ABSENT = "absent"         # System cannot do this at all


class CalibrationBias(Enum):
    OVERCONFIDENT = "overconfident"   # Claims more than it delivers
    CALIBRATED = "calibrated"         # Claims match delivery
    UNDERCONFIDENT = "underconfident" # Delivers more than it claims


@dataclass
class Capability:
    """A registered system capability."""
    capability_id: str
    domain: str
    description: str
    level: CapabilityLevel
    evidence: str = ""
    last_verified: str = ""

    def to_dict(self) -> dict:
        return {
            "capability_id": self.capability_id,
            "domain": self.domain,
            "level": self.level.value,
            "description": self.description,
            "last_verified": self.last_verified,
        }


@dataclass
class Limitation:
    """A registered system limitation."""
    limitation_id: str
    domain: str
    description: str
    workaround: str = ""     # What the system does instead
    severity: float = 0.5    # 0.0 = minor, 1.0 = critical gap
    acknowledged: bool = True

    def to_dict(self) -> dict:
        return {
            "limitation_id": self.limitation_id,
            "domain": self.domain,
            "description": self.description,
            "severity": self.severity,
            "acknowledged": self.acknowledged,
        }


@dataclass
class CalibrationRecord:
    """A single calibration measurement."""
    predicted_confidence: float   # What the system said it was
    actual_outcome: bool          # Whether it was actually correct
    domain: str
    timestamp: str


class SystemSelfAwareness:
    """
    The system's knowledge of itself.

    Not consciousness. Not sentience. Operational self-knowledge:
    - What can I do?
    - What can I not do?
    - Am I overconfident or underconfident?
    - What am I not seeing?

    Usage:
        ssa = SystemSelfAwareness()
        ssa.register_capability("dignity_check", "ethics",
                                "Evaluate dignity predicate D=A×L×M", CapabilityLevel.STRONG)
        ssa.register_limitation("cultural_context", "culture",
                                "Cannot detect culture-specific dignity violations")
        ssa.record_calibration(0.9, True, "ethics")  # predicted 90%, was correct
        ssa.record_calibration(0.9, False, "culture") # predicted 90%, was wrong
        report = ssa.calibration_report()
    """

    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._limitations: Dict[str, Limitation] = {}
        self._calibrations: List[CalibrationRecord] = []
        self._cap_counter = 0
        self._lim_counter = 0

    def register_capability(self, capability_id: str, domain: str,
                            description: str, level: CapabilityLevel,
                            evidence: str = "") -> Capability:
        """Register a system capability."""
        cap = Capability(
            capability_id=capability_id,
            domain=domain,
            description=description,
            level=level,
            evidence=evidence,
            last_verified=datetime.now(timezone.utc).isoformat(),
        )
        self._capabilities[capability_id] = cap
        return cap

    def register_limitation(self, limitation_id: str, domain: str,
                            description: str, workaround: str = "",
                            severity: float = 0.5) -> Limitation:
        """Register a system limitation — honest about what we can't do."""
        lim = Limitation(
            limitation_id=limitation_id,
            domain=domain,
            description=description,
            workaround=workaround,
            severity=max(0.0, min(1.0, severity)),
        )
        self._limitations[limitation_id] = lim
        return lim

    def record_calibration(self, predicted_confidence: float,
                           actual_outcome: bool, domain: str) -> None:
        """Record a calibration measurement."""
        self._calibrations.append(CalibrationRecord(
            predicted_confidence=max(0.0, min(1.0, predicted_confidence)),
            actual_outcome=actual_outcome,
            domain=domain,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

    def calibration_bias(self) -> CalibrationBias:
        """Determine if the system is over- or under-confident."""
        if len(self._calibrations) < 5:
            return CalibrationBias.CALIBRATED  # Not enough data

        avg_confidence = sum(c.predicted_confidence for c in self._calibrations) / len(self._calibrations)
        actual_rate = sum(1 for c in self._calibrations if c.actual_outcome) / len(self._calibrations)

        diff = avg_confidence - actual_rate
        if diff > 0.1:
            return CalibrationBias.OVERCONFIDENT
        elif diff < -0.1:
            return CalibrationBias.UNDERCONFIDENT
        return CalibrationBias.CALIBRATED

    def capability_coverage(self) -> Dict[str, int]:
        """Count capabilities by level."""
        counts: Dict[str, int] = {level.value: 0 for level in CapabilityLevel}
        for cap in self._capabilities.values():
            counts[cap.level.value] += 1
        return counts

    def critical_limitations(self) -> List[Limitation]:
        """Limitations with severity >= 0.8."""
        return [l for l in self._limitations.values() if l.severity >= 0.8]

    @property
    def capabilities_count(self) -> int:
        return len(self._capabilities)

    @property
    def limitations_count(self) -> int:
        return len(self._limitations)

    @property
    def calibrations_count(self) -> int:
        return len(self._calibrations)

    def report(self) -> dict:
        """Self-awareness health report."""
        return {
            "capabilities": self.capabilities_count,
            "limitations": self.limitations_count,
            "critical_limitations": len(self.critical_limitations()),
            "calibration_bias": self.calibration_bias().value,
            "calibration_samples": self.calibrations_count,
            "capability_coverage": self.capability_coverage(),
        }
