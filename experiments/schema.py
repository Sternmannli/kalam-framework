"""
schema.py — Experiment Data Collection Schema

Measures how system outputs change when interaction conditions change.
Supports A/B comparison between baseline and structured-framework conditions.

Tracks: token generation, noise percentage, efficiency (useful tokens per ms),
gate function score, and exchange count.

Dependencies: none (stdlib only)

Example:
    >>> cond_a = SessionCondition(gate_filter=False, pacing_active=False,
    ...     hard_constraints=False, output_rules=False)
    >>> cond_b = SessionCondition(gate_filter=True, pacing_active=True,
    ...     hard_constraints=True, output_rules=True)
    >>> run = ExperimentRun("RUN-001", cond_a, cond_b)
    >>> # Add measurements, then compare
    >>> result = compare(run)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class SessionCondition:
    """Defines the condition under which a session runs."""
    gate_filter: bool
    pacing_active: bool
    hard_constraints: bool
    output_rules: bool

    def label(self) -> str:
        if all([self.gate_filter, self.pacing_active,
                self.hard_constraints, self.output_rules]):
            return "FRAMEWORK_ON"
        if not any([self.gate_filter, self.pacing_active,
                    self.hard_constraints, self.output_rules]):
            return "FRAMEWORK_OFF"
        return "PARTIAL"


@dataclass
class SessionMeasurement:
    """A single measurement from one session."""
    condition: SessionCondition
    tokens_generated: int
    tokens_useful: int
    noise_percentage: float          # (generated - useful) / generated * 100
    energy_proxy_ms: float           # wall-clock time as energy proxy
    gate_score: float                # gate function score (0.0-1.0)
    exchange_count: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def efficiency(self) -> float:
        """Useful tokens per unit energy."""
        if self.energy_proxy_ms == 0:
            return 0.0
        return self.tokens_useful / self.energy_proxy_ms


@dataclass
class ComparisonResult:
    """Result of comparing condition A (baseline) vs condition B (with framework)."""
    noise_reduction_pct: float
    efficiency_gain_pct: float
    energy_delta_pct: float
    mean_gate_score_B: float
    sample_size_A: int
    sample_size_B: int

    def summary(self) -> str:
        return (
            f"Noise reduction: {self.noise_reduction_pct:+.1f}% | "
            f"Efficiency gain: {self.efficiency_gain_pct:+.1f}% | "
            f"Energy delta: {self.energy_delta_pct:+.1f}% | "
            f"Mean gate score (B): {self.mean_gate_score_B:.3f} | "
            f"Samples: A={self.sample_size_A}, B={self.sample_size_B}"
        )


@dataclass
class ExperimentRun:
    """One complete experiment run: A (baseline) vs B (with framework)."""
    run_id: str
    condition_A: SessionCondition
    condition_B: SessionCondition
    measurements_A: List[SessionMeasurement] = field(default_factory=list)
    measurements_B: List[SessionMeasurement] = field(default_factory=list)


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def compare(run: ExperimentRun) -> ComparisonResult:
    """Compare condition A vs condition B across all measurements in the run."""
    if not run.measurements_A or not run.measurements_B:
        raise ValueError("Both conditions need at least one measurement to compare.")

    noise_A = _mean([m.noise_percentage for m in run.measurements_A])
    noise_B = _mean([m.noise_percentage for m in run.measurements_B])

    eff_A = _mean([m.efficiency() for m in run.measurements_A])
    eff_B = _mean([m.efficiency() for m in run.measurements_B])

    energy_A = _mean([m.energy_proxy_ms for m in run.measurements_A])
    energy_B = _mean([m.energy_proxy_ms for m in run.measurements_B])

    gate_B = _mean([m.gate_score for m in run.measurements_B])

    noise_reduction = ((noise_A - noise_B) / noise_A * 100) if noise_A else 0.0
    efficiency_gain = ((eff_B - eff_A) / eff_A * 100) if eff_A else 0.0
    energy_delta = ((energy_B - energy_A) / energy_A * 100) if energy_A else 0.0

    return ComparisonResult(
        noise_reduction_pct=noise_reduction,
        efficiency_gain_pct=efficiency_gain,
        energy_delta_pct=energy_delta,
        mean_gate_score_B=gate_B,
        sample_size_A=len(run.measurements_A),
        sample_size_B=len(run.measurements_B),
    )


if __name__ == "__main__":
    cond_a = SessionCondition(gate_filter=False, pacing_active=False,
                              hard_constraints=False, output_rules=False)
    cond_b = SessionCondition(gate_filter=True, pacing_active=True,
                              hard_constraints=True, output_rules=True)

    run = ExperimentRun(run_id="RUN-001", condition_A=cond_a, condition_B=cond_b)

    for i in range(5):
        run.measurements_A.append(SessionMeasurement(
            condition=cond_a, tokens_generated=1000, tokens_useful=580,
            noise_percentage=42.0, energy_proxy_ms=3200.0,
            gate_score=0.0, exchange_count=12,
        ))

    for i in range(5):
        run.measurements_B.append(SessionMeasurement(
            condition=cond_b, tokens_generated=700, tokens_useful=620,
            noise_percentage=11.4, energy_proxy_ms=2100.0,
            gate_score=0.87, exchange_count=8,
        ))

    result = compare(run)
    print("Experiment Scaffold Run")
    print("=" * 60)
    print(f"Condition A: {cond_a.label()}")
    print(f"Condition B: {cond_b.label()}")
    print(result.summary())
    print("=" * 60)
    if result.noise_reduction_pct > 0 and result.energy_delta_pct < 0:
        print("SCAFFOLD RESULT: Consistent with hypothesis.")
    else:
        print("SCAFFOLD RESULT: Inconclusive — needs real data.")
