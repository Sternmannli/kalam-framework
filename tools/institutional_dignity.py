#!/usr/bin/env python3
"""
institutional_dignity.py — Seed #8: Institutional Dignity Score
Planted: 2026-03-13
Thermal delay: FROZEN (was 30 days, T2 Logic tier)

"A river that only measures its drops forgets its banks." — Axi

Individual dignity (D = A × L × M) measures one interaction.
Institutional dignity measures how an entire organization treats
people across all its interactions. This is the bridge from
individual to institutional deployment.

The Institutional Dignity Score (IDS) aggregates:
- Individual D scores across all exchanges
- Variance penalty (high variance = inconsistent treatment)
- Worst-case floor (the weakest experience defines the institution)
- Trend direction (improving or degrading?)

Needed for: kalam.ch institutional pricing, Layer 2 of PLAN-001


             T#18 (Fair Weight), T#47 (Phase Transition Physics)
Canon reference: Seed #8 spec, GAP#004 (collective dignity)


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import math


@dataclass
class InstitutionProfile:
    """An institution being evaluated."""
    institution_id: str
    name: str
    sector: str = ""
    exchanges_count: int = 0
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "institution_id": self.institution_id,
            "name": self.name,
            "sector": self.sector,
            "exchanges_count": self.exchanges_count,
        }


@dataclass
class IDSScore:
    """Institutional Dignity Score — one evaluation."""
    institution_id: str
    mean_D: float           # Average dignity across exchanges
    variance: float         # Variance of D scores
    floor_D: float          # Worst-case D score
    trend: float            # Positive = improving, negative = degrading
    IDS: float              # Composite score
    exchange_count: int
    timestamp: str
    grade: str = ""         # A, B, C, D, F

    def to_dict(self) -> dict:
        return {
            "institution_id": self.institution_id,
            "IDS": round(self.IDS, 4),
            "mean_D": round(self.mean_D, 4),
            "variance": round(self.variance, 6),
            "floor_D": round(self.floor_D, 4),
            "trend": round(self.trend, 4),
            "grade": self.grade,
            "exchange_count": self.exchange_count,
        }


class InstitutionalDignity:
    """
    Measures dignity at the institutional level.

    IDS = mean_D × (1 - variance_penalty) × floor_weight

    Where:
    - mean_D: average of all individual D scores
    - variance_penalty: penalizes inconsistent treatment
    - floor_weight: the worst experience pulls the score down
    - trend adjusts the grade (improving institutions get benefit of doubt)

    Usage:
        ids = InstitutionalDignity()
        ids.register("INST-001", "Hospital Alpha", sector="healthcare")
        ids.record_exchange("INST-001", D=0.85)
        ids.record_exchange("INST-001", D=0.92)
        ids.record_exchange("INST-001", D=0.10)  # One bad experience
        score = ids.evaluate("INST-001")
    """

    # Grade thresholds
    GRADE_A = 0.85
    GRADE_B = 0.70
    GRADE_C = 0.55
    GRADE_D = 0.40

    # Variance penalty coefficient
    VARIANCE_PENALTY_K = 2.0

    # Floor weight — how much the worst case matters
    FLOOR_WEIGHT = 0.3

    def __init__(self):
        self._institutions: Dict[str, InstitutionProfile] = {}
        self._scores: Dict[str, List[float]] = {}  # institution_id -> [D scores]
        self._evaluations: List[IDSScore] = []

    def register(self, institution_id: str, name: str,
                 sector: str = "") -> InstitutionProfile:
        """Register an institution for evaluation."""
        profile = InstitutionProfile(
            institution_id=institution_id,
            name=name,
            sector=sector,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._institutions[institution_id] = profile
        self._scores[institution_id] = []
        return profile

    def record_exchange(self, institution_id: str, D: float) -> bool:
        """Record an individual dignity score for this institution."""
        if institution_id not in self._scores:
            return False
        self._scores[institution_id].append(max(0.0, min(1.0, D)))
        if institution_id in self._institutions:
            self._institutions[institution_id].exchanges_count += 1
        return True

    def evaluate(self, institution_id: str) -> Optional[IDSScore]:
        """Evaluate an institution's dignity score."""
        scores = self._scores.get(institution_id)
        if not scores or len(scores) < 3:
            return None  # Need minimum data

        n = len(scores)
        mean_D = sum(scores) / n
        variance = sum((s - mean_D) ** 2 for s in scores) / n
        floor_D = min(scores)

        # Variance penalty: high variance = inconsistent treatment
        variance_penalty = min(1.0, self.VARIANCE_PENALTY_K * math.sqrt(variance))

        # Floor weight: worst experience pulls score down
        floor_component = floor_D * self.FLOOR_WEIGHT

        # IDS = (mean × (1 - penalty) × (1 - floor_weight)) + floor_component
        IDS = mean_D * (1 - variance_penalty) * (1 - self.FLOOR_WEIGHT) + floor_component

        # Trend: compare recent half to older half
        mid = n // 2
        if mid > 0:
            old_avg = sum(scores[:mid]) / mid
            new_avg = sum(scores[mid:]) / (n - mid)
            trend = new_avg - old_avg
        else:
            trend = 0.0

        # Grade
        grade = self._grade(IDS, trend)

        result = IDSScore(
            institution_id=institution_id,
            mean_D=mean_D,
            variance=variance,
            floor_D=floor_D,
            trend=trend,
            IDS=max(0.0, min(1.0, IDS)),
            exchange_count=n,
            timestamp=datetime.now(timezone.utc).isoformat(),
            grade=grade,
        )
        self._evaluations.append(result)
        return result

    def _grade(self, IDS: float, trend: float) -> str:
        """Assign letter grade with trend consideration."""
        # Slight boost for improving institutions
        adjusted = IDS + (0.02 if trend > 0.05 else 0)
        if adjusted >= self.GRADE_A:
            return "A"
        elif adjusted >= self.GRADE_B:
            return "B"
        elif adjusted >= self.GRADE_C:
            return "C"
        elif adjusted >= self.GRADE_D:
            return "D"
        return "F"

    @property
    def institutions_count(self) -> int:
        return len(self._institutions)

    @property
    def evaluations_count(self) -> int:
        return len(self._evaluations)

    def report(self) -> dict:
        """Institutional dignity health report."""
        return {
            "institutions": self.institutions_count,
            "evaluations": self.evaluations_count,
            "grades": {e.institution_id: e.grade for e in self._evaluations[-10:]},
        }
