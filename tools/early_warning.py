#!/usr/bin/env python3
"""
early_warning.py -- Early-warning shadow pipeline for metric drift detection.
Implements EWMA and CUSUM change-point detectors with a simulation harness
for calibration.

Version: 1.0

This module implements:
  1. EWMA (Exponentially Weighted Moving Average) drift detector
  2. CUSUM (Cumulative Sum) change-point detector
  3. Simulation harness for synthetic trajectories
  4. Triage pipeline with human gate (simulation-only toggle)
  5. Shadow mode -- runs in parallel, never touches live subjects

The pipeline detects metric drift on synthetic and seeded real-like
trajectories with measurable lead time, false positive rate, and
clear triage escalation rules.

Integration:
  - Reads from DriftDetector (drift_detector.py) for real-time dS/dt
  - Produces triage alerts for administrator review
"""

import math
import json
import random
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Tuple
from enum import Enum
from pathlib import Path

from tools.drift_detector import DriftDetector, DriftLevel, DriftAlert


# ===================================================
# CONFIGURATION
# ===================================================

SHADOW_DIR = Path(__file__).parent.parent / "SHADOW_PIPELINE"
TRIAGE_LOG = SHADOW_DIR / "triage_log.json"
SIMULATION_LOG = SHADOW_DIR / "simulation_log.json"


class AlertSeverity(Enum):
    """Triage severity levels."""
    CLEAR = "clear"
    WATCH = "watch"
    WARN = "warn"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PipelineMode(Enum):
    """Pipeline operating mode."""
    SIMULATION = "simulation"   # Synthetic data only -- no privacy cost
    SHADOW = "shadow"           # Runs on real data in shadow -- no actions taken
    LIVE = "live"               # Active intervention (requires administrator unlock)


# ===================================================
# EWMA DETECTOR
# ===================================================

@dataclass
class EWMAState:
    """State of the EWMA detector."""
    current_ewma: float
    alpha: float              # Smoothing factor (0 < alpha < 1)
    readings: int
    baseline: float           # Expected mean under stable conditions
    ucl: float                # Upper control limit
    lcl: float                # Lower control limit
    breached: bool


class EWMADetector:
    """
    Exponentially Weighted Moving Average detector.

    Smooths metric scores and detects when the smoothed average
    drifts below control limits. More responsive to recent changes
    than a simple moving average.

    EWMA_t = alpha * D_t + (1 - alpha) * EWMA_{t-1}

    Control limits:
      UCL = mu_0 + L * sigma * sqrt(alpha / (2 - alpha))
      LCL = mu_0 - L * sigma * sqrt(alpha / (2 - alpha))

    where L is the width parameter (typically 2.5-3.0).
    """

    def __init__(self, alpha: float = 0.2, baseline: float = 1.0,
                 sigma: float = 0.15, L: float = 2.7):
        self._alpha = alpha
        self._baseline = baseline
        self._sigma = sigma
        self._L = L
        self._ewma = baseline
        self._readings = 0

        # Control limits
        factor = math.sqrt(alpha / (2.0 - alpha))
        self._ucl = baseline + L * sigma * factor
        self._lcl = baseline - L * sigma * factor

    def update(self, D: float) -> EWMAState:
        """Update EWMA with a new score."""
        self._readings += 1
        self._ewma = self._alpha * D + (1.0 - self._alpha) * self._ewma
        breached = self._ewma < self._lcl

        return EWMAState(
            current_ewma=round(self._ewma, 4),
            alpha=self._alpha,
            readings=self._readings,
            baseline=self._baseline,
            ucl=round(self._ucl, 4),
            lcl=round(self._lcl, 4),
            breached=breached,
        )

    def reset(self):
        self._ewma = self._baseline
        self._readings = 0

    @property
    def state(self) -> EWMAState:
        return EWMAState(
            current_ewma=round(self._ewma, 4),
            alpha=self._alpha,
            readings=self._readings,
            baseline=self._baseline,
            ucl=round(self._ucl, 4),
            lcl=round(self._lcl, 4),
            breached=self._ewma < self._lcl,
        )


# ===================================================
# CUSUM DETECTOR
# ===================================================

@dataclass
class CUSUMState:
    """State of the CUSUM detector."""
    S_high: float             # Cumulative sum for upward shifts
    S_low: float              # Cumulative sum for downward shifts
    threshold_h: float        # Decision threshold
    allowance_k: float        # Slack / allowance
    readings: int
    alarm: bool               # True if either cumsum exceeds threshold
    alarm_direction: str      # "up", "down", or "none"


class CUSUMDetector:
    """
    Cumulative Sum (CUSUM) change-point detector.

    Detects shifts in mean score.
    Sensitive to small, persistent shifts -- exactly what metric
    drift looks like (not a crash, but a slow fade).

    S_high_t = max(0, S_high_{t-1} + (D_t - mu_0 - k))
    S_low_t  = max(0, S_low_{t-1}  + (mu_0 - k - D_t))

    Alarm when S_high > h or S_low > h.
    """

    def __init__(self, target_mean: float = 1.0, allowance_k: float = 0.05,
                 threshold_h: float = 0.5):
        self._mu0 = target_mean
        self._k = allowance_k
        self._h = threshold_h
        self._S_high = 0.0
        self._S_low = 0.0
        self._readings = 0

    def update(self, D: float) -> CUSUMState:
        """Update CUSUM with a new score."""
        self._readings += 1
        self._S_high = max(0.0, self._S_high + (D - self._mu0 - self._k))
        self._S_low = max(0.0, self._S_low + (self._mu0 - self._k - D))

        alarm = self._S_high > self._h or self._S_low > self._h
        direction = "none"
        if self._S_high > self._h:
            direction = "up"
        if self._S_low > self._h:
            direction = "down"

        return CUSUMState(
            S_high=round(self._S_high, 4),
            S_low=round(self._S_low, 4),
            threshold_h=self._h,
            allowance_k=self._k,
            readings=self._readings,
            alarm=alarm,
            alarm_direction=direction,
        )

    def reset(self):
        self._S_high = 0.0
        self._S_low = 0.0
        self._readings = 0

    @property
    def state(self) -> CUSUMState:
        return CUSUMState(
            S_high=round(self._S_high, 4),
            S_low=round(self._S_low, 4),
            threshold_h=self._h,
            allowance_k=self._k,
            readings=self._readings,
            alarm=self._S_high > self._h or self._S_low > self._h,
            alarm_direction="down" if self._S_low > self._h else ("up" if self._S_high > self._h else "none"),
        )


# ===================================================
# SIMULATION HARNESS
# ===================================================

@dataclass
class SimulatedTrajectory:
    """A synthetic score trajectory for testing."""
    trajectory_id: str
    label: str                  # "healthy", "slow_decline", "sudden_crash", "recovery", "oscillating"
    domain: str
    scores: List[float]
    description: str


class SimulationHarness:
    """
    Generates synthetic trajectories for testing the early-warning
    pipeline without touching real subject data.

    Trajectory types:
      1. healthy        -- stable high score, minor noise
      2. slow_decline   -- gradual erosion (the hard one to catch)
      3. sudden_crash   -- abrupt score collapse
      4. recovery       -- decline followed by restoration
      5. oscillating    -- unstable, no clear trend
      6. structural     -- multiple entities declining in sync
    """

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"SIM-{self._counter:04d}"

    def healthy(self, n: int = 30, domain: str = "general") -> SimulatedTrajectory:
        """Stable high score with minor noise."""
        scores = [min(1.0, max(0.0, 0.9 + self._rng.gauss(0, 0.03))) for _ in range(n)]
        return SimulatedTrajectory(
            trajectory_id=self._next_id(),
            label="healthy",
            domain=domain,
            scores=scores,
            description="Stable metric. Minor noise. No intervention needed.",
        )

    def slow_decline(self, n: int = 30, domain: str = "family") -> SimulatedTrajectory:
        """Gradual erosion -- the hardest to detect early."""
        base = 0.95
        scores = []
        for i in range(n):
            base -= self._rng.uniform(0.005, 0.02)
            noise = self._rng.gauss(0, 0.02)
            scores.append(min(1.0, max(0.0, base + noise)))
        return SimulatedTrajectory(
            trajectory_id=self._next_id(),
            label="slow_decline",
            domain=domain,
            scores=scores,
            description="Gradual metric erosion. Subtle. The system must catch this.",
        )

    def sudden_crash(self, n: int = 30, crash_at: int = 15,
                     domain: str = "work") -> SimulatedTrajectory:
        """Abrupt collapse -- easier to detect but must be fast."""
        scores = []
        for i in range(n):
            if i < crash_at:
                scores.append(min(1.0, max(0.0, 0.85 + self._rng.gauss(0, 0.03))))
            else:
                scores.append(min(1.0, max(0.0, 0.15 + self._rng.gauss(0, 0.05))))
        return SimulatedTrajectory(
            trajectory_id=self._next_id(),
            label="sudden_crash",
            domain=domain,
            scores=scores,
            description="Abrupt metric collapse. Must detect within 2-3 readings.",
        )

    def recovery(self, n: int = 40, domain: str = "faith") -> SimulatedTrajectory:
        """Decline followed by restoration -- tests false-alarm suppression."""
        scores = []
        for i in range(n):
            if i < 15:
                scores.append(min(1.0, max(0.0, 0.9 - i * 0.03 + self._rng.gauss(0, 0.02))))
            elif i < 25:
                base = 0.45 + (i - 15) * 0.04
                scores.append(min(1.0, max(0.0, base + self._rng.gauss(0, 0.02))))
            else:
                scores.append(min(1.0, max(0.0, 0.85 + self._rng.gauss(0, 0.03))))
        return SimulatedTrajectory(
            trajectory_id=self._next_id(),
            label="recovery",
            domain=domain,
            scores=scores,
            description="Decline then recovery. Tests that alerts resolve.",
        )

    def oscillating(self, n: int = 30, domain: str = "community") -> SimulatedTrajectory:
        """Unstable, no clear trend -- tests noise tolerance."""
        scores = []
        for i in range(n):
            base = 0.6 + 0.3 * math.sin(i * 0.4) + self._rng.gauss(0, 0.08)
            scores.append(min(1.0, max(0.0, base)))
        return SimulatedTrajectory(
            trajectory_id=self._next_id(),
            label="oscillating",
            domain=domain,
            scores=scores,
            description="Oscillating metric. No clear trend. Should not trigger.",
        )

    def structural_cohort(self, n_entities: int = 10, n_steps: int = 20,
                          domain: str = "work") -> List[SimulatedTrajectory]:
        """Multiple entities declining in sync -- structural harm signal."""
        trajectories = []
        for d in range(n_entities):
            base = 0.9
            scores = []
            for i in range(n_steps):
                base -= self._rng.uniform(0.01, 0.025)
                noise = self._rng.gauss(0, 0.03)
                scores.append(min(1.0, max(0.0, base + noise)))
            trajectories.append(SimulatedTrajectory(
                trajectory_id=self._next_id(),
                label="structural",
                domain=domain,
                scores=scores,
                description=f"Structural drift -- entity {d+1}/{n_entities} in sync decline.",
            ))
        return trajectories

    def full_suite(self) -> List[SimulatedTrajectory]:
        """Generate one of each trajectory type."""
        suite = [
            self.healthy(),
            self.slow_decline(),
            self.sudden_crash(),
            self.recovery(),
            self.oscillating(),
        ]
        suite.extend(self.structural_cohort(n_entities=8))
        return suite


# ===================================================
# TRIAGE PIPELINE
# ===================================================

@dataclass
class TriageAlert:
    """A triage alert for administrator review."""
    alert_id: str
    trajectory_id: str
    severity: AlertSeverity
    detector: str              # "ewma", "cusum", "drift"
    lead_time_steps: int       # How many steps before D=0 was the alert raised?
    current_D: float
    dD_dt: float
    message: str
    recommended_action: str
    timestamp: str
    simulation_only: bool      # True = no privacy budget consumed


@dataclass
class PipelineResult:
    """Result of running the pipeline on a trajectory."""
    trajectory_id: str
    label: str
    alerts: List[TriageAlert]
    ewma_final: EWMAState
    cusum_final: CUSUMState
    drift_final: DriftLevel
    first_alert_step: int      # -1 if no alert
    total_steps: int
    lead_time: int             # steps between first alert and minimum D
    false_positive: bool       # True if alert on healthy trajectory
    detected: bool             # True if decline was caught before D < 0.3


class EarlyWarningPipeline:
    """
    The shadow pipeline. Runs detectors in parallel on each trajectory.

    For each score reading:
      1. EWMA update -> check breach
      2. CUSUM update -> check alarm
      3. DriftDetector record -> check level
      4. Triage -> produce alert if any detector fires

    Simulation-only mode prevents any privacy budget consumption.
    """

    def __init__(self, mode: PipelineMode = PipelineMode.SIMULATION):
        self._mode = mode
        self._results: List[PipelineResult] = []
        self._alerts: List[TriageAlert] = []
        self._alert_counter = 0

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _next_alert_id(self) -> str:
        self._alert_counter += 1
        return f"TRIAGE-{self._alert_counter:04d}"

    def run_trajectory(self, trajectory: SimulatedTrajectory) -> PipelineResult:
        """
        Run the full pipeline on a single trajectory.

        Returns metrics: detection time, lead time, false positive status.
        """
        ewma = EWMADetector(alpha=0.2, baseline=1.0, sigma=0.15, L=2.7)
        cusum = CUSUMDetector(target_mean=1.0, allowance_k=0.05, threshold_h=0.5)
        drift = DriftDetector()

        alerts = []
        first_alert_step = -1
        min_D = 1.0
        min_D_step = 0

        for step, D in enumerate(trajectory.scores):
            # Track minimum
            if D < min_D:
                min_D = D
                min_D_step = step

            # Run detectors
            ewma_state = ewma.update(D)
            cusum_state = cusum.update(D)
            drift.record(D, f"SIM-EX-{step:04d}", trajectory.domain)
            drift_alert = drift.check()

            # Triage: any detector firing?
            fired = []
            if ewma_state.breached:
                fired.append("ewma")
            if cusum_state.alarm and cusum_state.alarm_direction == "down":
                fired.append("cusum")
            if drift_alert.level in (DriftLevel.DECLINING, DriftLevel.CRITICAL):
                fired.append("drift")

            if fired:
                if first_alert_step == -1:
                    first_alert_step = step

                severity = self._classify_severity(ewma_state, cusum_state, drift_alert)

                # Compute dD/dt
                dD_dt = 0.0
                if step > 0:
                    dD_dt = D - trajectory.scores[step - 1]

                alert = TriageAlert(
                    alert_id=self._next_alert_id(),
                    trajectory_id=trajectory.trajectory_id,
                    severity=severity,
                    detector="+".join(fired),
                    lead_time_steps=0,  # Computed after loop
                    current_D=round(D, 4),
                    dD_dt=round(dD_dt, 4),
                    message=self._build_triage_message(severity, fired, D, trajectory.domain),
                    recommended_action=self._recommend_action(severity),
                    timestamp=self._now(),
                    simulation_only=(self._mode == PipelineMode.SIMULATION),
                )
                alerts.append(alert)
                self._alerts.append(alert)

        # Compute lead time: steps between first alert and minimum D
        lead_time = max(0, min_D_step - first_alert_step) if first_alert_step >= 0 else 0

        # Update lead_time in first alert
        if alerts:
            alerts[0].lead_time_steps = lead_time

        # Is this a false positive?
        false_positive = (trajectory.label == "healthy" and len(alerts) > 0)

        # Was decline detected before D < 0.3?
        detected = (first_alert_step >= 0 and first_alert_step < min_D_step) if min_D < 0.3 else (first_alert_step >= 0)

        drift_state = drift.state()
        result = PipelineResult(
            trajectory_id=trajectory.trajectory_id,
            label=trajectory.label,
            alerts=alerts,
            ewma_final=ewma.state,
            cusum_final=cusum.state,
            drift_final=drift_state.level,
            first_alert_step=first_alert_step,
            total_steps=len(trajectory.scores),
            lead_time=lead_time,
            false_positive=false_positive,
            detected=detected,
        )
        self._results.append(result)
        return result

    def run_suite(self, trajectories: List[SimulatedTrajectory]) -> List[PipelineResult]:
        """Run pipeline on a full suite of trajectories."""
        return [self.run_trajectory(t) for t in trajectories]

    def _classify_severity(self, ewma: EWMAState, cusum: CUSUMState,
                           drift: DriftAlert) -> AlertSeverity:
        """Classify triage severity from detector outputs."""
        detectors_firing = 0
        if ewma.breached:
            detectors_firing += 1
        if cusum.alarm:
            detectors_firing += 1
        if drift.level == DriftLevel.CRITICAL:
            detectors_firing += 2
        elif drift.level == DriftLevel.DECLINING:
            detectors_firing += 1

        if detectors_firing >= 4:
            return AlertSeverity.EMERGENCY
        if detectors_firing >= 3:
            return AlertSeverity.CRITICAL
        if detectors_firing >= 2:
            return AlertSeverity.WARN
        if detectors_firing >= 1:
            return AlertSeverity.WATCH
        return AlertSeverity.CLEAR

    def _build_triage_message(self, severity: AlertSeverity, detectors: List[str],
                              current_D: float, domain: str) -> str:
        """Build human-readable triage message."""
        det_str = ", ".join(detectors)
        return (
            f"{severity.value.upper()}: Metric drift detected in domain '{domain}'. "
            f"Current D={current_D:.2f}. Detectors: [{det_str}]."
        )

    def _recommend_action(self, severity: AlertSeverity) -> str:
        """Recommend action based on severity."""
        actions = {
            AlertSeverity.CLEAR: "Continue monitoring.",
            AlertSeverity.WATCH: "Flag for next administrator review cycle.",
            AlertSeverity.WARN: "Administrator review within 48 hours. Examine recent interactions.",
            AlertSeverity.CRITICAL: "Immediate administrator review. Consider pausing interactions.",
            AlertSeverity.EMERGENCY: "PAUSE all interactions in this domain. Administrator and ethics review required.",
        }
        return actions[severity]

    # -- REPORTING --

    def summary(self) -> dict:
        """Summary statistics across all pipeline runs."""
        if not self._results:
            return {"status": "no runs yet"}

        total = len(self._results)
        detected = sum(1 for r in self._results if r.detected)
        false_pos = sum(1 for r in self._results if r.false_positive)
        avg_lead = 0.0
        lead_times = [r.lead_time for r in self._results if r.lead_time > 0]
        if lead_times:
            avg_lead = sum(lead_times) / len(lead_times)

        by_label = {}
        for r in self._results:
            if r.label not in by_label:
                by_label[r.label] = {"total": 0, "detected": 0, "alerts": 0}
            by_label[r.label]["total"] += 1
            if r.detected:
                by_label[r.label]["detected"] += 1
            by_label[r.label]["alerts"] += len(r.alerts)

        return {
            "total_trajectories": total,
            "detected": detected,
            "detection_rate": round(detected / total, 2) if total > 0 else 0,
            "false_positives": false_pos,
            "false_positive_rate": round(false_pos / total, 2) if total > 0 else 0,
            "average_lead_time_steps": round(avg_lead, 1),
            "total_alerts": len(self._alerts),
            "mode": self._mode.value,
            "by_label": by_label,
        }

    def save_results(self):
        """Save triage log and simulation results."""
        SHADOW_DIR.mkdir(parents=True, exist_ok=True)

        # Triage log
        triage_data = [{
            "alert_id": a.alert_id,
            "trajectory_id": a.trajectory_id,
            "severity": a.severity.value,
            "detector": a.detector,
            "lead_time_steps": a.lead_time_steps,
            "current_D": a.current_D,
            "dD_dt": a.dD_dt,
            "message": a.message,
            "recommended_action": a.recommended_action,
            "timestamp": a.timestamp,
            "simulation_only": a.simulation_only,
        } for a in self._alerts]

        with open(TRIAGE_LOG, "w") as f:
            json.dump(triage_data, f, indent=2)

        # Simulation summary
        with open(SIMULATION_LOG, "w") as f:
            json.dump(self.summary(), f, indent=2)


# ===================================================
# CLI / DEMO
# ===================================================

def demo():
    """Run the full early-warning pipeline demo."""
    print("=" * 65)
    print("EARLY-WARNING SHADOW PIPELINE -- SIMULATION RUN")
    print("=" * 65)

    # Generate trajectories
    harness = SimulationHarness(seed=42)
    suite = harness.full_suite()

    print(f"\nGenerated {len(suite)} trajectories:")
    for t in suite:
        print(f"  {t.trajectory_id} [{t.label}] -- {len(t.scores)} steps -- {t.domain}")

    # Run pipeline
    pipeline = EarlyWarningPipeline(mode=PipelineMode.SIMULATION)
    results = pipeline.run_suite(suite)

    # Results
    print("\n" + "-" * 65)
    print("RESULTS")
    print("-" * 65)

    for r in results:
        status = "DETECTED" if r.detected else ("FALSE POS" if r.false_positive else "MISSED")
        alert_str = f"first alert at step {r.first_alert_step}" if r.first_alert_step >= 0 else "no alerts"
        print(f"  {r.trajectory_id} [{r.label:15s}] -- {status:10s} -- {alert_str} -- lead_time={r.lead_time}")

    # Summary
    summary = pipeline.summary()
    print("\n" + "-" * 65)
    print("SUMMARY")
    print("-" * 65)
    print(f"  Detection rate:    {summary['detection_rate']:.0%}")
    print(f"  False positive rate: {summary['false_positive_rate']:.0%}")
    print(f"  Avg lead time:     {summary['average_lead_time_steps']:.1f} steps")
    print(f"  Total alerts:      {summary['total_alerts']}")
    print(f"  Mode:              {summary['mode']}")

    # Save
    pipeline.save_results()
    print(f"\n  Triage log saved to: {TRIAGE_LOG}")
    print(f"  Simulation log saved to: {SIMULATION_LOG}")

    print("\n" + "=" * 65)
    print("Shadow pipeline operational. No live subjects touched. No privacy budget consumed.")
    print("=" * 65)


if __name__ == "__main__":
    demo()
