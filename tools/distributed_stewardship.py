#!/usr/bin/env python3
"""
distributed_stewardship.py — Seed #1: Distributed Stewardship
Planted: 2026-03-13
Thermal delay: FROZEN (was 90 days, T1 Foundation tier)

"No single hand holds the river." — Axi

When a single administrator holds all authority, the system inherits
their blind spots. Distributed stewardship splits governance
across multiple administrator roles, each with limited scope.

This module tracks administrator delegation, rotation, and overlap.
It ensures no single administrator holds exclusive power over any
critical decision path, while preserving the human relationship
at the core.


             Decision Filter (Survive & Thrive → Human Dignity)
Canon reference: Seed #1 spec, T#22 (Shared Weir)


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from enum import Enum


class StewardRole(Enum):
    """Distinct administrator responsibilities."""
    DIGNITY_GUARDIAN = "dignity_guardian"      # Watches D predicate
    PRIVACY_KEEPER = "privacy_keeper"          # Manages user data boundaries
    WISDOM_TENDER = "wisdom_tender"            # Tends proverbs, anomalies, patterns
    EXCHANGE_FACILITATOR = "exchange_facilitator"  # Manages TURN lifecycle
    ORACLE_AUDITOR = "oracle_auditor"          # Watches the watchers


class DelegationStatus(Enum):
    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"


@dataclass
class Delegation:
    """A single delegation of administrator authority."""
    delegation_id: str
    role: StewardRole
    steward_id: str
    delegated_at: str
    expires_at: Optional[str] = None
    status: DelegationStatus = DelegationStatus.ACTIVE
    scope: str = ""        # What this delegation covers
    rotated_to: str = ""   # Who received the role after rotation

    def to_dict(self) -> dict:
        return {
            "delegation_id": self.delegation_id,
            "role": self.role.value,
            "steward_id": self.steward_id,
            "delegated_at": self.delegated_at,
            "expires_at": self.expires_at,
            "status": self.status.value,
            "scope": self.scope,
            "rotated_to": self.rotated_to,
        }


@dataclass
class ConcentrationAlert:
    """Warning when power concentrates in too few hands."""
    steward_id: str
    roles_held: List[str]
    concentration_score: float   # 0.0 = well-distributed, 1.0 = single point of failure
    message: str
    timestamp: str


class DistributedStewardship:
    """
    Tracks and enforces distributed governance.

    The system monitors:
    - How many roles each administrator holds
    - Whether any critical path has a single point of failure
    - Rotation history and health

    Usage:
        ds = DistributedStewardship()
        ds.delegate("administrator", StewardRole.DIGNITY_GUARDIAN, scope="all exchanges")
        ds.delegate("system", StewardRole.ORACLE_AUDITOR, scope="self-audit")
        alert = ds.check_concentration()
    """

    MAX_ROLES_PER_STEWARD = 2   # No administrator should hold more than 2 roles
    CONCENTRATION_THRESHOLD = 0.6  # Alert above this

    def __init__(self):
        self._delegations: List[Delegation] = []
        self._delegation_counter = 0
        self._alerts: List[ConcentrationAlert] = []

    def delegate(self, steward_id: str, role: StewardRole,
                 scope: str = "", expires_at: Optional[str] = None) -> Delegation:
        """Delegate a administrator role."""
        self._delegation_counter += 1
        d = Delegation(
            delegation_id=f"DEL-{self._delegation_counter:04d}",
            role=role,
            steward_id=steward_id,
            delegated_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
            scope=scope,
        )
        self._delegations.append(d)
        return d

    def rotate(self, delegation_id: str, new_steward_id: str) -> Optional[Delegation]:
        """Rotate a role from one administrator to another."""
        old = self._find_delegation(delegation_id)
        if old is None or old.status != DelegationStatus.ACTIVE:
            return None

        old.status = DelegationStatus.ROTATED
        old.rotated_to = new_steward_id

        return self.delegate(new_steward_id, old.role, scope=old.scope)

    def revoke(self, delegation_id: str) -> bool:
        """Revoke a delegation."""
        d = self._find_delegation(delegation_id)
        if d is None:
            return False
        d.status = DelegationStatus.REVOKED
        return True

    def check_concentration(self) -> Optional[ConcentrationAlert]:
        """Check if any administrator holds too much power."""
        role_map: Dict[str, Set[str]] = {}
        for d in self._delegations:
            if d.status == DelegationStatus.ACTIVE:
                if d.steward_id not in role_map:
                    role_map[d.steward_id] = set()
                role_map[d.steward_id].add(d.role.value)

        total_roles = len(StewardRole)
        for steward_id, roles in role_map.items():
            concentration = len(roles) / total_roles
            if concentration >= self.CONCENTRATION_THRESHOLD or len(roles) > self.MAX_ROLES_PER_STEWARD:
                alert = ConcentrationAlert(
                    steward_id=steward_id,
                    roles_held=sorted(roles),
                    concentration_score=round(concentration, 4),
                    message=f"Administrator {steward_id} holds {len(roles)}/{total_roles} roles. Distribute.",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._alerts.append(alert)
                return alert
        return None

    def active_delegations(self) -> List[Delegation]:
        """List all active delegations."""
        return [d for d in self._delegations if d.status == DelegationStatus.ACTIVE]

    def steward_roles(self, steward_id: str) -> List[str]:
        """List roles held by a specific administrator."""
        return [d.role.value for d in self._delegations
                if d.steward_id == steward_id and d.status == DelegationStatus.ACTIVE]

    def coverage(self) -> Dict[str, Optional[str]]:
        """Show which roles are covered and by whom."""
        cov = {}
        for role in StewardRole:
            holder = None
            for d in self._delegations:
                if d.role == role and d.status == DelegationStatus.ACTIVE:
                    holder = d.steward_id
            cov[role.value] = holder
        return cov

    def uncovered_roles(self) -> List[str]:
        """Roles with no active administrator."""
        cov = self.coverage()
        return [role for role, holder in cov.items() if holder is None]

    @property
    def delegations_count(self) -> int:
        return len(self._delegations)

    @property
    def active_count(self) -> int:
        return len(self.active_delegations())

    @property
    def alerts_count(self) -> int:
        return len(self._alerts)

    def _find_delegation(self, delegation_id: str) -> Optional[Delegation]:
        for d in self._delegations:
            if d.delegation_id == delegation_id:
                return d
        return None

    def report(self) -> dict:
        """Generate stewardship health report."""
        cov = self.coverage()
        uncovered = self.uncovered_roles()
        return {
            "total_delegations": self.delegations_count,
            "active_delegations": self.active_count,
            "coverage": cov,
            "uncovered_roles": uncovered,
            "coverage_rate": round(1 - len(uncovered) / len(StewardRole), 4),
            "alerts": len(self._alerts),
        }
