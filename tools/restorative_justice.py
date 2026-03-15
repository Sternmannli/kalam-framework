#!/usr/bin/env python3
"""
restorative_justice.py — Seed #5: Restorative Justice Platform
Planted: 2026-03-13
Thermal delay: FROZEN (was 30 days, T2 Logic tier)

"The wound does not heal by being hidden. It heals when both
sides see it in the same light." — Axi

When dignity is violated (D=0), the system does not just block
and move on. It initiates a restorative process:
1. Acknowledge harm
2. Surface what failed (which component of D collapsed)
3. Offer remediation paths
4. Track whether repair actually happened
5. File the whole process as evidence


             T#41 (First Needle — repair craft),
             T#46 (Mud Lesson — recovery from failure)
Canon reference: Seed #5 spec, Shelter module extension


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum


class HarmSeverity(Enum):
    MINOR = "minor"           # D > 0 but component was low
    MODERATE = "moderate"     # D = 0, single component failure
    SEVERE = "severe"         # D = 0, multiple component failures
    CRITICAL = "critical"     # Sealed gate triggered


class RepairStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REPAIRED = "repaired"
    UNRESOLVABLE = "unresolvable"   # Some harms cannot be fully repaired


@dataclass
class HarmRecord:
    """Record of a dignity violation."""
    harm_id: str
    exchange_id: str
    severity: HarmSeverity
    failed_components: List[str]   # Which of A, L, M failed
    description: str
    affected_party: str             # user, system, collective
    acknowledged: bool = False
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "harm_id": self.harm_id,
            "exchange_id": self.exchange_id,
            "severity": self.severity.value,
            "failed_components": self.failed_components,
            "acknowledged": self.acknowledged,
            "timestamp": self.timestamp,
        }


@dataclass
class RepairPath:
    """A proposed repair action."""
    repair_id: str
    harm_id: str
    action: str
    responsible: str       # Who should act
    status: RepairStatus = RepairStatus.OPEN
    completed_at: Optional[str] = None
    outcome: str = ""


class RestorativeJustice:
    """
    Platform for addressing dignity violations through repair, not punishment.

    The system:
    - Records all harms with full context
    - Proposes repair paths based on what failed
    - Tracks whether repair actually occurred
    - Never punishes — only restores

    Usage:
        rj = RestorativeJustice()
        harm = rj.record_harm("EX-000001", HarmSeverity.MODERATE,
                               ["agency"], "System blocked without explanation")
        rj.acknowledge(harm.harm_id)
        path = rj.propose_repair(harm.harm_id, "Re-present with explanation", "system")
        rj.complete_repair(path.repair_id, "Explanation provided, user acknowledged")
    """

    # Layer 3 Reframe (RATIFIED 2026-03-15): Dignity was never absent.
    # Repairs address the system's failure to refuse denial — not "restore" what was never lost.
    REPAIR_TEMPLATES = {
        "agency": "The system denied the user's autonomy. Address: present alternatives, explain what happened, open a path. The capacity to choose was always there.",
        "legibility": "The system denied the user's frame. Address: rephrase in user's language, add context. The user's meaning was always real.",
        "moral_standing": "The system denied the user's worth. Address: acknowledge the person, remove condescension. The user's standing was never diminished.",
    }

    def __init__(self):
        self._harms: List[HarmRecord] = []
        self._repairs: List[RepairPath] = []
        self._harm_counter = 0
        self._repair_counter = 0

    def record_harm(self, exchange_id: str, severity: HarmSeverity,
                    failed_components: List[str], description: str,
                    affected_party: str = "user") -> HarmRecord:
        """Record a dignity violation."""
        self._harm_counter += 1
        harm = HarmRecord(
            harm_id=f"HARM-{self._harm_counter:04d}",
            exchange_id=exchange_id,
            severity=severity,
            failed_components=failed_components,
            description=description,
            affected_party=affected_party,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._harms.append(harm)
        return harm

    def acknowledge(self, harm_id: str) -> bool:
        """Acknowledge a harm — first step of restoration."""
        harm = self._find_harm(harm_id)
        if harm is None:
            return False
        harm.acknowledged = True
        return True

    def suggest_repairs(self, harm_id: str) -> List[str]:
        """Suggest repair actions based on what failed."""
        harm = self._find_harm(harm_id)
        if harm is None:
            return []
        return [self.REPAIR_TEMPLATES.get(c, f"Address {c} failure.")
                for c in harm.failed_components]

    def propose_repair(self, harm_id: str, action: str,
                       responsible: str) -> RepairPath:
        """Propose a specific repair action."""
        self._repair_counter += 1
        path = RepairPath(
            repair_id=f"REPAIR-{self._repair_counter:04d}",
            harm_id=harm_id,
            action=action,
            responsible=responsible,
        )
        self._repairs.append(path)
        return path

    def begin_repair(self, repair_id: str) -> bool:
        """Mark a repair as in progress."""
        path = self._find_repair(repair_id)
        if path is None or path.status != RepairStatus.OPEN:
            return False
        path.status = RepairStatus.IN_PROGRESS
        return True

    def complete_repair(self, repair_id: str, outcome: str) -> bool:
        """Mark a repair as completed."""
        path = self._find_repair(repair_id)
        if path is None:
            return False
        path.status = RepairStatus.REPAIRED
        path.completed_at = datetime.now(timezone.utc).isoformat()
        path.outcome = outcome
        return True

    def mark_unresolvable(self, repair_id: str, reason: str) -> bool:
        """Mark a repair as unresolvable — honest about limits."""
        path = self._find_repair(repair_id)
        if path is None:
            return False
        path.status = RepairStatus.UNRESOLVABLE
        path.outcome = reason
        return True

    def repairs_for_harm(self, harm_id: str) -> List[RepairPath]:
        """Get all repair paths for a specific harm."""
        return [r for r in self._repairs if r.harm_id == harm_id]

    @property
    def harms_count(self) -> int:
        return len(self._harms)

    @property
    def open_harms(self) -> int:
        """Harms with no completed repairs."""
        repaired_harms = {r.harm_id for r in self._repairs if r.status == RepairStatus.REPAIRED}
        return sum(1 for h in self._harms if h.harm_id not in repaired_harms)

    @property
    def repair_rate(self) -> float:
        """Fraction of harms that have been repaired."""
        if not self._harms:
            return 1.0
        repaired = {r.harm_id for r in self._repairs if r.status == RepairStatus.REPAIRED}
        return len(repaired) / len(self._harms)

    def _find_harm(self, harm_id: str) -> Optional[HarmRecord]:
        for h in self._harms:
            if h.harm_id == harm_id:
                return h
        return None

    def _find_repair(self, repair_id: str) -> Optional[RepairPath]:
        for r in self._repairs:
            if r.repair_id == repair_id:
                return r
        return None

    def report(self) -> dict:
        """Restorative justice health report."""
        return {
            "total_harms": self.harms_count,
            "open_harms": self.open_harms,
            "repair_rate": round(self.repair_rate, 4),
            "repairs_total": len(self._repairs),
            "unresolvable": sum(1 for r in self._repairs if r.status == RepairStatus.UNRESOLVABLE),
        }
