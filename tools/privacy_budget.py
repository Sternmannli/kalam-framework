#!/usr/bin/env python3
"""
privacy_budget.py — Global privacy budget accounting for differential privacy
systems. Tracks epsilon consumption, enforces limits, projects exhaustion, and
provides administrator visibility.

Grounded in:
  - Federation protocol spec: epsilon <= 1.0 total, k >= 7, 14-day window

Key principle: epsilon is global, not per-query. Composition matters.
  Basic composition: epsilon_total = sum(epsilon_i) (each query adds to the total)
  Advanced composition (Dwork et al.): epsilon_total <= sqrt(2n * ln(1/delta)) * epsilon_per + n * epsilon_per * (e^epsilon_per - 1)

This module uses basic composition (conservative) with an option
to switch to advanced composition when the math is validated.
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Dict

# Privacy constants (from federation protocol / export module)
EPSILON_TOTAL_BUDGET = 1.0        # Total lifetime budget
EPSILON_PER_QUERY = 0.1           # Default per-query cost
K_ANONYMITY_FLOOR = 7             # Minimum k-anonymity
TEMPORAL_WINDOW_DAYS = 14         # Minimum aggregation window
DELTA = 1e-5                      # Failure probability for advanced composition


@dataclass
class BudgetEntry:
    """A single privacy budget consumption event."""
    entry_id: str
    epsilon_consumed: float
    module: str                    # Which module consumed it
    operation: str                 # What operation (pattern_scan, export, query, etc.)
    timestamp: str
    cumulative_epsilon: float      # Running total after this entry
    k_achieved: int                # Actual k-anonymity achieved
    approved_by: str               # "system", "administrator", "auto"


@dataclass
class BudgetState:
    """Current state of the privacy budget."""
    total_budget: float
    consumed: float
    remaining: float
    utilization_pct: float
    entries_count: int
    last_consumption: Optional[str]
    projected_exhaustion: Optional[str]  # Estimated date of exhaustion at current rate
    status: str                    # "healthy", "warning", "critical", "exhausted"
    daily_rate: float              # Average epsilon consumed per day


class PrivacyBudget:
    """
    Global privacy budget accountant.

    Tracks every epsilon consumption, enforces limits, and provides
    administrator-facing metrics. The budget is append-only — consumption
    can never be reversed.
    """

    # Status thresholds
    WARNING_THRESHOLD = 0.7       # 70% consumed -> warning
    CRITICAL_THRESHOLD = 0.9      # 90% consumed -> critical

    def __init__(self, total_budget: float = EPSILON_TOTAL_BUDGET,
                 ledger_path: Optional[Path] = None):
        self._total = total_budget
        self._consumed = 0.0
        self._entries: List[BudgetEntry] = []
        self._counter = 0
        self._locked = False       # Emergency lock
        self._ledger_path = ledger_path or Path("privacy_budget_ledger.json")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _next_id(self) -> str:
        self._counter += 1
        return f"PB-{self._counter:04d}"

    @property
    def remaining(self) -> float:
        return max(0.0, self._total - self._consumed)

    @property
    def utilization(self) -> float:
        return self._consumed / self._total if self._total > 0 else 1.0

    @property
    def is_exhausted(self) -> bool:
        return self._consumed >= self._total

    @property
    def is_locked(self) -> bool:
        return self._locked

    def can_consume(self, epsilon: float) -> bool:
        """Check if a consumption is possible without exceeding budget."""
        if self._locked:
            return False
        return (self._consumed + epsilon) <= self._total

    def consume(self, epsilon: float, module: str, operation: str,
                k_achieved: int = K_ANONYMITY_FLOOR,
                approved_by: str = "system") -> Optional[BudgetEntry]:
        """
        Consume privacy budget. Returns BudgetEntry if successful, None if denied.

        Denial reasons:
          - Budget exhausted
          - k-anonymity below floor
          - Emergency lock active
        """
        # Check lock
        if self._locked:
            return None

        # Check k-anonymity
        if k_achieved < K_ANONYMITY_FLOOR:
            return None

        # Check budget
        if not self.can_consume(epsilon):
            return None

        # Consume
        self._consumed += epsilon
        entry = BudgetEntry(
            entry_id=self._next_id(),
            epsilon_consumed=epsilon,
            module=module,
            operation=operation,
            timestamp=self._now(),
            cumulative_epsilon=round(self._consumed, 6),
            k_achieved=k_achieved,
            approved_by=approved_by,
        )
        self._entries.append(entry)

        # Auto-lock if exhausted
        if self.is_exhausted:
            self._locked = True

        return entry

    def lock(self, reason: str = "manual"):
        """Emergency lock — no further consumption allowed."""
        self._locked = True
        self._entries.append(BudgetEntry(
            entry_id=self._next_id(),
            epsilon_consumed=0.0,
            module="privacy_budget",
            operation=f"LOCK: {reason}",
            timestamp=self._now(),
            cumulative_epsilon=self._consumed,
            k_achieved=0,
            approved_by="administrator",
        ))

    def unlock(self, admin_approval: str = "administrator"):
        """Unlock — requires administrator approval. Only if budget remains."""
        if self.is_exhausted:
            return False  # Cannot unlock exhausted budget
        self._locked = False
        self._entries.append(BudgetEntry(
            entry_id=self._next_id(),
            epsilon_consumed=0.0,
            module="privacy_budget",
            operation="UNLOCK",
            timestamp=self._now(),
            cumulative_epsilon=self._consumed,
            k_achieved=0,
            approved_by=admin_approval,
        ))
        return True

    def _daily_rate(self) -> float:
        """Compute average daily epsilon consumption rate."""
        if len(self._entries) < 2:
            return 0.0

        # Find entries that actually consumed epsilon
        consuming = [e for e in self._entries if e.epsilon_consumed > 0]
        if len(consuming) < 2:
            return 0.0

        first_ts = datetime.fromisoformat(consuming[0].timestamp.replace("Z", "+00:00"))
        last_ts = datetime.fromisoformat(consuming[-1].timestamp.replace("Z", "+00:00"))
        days = max((last_ts - first_ts).total_seconds() / 86400, 0.001)
        total_consumed = sum(e.epsilon_consumed for e in consuming)
        return total_consumed / days

    def _projected_exhaustion(self) -> Optional[str]:
        """Project when the budget will be exhausted at current rate."""
        rate = self._daily_rate()
        if rate <= 0:
            return None
        days_remaining = self.remaining / rate
        exhaustion_date = datetime.now(timezone.utc) + timedelta(days=days_remaining)
        return exhaustion_date.isoformat()

    def state(self) -> BudgetState:
        """Current budget state — administrator dashboard data."""
        utilization = self.utilization

        if self.is_exhausted:
            status = "exhausted"
        elif utilization >= self.CRITICAL_THRESHOLD:
            status = "critical"
        elif utilization >= self.WARNING_THRESHOLD:
            status = "warning"
        else:
            status = "healthy"

        last = self._entries[-1].timestamp if self._entries else None

        return BudgetState(
            total_budget=self._total,
            consumed=round(self._consumed, 6),
            remaining=round(self.remaining, 6),
            utilization_pct=round(utilization * 100, 2),
            entries_count=len(self._entries),
            last_consumption=last,
            projected_exhaustion=self._projected_exhaustion(),
            status=status,
            daily_rate=round(self._daily_rate(), 6),
        )

    def consumption_by_module(self) -> Dict[str, float]:
        """Break down consumption by module."""
        by_module: Dict[str, float] = {}
        for e in self._entries:
            if e.epsilon_consumed > 0:
                by_module[e.module] = by_module.get(e.module, 0.0) + e.epsilon_consumed
        return {k: round(v, 6) for k, v in by_module.items()}

    def consumption_by_day(self) -> Dict[str, float]:
        """Break down consumption by calendar day."""
        by_day: Dict[str, float] = {}
        for e in self._entries:
            if e.epsilon_consumed > 0:
                day = e.timestamp[:10]
                by_day[day] = by_day.get(day, 0.0) + e.epsilon_consumed
        return {k: round(v, 6) for k, v in sorted(by_day.items())}

    def save_ledger(self):
        """Save the full ledger to disk (append-only intent)."""
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)

        ledger = {
            "budget": {
                "total": self._total,
                "consumed": round(self._consumed, 6),
                "remaining": round(self.remaining, 6),
                "locked": self._locked,
                "status": self.state().status,
            },
            "entries": [{
                "entry_id": e.entry_id,
                "epsilon_consumed": e.epsilon_consumed,
                "module": e.module,
                "operation": e.operation,
                "timestamp": e.timestamp,
                "cumulative_epsilon": e.cumulative_epsilon,
                "k_achieved": e.k_achieved,
                "approved_by": e.approved_by,
            } for e in self._entries],
            "by_module": self.consumption_by_module(),
            "saved_at": self._now(),
        }

        with open(self._ledger_path, "w") as f:
            json.dump(ledger, f, indent=2)

    def load_ledger(self):
        """Load existing ledger state (for resuming across sessions)."""
        if not self._ledger_path.exists():
            return

        with open(self._ledger_path) as f:
            data = json.load(f)

        budget = data.get("budget", {})
        self._consumed = budget.get("consumed", 0.0)
        self._locked = budget.get("locked", False)
        self._total = budget.get("total", EPSILON_TOTAL_BUDGET)

        self._entries = []
        for e in data.get("entries", []):
            self._entries.append(BudgetEntry(
                entry_id=e["entry_id"],
                epsilon_consumed=e["epsilon_consumed"],
                module=e["module"],
                operation=e["operation"],
                timestamp=e["timestamp"],
                cumulative_epsilon=e["cumulative_epsilon"],
                k_achieved=e["k_achieved"],
                approved_by=e["approved_by"],
            ))
        self._counter = len(self._entries)

    # -- Advanced composition (for reference / future activation) --

    @staticmethod
    def advanced_composition_bound(n_queries: int, epsilon_per: float,
                                    delta: float = DELTA) -> float:
        """
        Compute the advanced composition bound (Dwork et al. 2010).

        Total privacy loss after n queries each with epsilon_per:
          epsilon_total <= sqrt(2n * ln(1/delta)) * epsilon_per + n * epsilon_per * (e^epsilon_per - 1)

        This is tighter than basic composition (n * epsilon_per) for large n.
        """
        term1 = math.sqrt(2 * n_queries * math.log(1.0 / delta)) * epsilon_per
        term2 = n_queries * epsilon_per * (math.exp(epsilon_per) - 1)
        return term1 + term2
