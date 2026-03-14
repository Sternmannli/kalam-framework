#!/usr/bin/env python3
"""
drift_detector.py — Early Warning System for Metric Drift

Tracks a score over time and detects downward trends before collapse.
Uses sliding-window rate-of-change (dS/dt) with configurable thresholds.

The difference between archival and preventive monitoring:
  - Archival tells you "score failed" (reactive)
  - Drift tells you "score is falling" (preventive)

Alert levels: STABLE, DECLINING, CRITICAL

Dependencies: none (stdlib only)

Example:
    >>> drift = DriftDetector()
    >>> for score in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
    ...     drift.record(score, f"EX-{score}")
    >>> alert = drift.check()
    >>> alert.level
    <DriftLevel.DECLINING: 'declining'>
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from enum import Enum


class DriftLevel(Enum):
    """How fast is the score falling?"""
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"


@dataclass
class DriftReading:
    """A single measurement in time."""
    score: float
    timestamp: str
    exchange_id: str
    domain: str = ""


@dataclass
class DriftAlert:
    """Alert when score is falling."""
    level: DriftLevel
    rate: float                   # rate of change (negative = falling)
    current_score: float
    window_size: int
    trend_readings: int           # consecutive declines
    message: str
    timestamp: str
    recommended_action: str


@dataclass
class DriftState:
    """Full state of the drift detector."""
    level: DriftLevel
    current_score: float
    rate: float
    readings_count: int
    consecutive_declines: int
    alert_history: List[DriftAlert] = field(default_factory=list)


class DriftDetector:
    """
    Tracks scores over time and detects downward trends.

    Usage:
        drift = DriftDetector()
        drift.record(1.0, "EX-001")
        alert = drift.check()
        if alert.level == DriftLevel.CRITICAL:
            # pause and review
    """

    WINDOW_SIZE = 10
    DECLINE_THRESHOLD = -0.1
    CRITICAL_THRESHOLD = -0.3
    CONSECUTIVE_ALERT = 3
    CRITICAL_CONSECUTIVE = 5
    NEAR_ZERO = 0.2

    def __init__(self):
        self._readings: List[DriftReading] = []
        self._alerts: List[DriftAlert] = []
        self._consecutive_declines = 0

    def record(self, score: float, exchange_id: str, domain: str = "") -> None:
        """Record a score measurement."""
        reading = DriftReading(
            score=score,
            timestamp=datetime.now(timezone.utc).isoformat(),
            exchange_id=exchange_id,
            domain=domain,
        )
        self._readings.append(reading)

        if len(self._readings) >= 2:
            prev = self._readings[-2].score
            if score < prev:
                self._consecutive_declines += 1
            else:
                self._consecutive_declines = 0

    def check(self) -> DriftAlert:
        """
        Check current drift state and return an alert.
        Computes rate of change over the sliding window.
        """
        now = datetime.now(timezone.utc).isoformat()

        if len(self._readings) < 2:
            return DriftAlert(
                level=DriftLevel.STABLE,
                rate=0.0,
                current_score=self._readings[-1].score if self._readings else 1.0,
                window_size=len(self._readings),
                trend_readings=0,
                message="Insufficient data for drift detection.",
                timestamp=now,
                recommended_action="Continue monitoring.",
            )

        window = self._readings[-self.WINDOW_SIZE:]
        current = window[-1].score
        rate = self._compute_rate(window)
        level = self._classify(rate, current)
        message, action = self._build_message(level, rate, current)

        alert = DriftAlert(
            level=level, rate=round(rate, 4), current_score=current,
            window_size=len(window), trend_readings=self._consecutive_declines,
            message=message, timestamp=now, recommended_action=action,
        )

        if level != DriftLevel.STABLE:
            self._alerts.append(alert)

        return alert

    def _compute_rate(self, window: List[DriftReading]) -> float:
        if len(window) < 2:
            return 0.0
        n = len(window)
        return (window[-1].score - window[0].score) / (n - 1)

    def _classify(self, rate: float, current: float) -> DriftLevel:
        if current <= self.NEAR_ZERO and rate < 0:
            return DriftLevel.CRITICAL
        if rate <= self.CRITICAL_THRESHOLD:
            return DriftLevel.CRITICAL
        if rate <= self.DECLINE_THRESHOLD:
            return DriftLevel.DECLINING
        if self._consecutive_declines >= self.CRITICAL_CONSECUTIVE:
            return DriftLevel.CRITICAL
        if self._consecutive_declines >= self.CONSECUTIVE_ALERT:
            return DriftLevel.DECLINING
        return DriftLevel.STABLE

    def _build_message(self, level, rate, current):
        if level == DriftLevel.STABLE:
            return ("Scores stable. No drift detected.", "Continue monitoring.")
        elif level == DriftLevel.DECLINING:
            return (
                f"Score declining: rate={rate:.4f}, current={current:.2f}. "
                f"{self._consecutive_declines} consecutive declines.",
                "Review recent interactions for emerging patterns."
            )
        else:
            return (
                f"CRITICAL drift: rate={rate:.4f}, current={current:.2f}. "
                f"{self._consecutive_declines} consecutive declines. Collapse imminent.",
                "PAUSE recommended. Review immediately."
            )

    def state(self) -> DriftState:
        """Return full detector state."""
        current = self._readings[-1].score if self._readings else 1.0
        rate = 0.0
        if len(self._readings) >= 2:
            window = self._readings[-self.WINDOW_SIZE:]
            rate = self._compute_rate(window)
        level = self._classify(rate, current) if self._readings else DriftLevel.STABLE

        return DriftState(
            level=level, current_score=current, rate=round(rate, 4),
            readings_count=len(self._readings),
            consecutive_declines=self._consecutive_declines,
            alert_history=list(self._alerts),
        )

    def reset(self) -> None:
        """Reset detector."""
        self._readings.clear()
        self._alerts.clear()
        self._consecutive_declines = 0

    @property
    def readings_count(self) -> int:
        return len(self._readings)

    @property
    def alert_count(self) -> int:
        return len(self._alerts)
