#!/usr/bin/env python3
"""
agency_amplifier.py — Seed #12: Agency Amplifier (Penguin Pulse)
Planted: 2026-03-13
Thermal delay: 7 days (T4 Interface tier)
Earliest ready: 2026-03-20

Extends agency (A) from binary to graded measurement.
D = A × L × M — if A is binary, dignity is binary.
This module makes A a real number in [0, 1] by measuring four sub-dimensions:

  A = (V + F + C + U) / 4

  V = Visibility    — can the person SEE what the system decided?
  F = Affordability — can the person ACCESS recourse without unreasonable cost?
  C = Controllability — can the person CHANGE the outcome?
  U = Understandability — can the person UNDERSTAND why the decision was made?

Each sub-dimension is scored [0, 1]. Agency is the mean.
If any sub-dimension is 0, agency collapses (non-compensatory, matching D).


Canon reference: Seed #12 spec, T#47 (Phase Transition Physics)


"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AgencyScore:
    """Multidimensional agency measurement."""
    visibility: float       # V: can they see the decision?
    affordability: float    # F: can they access recourse?
    controllability: float  # C: can they change the outcome?
    understandability: float  # U: can they understand why?
    exchange_id: str
    timestamp: str
    notes: str = ""

    @property
    def A(self) -> float:
        """
        Composite agency score.
        Non-compensatory: any zero collapses A to zero.
        """
        dims = [self.visibility, self.affordability,
                self.controllability, self.understandability]
        if any(d == 0.0 for d in dims):
            return 0.0
        return sum(dims) / len(dims)

    @property
    def weakest(self) -> str:
        """Return the name of the weakest sub-dimension."""
        dims = {
            "visibility": self.visibility,
            "affordability": self.affordability,
            "controllability": self.controllability,
            "understandability": self.understandability,
        }
        return min(dims, key=dims.get)

    @property
    def is_collapsed(self) -> bool:
        """True if any sub-dimension is zero."""
        return self.A == 0.0

    def to_dict(self) -> dict:
        return {
            "V": self.visibility,
            "F": self.affordability,
            "C": self.controllability,
            "U": self.understandability,
            "A": round(self.A, 4),
            "weakest": self.weakest,
            "collapsed": self.is_collapsed,
            "exchange_id": self.exchange_id,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }


class AgencyAmplifier:
    """
    Tracks agency scores over time and identifies systemic weakness.

    The amplifier doesn't just measure — it recommends where to
    invest to raise agency most efficiently (weakest-voice-first
    applied to sub-dimensions).

    Usage:
        amp = AgencyAmplifier()
        score = amp.measure("EX-001", V=0.8, F=0.3, C=0.7, U=0.9)
        report = amp.report()
    """

    def __init__(self):
        self._scores: List[AgencyScore] = []

    def measure(self, exchange_id: str,
                V: float, F: float, C: float, U: float,
                notes: str = "") -> AgencyScore:
        """Record an agency measurement for an exchange."""
        # Clamp to [0, 1]
        V = max(0.0, min(1.0, V))
        F = max(0.0, min(1.0, F))
        C = max(0.0, min(1.0, C))
        U = max(0.0, min(1.0, U))

        score = AgencyScore(
            visibility=V,
            affordability=F,
            controllability=C,
            understandability=U,
            exchange_id=exchange_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )
        self._scores.append(score)
        return score

    def report(self) -> dict:
        """
        Generate an agency report across all measurements.
        Identifies systemic weaknesses using weakest-voice-first.
        """
        if not self._scores:
            return {"status": "no_data", "message": "No agency measurements recorded."}

        n = len(self._scores)
        avg_V = sum(s.visibility for s in self._scores) / n
        avg_F = sum(s.affordability for s in self._scores) / n
        avg_C = sum(s.controllability for s in self._scores) / n
        avg_U = sum(s.understandability for s in self._scores) / n
        avg_A = sum(s.A for s in self._scores) / n
        collapses = sum(1 for s in self._scores if s.is_collapsed)

        # Weakest dimension across all measurements
        dim_avgs = {
            "visibility": avg_V,
            "affordability": avg_F,
            "controllability": avg_C,
            "understandability": avg_U,
        }
        systemic_weakness = min(dim_avgs, key=dim_avgs.get)

        # Recommendation: invest in the weakest
        recommendations = {
            "visibility": "Make system decisions more visible to the person.",
            "affordability": "Reduce the cost of recourse and appeal.",
            "controllability": "Give the person more control over outcomes.",
            "understandability": "Explain decisions in the person's language.",
        }

        return {
            "status": "ok",
            "measurements": n,
            "averages": {k: round(v, 4) for k, v in dim_avgs.items()},
            "avg_agency": round(avg_A, 4),
            "collapses": collapses,
            "collapse_rate": round(collapses / n, 4) if n > 0 else 0,
            "systemic_weakness": systemic_weakness,
            "recommendation": recommendations[systemic_weakness],
        }

    @property
    def scores_count(self) -> int:
        return len(self._scores)

    def reset(self) -> None:
        """Reset measurements (e.g., after administrator review)."""
        self._scores.clear()
