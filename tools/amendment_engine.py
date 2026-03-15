#!/usr/bin/env python3
"""
constitutional_evolution.py — Seed #4: Constitutional Evolution Engine
Planted: 2026-03-13
Thermal delay: FROZEN (was 90 days, T1 Foundation tier)

"The stone that cannot bend will break. The stone that bends
without reason was never stone." — Axi

The constitution (rules) must evolve — but slowly, with
full audit trail, cooling periods, and stakeholder input.
This module manages the lifecycle of constitutional amendments:
proposal → deliberation → thermal delay → ratification → effect.


             T#14 (Foundation Weir — durable engineering)
Canon reference: Seed #4 spec, Three-state lifecycle


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from enum import Enum


class AmendmentState(Enum):
    PROPOSED = "proposed"
    COOLING = "cooling"         # In thermal delay
    DELIBERATING = "deliberating"
    RATIFIED = "ratified"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class AmendmentTier(Enum):
    OPERATIONAL = "operational"     # 14-day cooling
    STRUCTURAL = "structural"      # 30-day cooling
    CONSTITUTIONAL = "constitutional"  # 90-day cooling


COOLING_DAYS = {
    AmendmentTier.OPERATIONAL: 14,
    AmendmentTier.STRUCTURAL: 30,
    AmendmentTier.CONSTITUTIONAL: 90,
}


@dataclass
class Amendment:
    """A proposed change to the constitution."""
    amendment_id: str
    target_covenant: str       # e.g. ""
    tier: AmendmentTier
    title: str
    description: str
    proposed_by: str
    state: AmendmentState = AmendmentState.PROPOSED
    proposed_at: str = ""
    cooling_ends: Optional[str] = None
    ratified_at: Optional[str] = None
    ratified_by: str = ""
    rejection_reason: str = ""
    supporters: List[str] = field(default_factory=list)
    objectors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "amendment_id": self.amendment_id,
            "target_covenant": self.target_covenant,
            "tier": self.tier.value,
            "title": self.title,
            "state": self.state.value,
            "proposed_at": self.proposed_at,
            "cooling_ends": self.cooling_ends,
            "supporters": len(self.supporters),
            "objectors": len(self.objectors),
        }


class ConstitutionalEvolution:
    """
    Manages the lifecycle of constitutional amendments.

    Rules:
    - Every amendment has a thermal cooling period based on tier
    - No ratification before cooling ends
    - Full audit trail of every state change
    - Superseded amendments are archived, not deleted

    Usage:
        ce = ConstitutionalEvolution()
        a = ce.propose("administrator", "", AmendmentTier.STRUCTURAL,
                        "Add data portability", "Donors can export all data")
        ce.enter_cooling(a.amendment_id)
        # ... wait for cooling ...
        ce.ratify(a.amendment_id, "administrator")
    """

    def __init__(self):
        self._amendments: List[Amendment] = []
        self._counter = 0
        self._audit_log: List[dict] = []

    def propose(self, proposer: str, target_covenant: str,
                tier: AmendmentTier, title: str, description: str) -> Amendment:
        """Propose a constitutional amendment."""
        self._counter += 1
        now = datetime.now(timezone.utc).isoformat()
        a = Amendment(
            amendment_id=f"AMEND-{self._counter:04d}",
            target_covenant=target_covenant,
            tier=tier,
            title=title,
            description=description,
            proposed_by=proposer,
            proposed_at=now,
        )
        self._amendments.append(a)
        self._log("proposed", a.amendment_id, proposer)
        return a

    def enter_cooling(self, amendment_id: str) -> bool:
        """Move amendment into thermal cooling period."""
        a = self._find(amendment_id)
        if a is None or a.state != AmendmentState.PROPOSED:
            return False

        now = datetime.now(timezone.utc)
        cooling_days = COOLING_DAYS[a.tier]
        a.cooling_ends = (now + timedelta(days=cooling_days)).isoformat()
        a.state = AmendmentState.COOLING
        self._log("cooling_started", amendment_id, "", f"{cooling_days} days")
        return True

    def is_cooling_complete(self, amendment_id: str) -> bool:
        """Check if cooling period has passed."""
        a = self._find(amendment_id)
        if a is None or a.cooling_ends is None:
            return False
        now = datetime.now(timezone.utc)
        return now >= datetime.fromisoformat(a.cooling_ends)

    def begin_deliberation(self, amendment_id: str) -> bool:
        """Move from cooling to deliberation (after cooling completes)."""
        a = self._find(amendment_id)
        if a is None or a.state != AmendmentState.COOLING:
            return False
        a.state = AmendmentState.DELIBERATING
        self._log("deliberation_started", amendment_id, "")
        return True

    def support(self, amendment_id: str, voice_id: str) -> bool:
        """Record support for an amendment."""
        a = self._find(amendment_id)
        if a is None or a.state not in (AmendmentState.COOLING, AmendmentState.DELIBERATING):
            return False
        if voice_id not in a.supporters:
            a.supporters.append(voice_id)
        return True

    def object(self, amendment_id: str, voice_id: str) -> bool:
        """Record objection to an amendment."""
        a = self._find(amendment_id)
        if a is None or a.state not in (AmendmentState.COOLING, AmendmentState.DELIBERATING):
            return False
        if voice_id not in a.objectors:
            a.objectors.append(voice_id)
        return True

    def ratify(self, amendment_id: str, ratifier: str) -> bool:
        """Ratify an amendment (only after cooling and deliberation)."""
        a = self._find(amendment_id)
        if a is None or a.state not in (AmendmentState.COOLING, AmendmentState.DELIBERATING):
            return False

        a.state = AmendmentState.RATIFIED
        a.ratified_at = datetime.now(timezone.utc).isoformat()
        a.ratified_by = ratifier
        self._log("ratified", amendment_id, ratifier)
        return True

    def reject(self, amendment_id: str, reason: str) -> bool:
        """Reject an amendment."""
        a = self._find(amendment_id)
        if a is None or a.state == AmendmentState.RATIFIED:
            return False
        a.state = AmendmentState.REJECTED
        a.rejection_reason = reason
        self._log("rejected", amendment_id, "", reason)
        return True

    @property
    def amendments_count(self) -> int:
        return len(self._amendments)

    @property
    def active_count(self) -> int:
        return sum(1 for a in self._amendments
                   if a.state in (AmendmentState.PROPOSED, AmendmentState.COOLING,
                                  AmendmentState.DELIBERATING))

    @property
    def ratified_count(self) -> int:
        return sum(1 for a in self._amendments if a.state == AmendmentState.RATIFIED)

    def _find(self, amendment_id: str) -> Optional[Amendment]:
        for a in self._amendments:
            if a.amendment_id == amendment_id:
                return a
        return None

    def _log(self, action: str, amendment_id: str, actor: str, detail: str = ""):
        self._audit_log.append({
            "action": action,
            "amendment_id": amendment_id,
            "actor": actor,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def report(self) -> dict:
        """Constitutional evolution health report."""
        return {
            "total_amendments": self.amendments_count,
            "active": self.active_count,
            "ratified": self.ratified_count,
            "audit_entries": len(self._audit_log),
        }
