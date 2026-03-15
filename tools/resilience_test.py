#!/usr/bin/env python3
"""
proverb_stress_test.py — Seed #11: Proverb Stress Test Engine
Planted: 2026-03-13
Thermal delay: 14 days (T3 Wisdom/Wisdom tier)
Earliest ready: 2026-03-27

SIP says: "a pattern that fails under stress becomes an anomaly."

This engine re-applies ratified proverbs to new anomalies and measures
whether the proverb still holds. If a proverb consistently fails to
address new anomalies in its domain, it is flagged for administrator review.

A proverb "fails" when:
  1. An anomaly in the proverb's domain keeps recurring despite the proverb
  2. The proverb's remedy has been applied but the anomaly persists
  3. New anomalies emerge that contradict the proverb's wisdom

This is NOT auto-compost. Flagged proverbs go to administrator review.
Only administrator can compost a proverb.


Canon reference: Seed #11 spec


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional
from enum import Enum


class ProverbHealth(Enum):
    """Health status of a proverb under stress."""
    STRONG = "strong"       # Proverb holds — anomalies in its domain are declining
    STABLE = "stable"       # Proverb holds — no change in anomaly patterns
    STRESSED = "stressed"   # Proverb under pressure — anomalies in domain increasing
    FAILING = "failing"     # Proverb may be wrong — consistent contradictions found


@dataclass
class StressRecord:
    """One stress test application."""
    proverb_id: str
    anomaly_id: str
    felt_domain: str
    proverb_held: bool      # Did the proverb's wisdom apply to this anomaly?
    notes: str
    timestamp: str


@dataclass
class ProverbStressReport:
    """Stress report for a single proverb."""
    proverb_id: str
    proverb_text: str
    health: ProverbHealth
    tests_run: int
    tests_passed: int
    pass_rate: float
    recent_failures: List[str]  # anomaly IDs that contradicted the proverb
    recommendation: str


class ProverbStressTest:
    """
    Continuously stress-tests ratified proverbs against new anomalies.

    Usage:
        engine = ProverbStressTest()
        engine.register_proverb("P#0025", "Hurry carves ruts; patience builds roads.", "agency")
        engine.test("P#0025", "ANOM#0020", held=False, notes="System still fails to halt")
        report = engine.report("P#0025")
    """

    # Thresholds
    STRESS_THRESHOLD = 0.7   # Below 70% pass rate = STRESSED
    FAILURE_THRESHOLD = 0.4  # Below 40% pass rate = FAILING
    MIN_TESTS = 3            # Minimum tests before health assessment

    def __init__(self):
        self._proverbs: Dict[str, dict] = {}  # id -> {text, domain}
        self._records: Dict[str, List[StressRecord]] = {}  # proverb_id -> records

    def register_proverb(self, proverb_id: str, text: str, domain: str) -> None:
        """Register a proverb for stress testing."""
        self._proverbs[proverb_id] = {"text": text, "domain": domain}
        if proverb_id not in self._records:
            self._records[proverb_id] = []

    def test(self, proverb_id: str, anomaly_id: str,
             held: bool, notes: str = "") -> StressRecord:
        """
        Apply a proverb to an anomaly and record whether it held.

        held=True: The proverb's wisdom applies to this anomaly
        held=False: The anomaly contradicts or escapes the proverb
        """
        if proverb_id not in self._proverbs:
            raise ValueError(f"Proverb {proverb_id} not registered. Register first.")

        domain = self._proverbs[proverb_id]["domain"]
        record = StressRecord(
            proverb_id=proverb_id,
            anomaly_id=anomaly_id,
            felt_domain=domain,
            proverb_held=held,
            notes=notes,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._records[proverb_id].append(record)
        return record

    def assess_health(self, proverb_id: str) -> ProverbHealth:
        """Assess the health of a proverb based on its stress test history."""
        records = self._records.get(proverb_id, [])
        if len(records) < self.MIN_TESTS:
            return ProverbHealth.STABLE  # Not enough data

        pass_rate = sum(1 for r in records if r.proverb_held) / len(records)

        if pass_rate >= 0.9:
            return ProverbHealth.STRONG
        elif pass_rate >= self.STRESS_THRESHOLD:
            return ProverbHealth.STABLE
        elif pass_rate >= self.FAILURE_THRESHOLD:
            return ProverbHealth.STRESSED
        else:
            return ProverbHealth.FAILING

    def report(self, proverb_id: str) -> ProverbStressReport:
        """Generate a stress report for a single proverb."""
        if proverb_id not in self._proverbs:
            raise ValueError(f"Proverb {proverb_id} not registered.")

        proverb = self._proverbs[proverb_id]
        records = self._records.get(proverb_id, [])
        health = self.assess_health(proverb_id)

        tests_run = len(records)
        tests_passed = sum(1 for r in records if r.proverb_held)
        pass_rate = tests_passed / tests_run if tests_run > 0 else 1.0

        failures = [r.anomaly_id for r in records if not r.proverb_held]
        recent_failures = failures[-5:]  # Last 5 failures

        recommendations = {
            ProverbHealth.STRONG: "Proverb holds well. No action needed.",
            ProverbHealth.STABLE: "Proverb stable. Continue monitoring.",
            ProverbHealth.STRESSED: "Proverb under stress. Administrator should review whether domain has shifted.",
            ProverbHealth.FAILING: "STEWARD REVIEW REQUIRED. Proverb may need amendment or composting.",
        }

        return ProverbStressReport(
            proverb_id=proverb_id,
            proverb_text=proverb["text"],
            health=health,
            tests_run=tests_run,
            tests_passed=tests_passed,
            pass_rate=round(pass_rate, 4),
            recent_failures=recent_failures,
            recommendation=recommendations[health],
        )

    def report_all(self) -> List[ProverbStressReport]:
        """Generate stress reports for all registered proverbs."""
        return [self.report(pid) for pid in self._proverbs]

    def flagged(self) -> List[ProverbStressReport]:
        """Return only proverbs that need administrator attention."""
        return [r for r in self.report_all()
                if r.health in (ProverbHealth.STRESSED, ProverbHealth.FAILING)]

    @property
    def proverbs_count(self) -> int:
        return len(self._proverbs)

    @property
    def total_tests(self) -> int:
        return sum(len(records) for records in self._records.values())
