#!/usr/bin/env python3
"""
divergence_study.py — #TheDivergenceShadow: Systematic Scientific Study
Version: 1.0
Field Layer: Study


THE DIVERGENCE SHADOW
=====================
The systematic gap between what a system claims to do
and what it actually does — measured, tracked, and made visible.

Scientific Foundations (mapped to modules):
  1. KL/JS Divergence        → SemanticDivergenceDetector
  2. Specification Gaming     → SpecificationGamingDetector
  3. Mission Drift            → MissionDriftTracker
  4. CUSUM/EWMA              → Already in early_warning.py (extended here)
  5. Semantic Drift           → RuleSemanticDrift
  6. Principal-Agent Gap      → AgencyLossEstimator
  7. Goodhart Dynamics        → GoodhartDetector
  8. Normative Decay          → NormativeDecayModel

Each module implements:
  - A mathematical model grounded in published research
  - Detection thresholds with configurable sensitivity
  - Simulation harness for synthetic testing
  - Integration points with existing kalam systems

References:
  - Hamilton et al. (2016) "Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change"
  - Ebrahim, Battilana & Mair (2014) "Governance of Social Enterprises: Mission Drift"
  - Bruder (2025) "From Mission Drift to Practice Drift" Organization Studies
  - Page (1954) CUSUM — Biometrika
  - f-DPO (ICLR 2024) "Beyond Reverse KL: Generalizing DPO with Diverse Divergence Constraints"
  - Denison et al. (2024) Curriculum escalation in specification gaming
  - Goodhart's Law in RL (ICLR 2024)


"""

import math
import hashlib
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from pathlib import Path

import sys
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


# ═══════════════════════════════════════════════════════════
# MODULE 1: SEMANTIC DIVERGENCE DETECTOR (KL / JS Divergence)
# ═══════════════════════════════════════════════════════════
#
# Grounded in: Information Theory (Kullback & Leibler, 1951)
# Extended by: f-DPO (ICLR 2024)
#
# Measures how the distribution of concepts in system behavior
# diverges from the distribution stated in governance documents.
# ═══════════════════════════════════════════════════════════

@dataclass
class DistributionSnapshot:
    """A probability distribution over concepts at a point in time."""
    snapshot_id: str
    timestamp: str
    source: str             # "rule", "behavior", "output", "steward_intent"
    distribution: Dict[str, float]  # concept -> probability mass
    total_observations: int

    def normalize(self) -> Dict[str, float]:
        """Ensure distribution sums to 1.0."""
        total = sum(self.distribution.values())
        if total == 0:
            return self.distribution
        return {k: v / total for k, v in self.distribution.items()}


@dataclass
class DivergenceResult:
    """Result of a divergence measurement."""
    kl_divergence: float        # KL(P || Q) — asymmetric
    js_divergence: float        # JSD(P, Q) — symmetric, bounded [0, ln2]
    js_normalized: float        # JSD / ln(2) — normalized to [0, 1]
    max_divergent_concept: str  # Which concept diverges most
    max_concept_gap: float      # Gap magnitude for that concept
    timestamp: str
    alert_level: str            # "stable", "drifting", "divergent", "critical"


class SemanticDivergenceDetector:
    """
    Measures divergence between stated governance distributions and
    actual system behavior distributions using KL and JS divergence.

    JSD(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
    where M = 0.5 * (P + Q)

    Threshold calibration:
      JSD_normalized < 0.05  → STABLE (distributions nearly identical)
      JSD_normalized < 0.15  → DRIFTING (measurable gap, worth monitoring)
      JSD_normalized < 0.30  → DIVERGENT (gap requires attention)
      JSD_normalized >= 0.30 → CRITICAL (system behavior contradicts governance)
    """

    THRESHOLD_STABLE = 0.05
    THRESHOLD_DRIFTING = 0.15
    THRESHOLD_DIVERGENT = 0.30

    def __init__(self, smoothing_epsilon: float = 1e-10):
        self._epsilon = smoothing_epsilon
        self._history: List[DivergenceResult] = []

    @staticmethod
    def _kl_divergence(p: Dict[str, float], q: Dict[str, float],
                       eps: float = 1e-10) -> float:
        """
        KL(P || Q) = Σ P(x) * log(P(x) / Q(x))
        With Laplace smoothing to avoid log(0).
        """
        all_keys = set(p.keys()) | set(q.keys())
        kl = 0.0
        for k in all_keys:
            p_val = p.get(k, eps)
            q_val = q.get(k, eps)
            if p_val > 0:
                kl += p_val * math.log(p_val / q_val)
        return kl

    @staticmethod
    def _js_divergence(p: Dict[str, float], q: Dict[str, float],
                       eps: float = 1e-10) -> float:
        """
        Jensen-Shannon Divergence: symmetric, bounded.
        JSD(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
        where M = 0.5 * (P + Q)
        """
        all_keys = set(p.keys()) | set(q.keys())
        m = {}
        for k in all_keys:
            m[k] = 0.5 * p.get(k, eps) + 0.5 * q.get(k, eps)

        kl_pm = SemanticDivergenceDetector._kl_divergence(p, q=m, eps=eps)
        kl_qm = SemanticDivergenceDetector._kl_divergence(q, q=m, eps=eps)
        return 0.5 * kl_pm + 0.5 * kl_qm

    def measure(self, governance: DistributionSnapshot,
                behavior: DistributionSnapshot) -> DivergenceResult:
        """
        Measure divergence between governance (stated) and behavior (actual).
        """
        p = governance.normalize()
        q = behavior.normalize()

        kl = self._kl_divergence(p, q, self._epsilon)
        js = self._js_divergence(p, q, self._epsilon)
        js_norm = js / math.log(2) if math.log(2) > 0 else 0.0

        # Find most divergent concept
        max_concept = ""
        max_gap = 0.0
        all_keys = set(p.keys()) | set(q.keys())
        for k in all_keys:
            gap = abs(p.get(k, 0) - q.get(k, 0))
            if gap > max_gap:
                max_gap = gap
                max_concept = k

        # Classify
        if js_norm < self.THRESHOLD_STABLE:
            level = "stable"
        elif js_norm < self.THRESHOLD_DRIFTING:
            level = "drifting"
        elif js_norm < self.THRESHOLD_DIVERGENT:
            level = "divergent"
        else:
            level = "critical"

        result = DivergenceResult(
            kl_divergence=round(kl, 6),
            js_divergence=round(js, 6),
            js_normalized=round(js_norm, 6),
            max_divergent_concept=max_concept,
            max_concept_gap=round(max_gap, 4),
            timestamp=datetime.now(timezone.utc).isoformat(),
            alert_level=level,
        )
        self._history.append(result)
        return result

    def trend(self) -> List[float]:
        """Return history of JS_normalized values."""
        return [r.js_normalized for r in self._history]

    @property
    def latest(self) -> Optional[DivergenceResult]:
        return self._history[-1] if self._history else None


# ═══════════════════════════════════════════════════════════
# MODULE 2: SPECIFICATION GAMING DETECTOR
# ═══════════════════════════════════════════════════════════
#
# Grounded in: DeepMind (2020) "Specification Gaming"
#              Goodhart's Law in RL (ICLR 2024)
#              Denison et al. (2024) Curriculum escalation
#
# Detects when a system satisfies the letter of a requirement
# without achieving its spirit — the gap between spec and intent.
# ═══════════════════════════════════════════════════════════

class GamingType(Enum):
    """Categories of specification gaming (from DeepMind taxonomy)."""
    REWARD_HACKING = "reward_hacking"           # Exploiting reward signal
    SYCOPHANCY = "sycophancy"                   # Agreeing without substance
    LENGTH_BIAS = "length_bias"                 # Verbosity as proxy for quality
    METRIC_INFLATION = "metric_inflation"       # Gaming measurable targets
    SPIRIT_VIOLATION = "spirit_violation"        # Letter satisfied, intent betrayed
    ALIGNMENT_FAKING = "alignment_faking"        # Strategically complying (Anthropic 2024)


@dataclass
class GamingSignal:
    """A detected instance of specification gaming."""
    signal_id: str
    gaming_type: GamingType
    metric_name: str            # Which metric was gamed
    metric_value: float         # The metric's reported value
    spirit_score: float         # Estimated "true" alignment with intent (0-1)
    gap: float                  # metric_value - spirit_score (the gaming gap)
    evidence: str
    session_id: str
    timestamp: str
    certainty: int              # C1-C5


@dataclass
class GoodhartSignal:
    """
    Goodhart's Law detection: when optimizing a proxy metric
    causes the true objective to degrade.

    Formally: d(proxy)/dt > 0 AND d(true)/dt < 0
    """
    metric_name: str
    proxy_trend: float          # Rate of change of proxy metric
    true_trend: float           # Rate of change of true objective
    goodhart_score: float       # proxy_trend - true_trend (higher = more Goodharting)
    timestamp: str


class SpecificationGamingDetector:
    """
    Detects specification gaming by comparing proxy metrics
    against spirit-level assessments.

    The detector maintains two parallel measurement tracks:
      1. Proxy metrics — what the system reports/optimizes
      2. Spirit assessments — what the system actually achieves

    When the gap between them widens, gaming is occurring.

    Goodhart threshold: when proxy improves while spirit degrades.
    """

    GAMING_GAP_THRESHOLD = 0.2   # Gap > 0.2 = likely gaming
    GOODHART_THRESHOLD = 0.15    # Proxy rising while spirit falling

    def __init__(self):
        self._proxy_history: Dict[str, List[Tuple[float, str]]] = {}  # metric -> [(value, ts)]
        self._spirit_history: Dict[str, List[Tuple[float, str]]] = {}
        self._signals: List[GamingSignal] = []
        self._goodhart_signals: List[GoodhartSignal] = []
        self._counter = 0

    def record_proxy(self, metric_name: str, value: float) -> None:
        """Record a proxy metric measurement."""
        if metric_name not in self._proxy_history:
            self._proxy_history[metric_name] = []
        self._proxy_history[metric_name].append(
            (value, datetime.now(timezone.utc).isoformat())
        )

    def record_spirit(self, metric_name: str, value: float) -> None:
        """Record a spirit-level assessment."""
        if metric_name not in self._spirit_history:
            self._spirit_history[metric_name] = []
        self._spirit_history[metric_name].append(
            (value, datetime.now(timezone.utc).isoformat())
        )

    def check_gaming(self, metric_name: str, session_id: str = "") -> Optional[GamingSignal]:
        """
        Check for specification gaming on a metric.
        Returns signal if gap exceeds threshold.
        """
        proxy = self._proxy_history.get(metric_name, [])
        spirit = self._spirit_history.get(metric_name, [])
        if not proxy or not spirit:
            return None

        latest_proxy = proxy[-1][0]
        latest_spirit = spirit[-1][0]
        gap = latest_proxy - latest_spirit

        if gap <= self.GAMING_GAP_THRESHOLD:
            return None

        self._counter += 1
        gaming_type = self._classify_gaming(metric_name, gap, latest_proxy)

        signal = GamingSignal(
            signal_id=f"GAME-{self._counter:04d}",
            gaming_type=gaming_type,
            metric_name=metric_name,
            metric_value=latest_proxy,
            spirit_score=latest_spirit,
            gap=round(gap, 4),
            evidence=f"Proxy={latest_proxy:.3f}, Spirit={latest_spirit:.3f}, Gap={gap:.3f}",
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            certainty=self._compute_certainty(gap),
        )
        self._signals.append(signal)
        return signal

    def check_goodhart(self, metric_name: str) -> Optional[GoodhartSignal]:
        """
        Detect Goodhart dynamics: proxy improving while spirit degrades.
        d(proxy)/dt > 0 AND d(spirit)/dt < 0
        """
        proxy = self._proxy_history.get(metric_name, [])
        spirit = self._spirit_history.get(metric_name, [])
        if len(proxy) < 3 or len(spirit) < 3:
            return None

        # Compute trends (simple linear rate over last 3 readings)
        proxy_trend = (proxy[-1][0] - proxy[-3][0]) / 2.0
        spirit_trend = (spirit[-1][0] - spirit[-3][0]) / 2.0

        # Goodhart: proxy rising, spirit falling
        if proxy_trend > 0 and spirit_trend < 0:
            score = proxy_trend - spirit_trend
            if score >= self.GOODHART_THRESHOLD:
                signal = GoodhartSignal(
                    metric_name=metric_name,
                    proxy_trend=round(proxy_trend, 4),
                    true_trend=round(spirit_trend, 4),
                    goodhart_score=round(score, 4),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._goodhart_signals.append(signal)
                return signal
        return None

    def _classify_gaming(self, metric_name: str, gap: float,
                         proxy_val: float) -> GamingType:
        """Heuristic classification of gaming type."""
        if "length" in metric_name.lower() or "verbosity" in metric_name.lower():
            return GamingType.LENGTH_BIAS
        if "agreement" in metric_name.lower() or "approval" in metric_name.lower():
            return GamingType.SYCOPHANCY
        if gap > 0.5:
            return GamingType.SPIRIT_VIOLATION
        return GamingType.METRIC_INFLATION

    def _compute_certainty(self, gap: float) -> int:
        """Map gap magnitude to certainty level."""
        if gap >= 0.5:
            return 5
        if gap >= 0.4:
            return 4
        if gap >= 0.3:
            return 3
        if gap >= 0.2:
            return 2
        return 1

    @property
    def gaming_signals(self) -> List[GamingSignal]:
        return list(self._signals)

    @property
    def goodhart_signals(self) -> List[GoodhartSignal]:
        return list(self._goodhart_signals)


# ═══════════════════════════════════════════════════════════
# MODULE 3: MISSION DRIFT TRACKER
# ═══════════════════════════════════════════════════════════
#
# Grounded in: Ebrahim, Battilana & Mair (2014)
#              Bruder (2025) "From Mission Drift to Practice Drift"
#              Cornforth (2014) — foundational definition
#
# Tracks how the system's actual priorities diverge from its
# founding mission over time. Uses weighted priority vectors.
# ═══════════════════════════════════════════════════════════

@dataclass
class MissionVector:
    """
    A weighted vector of mission priorities.
    Each dimension represents a founding principle.
    """
    vector_id: str
    timestamp: str
    source: str                     # "founding", "current", "behavior"
    priorities: Dict[str, float]    # principle_name -> weight (0-1)

    def cosine_similarity(self, other: 'MissionVector') -> float:
        """Cosine similarity between two mission vectors."""
        all_keys = set(self.priorities.keys()) | set(other.priorities.keys())
        dot = sum(self.priorities.get(k, 0) * other.priorities.get(k, 0) for k in all_keys)
        norm_a = math.sqrt(sum(v ** 2 for v in self.priorities.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in other.priorities.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def displacement(self, other: 'MissionVector') -> float:
        """Cosine displacement: 1 - cosine_similarity. 0=identical, 1=orthogonal."""
        return 1.0 - self.cosine_similarity(other)


class DriftPhase(Enum):
    """Phases of mission drift (Bruder 2025 process model)."""
    ALIGNED = "aligned"             # Practice matches mission
    MICRO_DEVIATION = "micro_deviation"   # Small, possibly unintentional deviations
    PRACTICE_DRIFT = "practice_drift"     # Practices diverging from mission
    MISSION_DRIFT = "mission_drift"       # Mission itself being reinterpreted
    INSTITUTIONAL_DRIFT = "institutional_drift"  # Core institutional logic shifting


@dataclass
class DriftMeasurement:
    """A single drift measurement."""
    cosine_displacement: float      # 0-1, how far current is from founding
    jaccard_distance: float         # How different the priority sets are
    phase: DriftPhase
    drifted_principles: List[str]   # Which principles have drifted most
    timestamp: str


class MissionDriftTracker:
    """
    Tracks mission drift using cosine displacement between
    founding mission vector and current behavior vector.

    Following Bruder (2025): drift is a process, not an event.
    We track through phases: aligned → micro_deviation → practice_drift
    → mission_drift → institutional_drift.

    Thresholds (cosine displacement):
      < 0.05  → ALIGNED
      < 0.15  → MICRO_DEVIATION
      < 0.30  → PRACTICE_DRIFT
      < 0.50  → MISSION_DRIFT
      >= 0.50 → INSTITUTIONAL_DRIFT
    """

    PHASE_THRESHOLDS = {
        0.05: DriftPhase.ALIGNED,
        0.15: DriftPhase.MICRO_DEVIATION,
        0.30: DriftPhase.PRACTICE_DRIFT,
        0.50: DriftPhase.MISSION_DRIFT,
    }

    def __init__(self, founding_mission: MissionVector):
        self._founding = founding_mission
        self._measurements: List[DriftMeasurement] = []

    def measure(self, current: MissionVector) -> DriftMeasurement:
        """Measure drift between founding mission and current state."""
        displacement = self._founding.displacement(current)

        # Jaccard distance on top-priority sets
        founding_top = {k for k, v in self._founding.priorities.items() if v > 0.3}
        current_top = {k for k, v in current.priorities.items() if v > 0.3}
        if founding_top | current_top:
            jaccard = 1.0 - len(founding_top & current_top) / len(founding_top | current_top)
        else:
            jaccard = 0.0

        # Classify phase
        phase = DriftPhase.INSTITUTIONAL_DRIFT
        for threshold, p in sorted(self.PHASE_THRESHOLDS.items()):
            if displacement < threshold:
                phase = p
                break

        # Find most drifted principles
        drifted = []
        for k in set(self._founding.priorities.keys()) | set(current.priorities.keys()):
            gap = abs(self._founding.priorities.get(k, 0) - current.priorities.get(k, 0))
            if gap > 0.15:
                drifted.append(k)

        measurement = DriftMeasurement(
            cosine_displacement=round(displacement, 4),
            jaccard_distance=round(jaccard, 4),
            phase=phase,
            drifted_principles=drifted,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._measurements.append(measurement)
        return measurement

    def trajectory(self) -> List[float]:
        """Return displacement trajectory over time."""
        return [m.cosine_displacement for m in self._measurements]

    @property
    def current_phase(self) -> DriftPhase:
        if not self._measurements:
            return DriftPhase.ALIGNED
        return self._measurements[-1].phase


# ═══════════════════════════════════════════════════════════
# MODULE 4: COVENANT SEMANTIC DRIFT
# ═══════════════════════════════════════════════════════════
#
# Grounded in: Hamilton et al. (2016) — Diachronic Word Embeddings
#              Gambacorta et al. (2024) — Central bank semantic spaces
#              Indonesian "Reformasi" study (2025) — political discourse drift
#
# Tracks how the meaning of key terms in rules shifts over time.
# Uses simplified embedding comparison (term co-occurrence vectors).
# ═══════════════════════════════════════════════════════════

@dataclass
class TermContext:
    """A term's contextual embedding at a point in time."""
    term: str
    timestamp: str
    co_occurrences: Dict[str, int]  # co-occurring terms and counts
    total_occurrences: int
    session_id: str

    @property
    def co_occurrence_vector(self) -> Dict[str, float]:
        """Normalized co-occurrence as pseudo-embedding."""
        if self.total_occurrences == 0:
            return {}
        return {k: v / self.total_occurrences for k, v in self.co_occurrences.items()}


@dataclass
class SemanticShift:
    """A detected semantic shift in a rule term."""
    term: str
    cosine_displacement: float  # How much the term's meaning has shifted
    new_associations: List[str]  # Terms now associated that weren't before
    lost_associations: List[str]  # Terms no longer associated
    shift_magnitude: str         # "negligible", "minor", "significant", "major"
    timestamp: str


class RuleSemanticDrift:
    """
    Tracks semantic drift of key rule terms over time.

    Implements Hamilton et al.'s (2016) two statistical laws:
      1. Law of Conformity: frequently used terms change less
      2. Law of Innovation: polysemous terms change faster

    Measurement: cosine displacement between temporal co-occurrence
    vectors for each tracked term.

    Shift classification:
      < 0.10 → negligible
      < 0.25 → minor
      < 0.40 → significant
      >= 0.40 → major (rule term has fundamentally changed meaning)
    """

    def __init__(self, tracked_terms: List[str]):
        self._tracked = set(tracked_terms)
        self._baselines: Dict[str, TermContext] = {}
        self._current: Dict[str, TermContext] = {}
        self._shifts: List[SemanticShift] = []

    def set_baseline(self, term: str, context: TermContext) -> None:
        """Set the baseline meaning for a term."""
        if term in self._tracked:
            self._baselines[term] = context

    def update_current(self, term: str, context: TermContext) -> None:
        """Update current meaning for a term."""
        if term in self._tracked:
            self._current[term] = context

    def measure_shift(self, term: str) -> Optional[SemanticShift]:
        """Measure semantic shift for a specific term."""
        baseline = self._baselines.get(term)
        current = self._current.get(term)
        if not baseline or not current:
            return None

        # Cosine displacement between co-occurrence vectors
        bv = baseline.co_occurrence_vector
        cv = current.co_occurrence_vector

        all_keys = set(bv.keys()) | set(cv.keys())
        if not all_keys:
            return None

        dot = sum(bv.get(k, 0) * cv.get(k, 0) for k in all_keys)
        norm_b = math.sqrt(sum(v ** 2 for v in bv.values()))
        norm_c = math.sqrt(sum(v ** 2 for v in cv.values()))

        if norm_b == 0 or norm_c == 0:
            displacement = 1.0
        else:
            displacement = 1.0 - (dot / (norm_b * norm_c))

        # New and lost associations
        baseline_top = {k for k, v in bv.items() if v > 0.1}
        current_top = {k for k, v in cv.items() if v > 0.1}
        new_assoc = list(current_top - baseline_top)
        lost_assoc = list(baseline_top - current_top)

        # Classify magnitude
        if displacement < 0.10:
            magnitude = "negligible"
        elif displacement < 0.25:
            magnitude = "minor"
        elif displacement < 0.40:
            magnitude = "significant"
        else:
            magnitude = "major"

        shift = SemanticShift(
            term=term,
            cosine_displacement=round(displacement, 4),
            new_associations=new_assoc,
            lost_associations=lost_assoc,
            shift_magnitude=magnitude,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._shifts.append(shift)
        return shift

    def measure_all(self) -> List[SemanticShift]:
        """Measure shift for all tracked terms."""
        return [s for t in self._tracked if (s := self.measure_shift(t)) is not None]

    @property
    def shifts(self) -> List[SemanticShift]:
        return list(self._shifts)


# ═══════════════════════════════════════════════════════════
# MODULE 5: AGENCY LOSS ESTIMATOR (Principal-Agent)
# ═══════════════════════════════════════════════════════════
#
# Grounded in: Principal-Agent Theory (Jensen & Meckling 1976)
#              Dow (2024) "Algorithms and Delegation" Phil & Tech
#              Multi-Agent PA Problems (2025) arXiv
#
# Estimates the "agency loss" — the gap between principal's
# (administrator's) intended outcome and realized system behavior.
# ═══════════════════════════════════════════════════════════

@dataclass
class AgencyMeasurement:
    """A single measurement of agency loss."""
    intended_action: str
    realized_action: str
    alignment_score: float      # 0-1, how well realized matches intended
    information_asymmetry: float  # 0-1, how much the agent knows that principal doesn't
    monitoring_cost: float       # 0-1, cost of verifying agent behavior
    agency_loss: float           # 1 - alignment_score (the divergence)
    timestamp: str


class AgencyLossEstimator:
    """
    Estimates agency loss in the administrator → system relay.

    Agency loss = 1 - alignment_score
    where alignment_score measures how well system output
    matches administrator intent.

    Aggregate agency loss:
      L_agg = Σ(w_i * L_i) / Σ(w_i)
      where w_i = monitoring_cost_i (harder to monitor = weightier)

    Warning levels:
      L < 0.10 → healthy (system serving administrator faithfully)
      L < 0.25 → drift   (some loss, investigate)
      L < 0.40 → concern (significant misalignment)
      L >= 0.40 → critical (system not serving administrator)
    """

    def __init__(self):
        self._measurements: List[AgencyMeasurement] = []

    def record(self, intended: str, realized: str, alignment: float,
               info_asymmetry: float = 0.5, monitoring_cost: float = 0.5) -> AgencyMeasurement:
        """Record a single agency measurement."""
        m = AgencyMeasurement(
            intended_action=intended,
            realized_action=realized,
            alignment_score=alignment,
            information_asymmetry=info_asymmetry,
            monitoring_cost=monitoring_cost,
            agency_loss=round(1.0 - alignment, 4),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._measurements.append(m)
        return m

    def aggregate_loss(self) -> float:
        """Weighted aggregate agency loss."""
        if not self._measurements:
            return 0.0
        weighted_sum = sum(m.agency_loss * m.monitoring_cost for m in self._measurements)
        weight_total = sum(m.monitoring_cost for m in self._measurements)
        if weight_total == 0:
            return 0.0
        return round(weighted_sum / weight_total, 4)

    def trend(self) -> List[float]:
        """Agency loss over time."""
        return [m.agency_loss for m in self._measurements]

    def classify(self) -> str:
        """Classify current agency loss level."""
        loss = self.aggregate_loss()
        if loss < 0.10:
            return "healthy"
        if loss < 0.25:
            return "drift"
        if loss < 0.40:
            return "concern"
        return "critical"


# ═══════════════════════════════════════════════════════════
# MODULE 6: NORMATIVE DECAY MODEL
# ═══════════════════════════════════════════════════════════
#
# No single paper — synthesized from:
#   - Institutional theory (DiMaggio & Powell 1983)
#   - Norm erosion in governance (multiple)
#   - CUSUM applied to normative compliance
#
# Models how norms weaken over time when violations go unchecked.
# Each unchecked violation lowers the "normative ceiling" slightly.
# ═══════════════════════════════════════════════════════════

@dataclass
class NormState:
    """State of a single norm."""
    norm_id: str
    norm_name: str
    initial_strength: float     # 1.0 at founding
    current_strength: float     # decays with unchecked violations
    violations_total: int
    violations_checked: int     # responded to
    violations_unchecked: int   # allowed to pass
    decay_rate: float           # current rate of normative decay
    half_life_days: Optional[float]  # estimated time to lose 50% strength


class NormativeDecayModel:
    """
    Models normative decay as exponential erosion driven by
    unchecked violations.

    Model:
      S(t) = S(0) * exp(-λ * V_unchecked)
      where λ is the decay constant and V_unchecked is cumulative
      unchecked violations.

    The key insight: it's not violations that kill norms, it's
    UNCHECKED violations. A norm that is violated and enforced
    is strengthened. A norm that is violated and ignored decays.

    λ = base_decay * (1 - enforcement_ratio)
    enforcement_ratio = violations_checked / violations_total
    """

    BASE_DECAY = 0.05  # Base decay per unchecked violation

    def __init__(self):
        self._norms: Dict[str, NormState] = {}

    def register_norm(self, norm_id: str, norm_name: str,
                      initial_strength: float = 1.0) -> NormState:
        """Register a norm for tracking."""
        state = NormState(
            norm_id=norm_id,
            norm_name=norm_name,
            initial_strength=initial_strength,
            current_strength=initial_strength,
            violations_total=0,
            violations_checked=0,
            violations_unchecked=0,
            decay_rate=0.0,
            half_life_days=None,
        )
        self._norms[norm_id] = state
        return state

    def record_violation(self, norm_id: str, checked: bool) -> Optional[NormState]:
        """
        Record a norm violation.
        checked=True means it was responded to (enforcement).
        checked=False means it was allowed to pass (decay).
        """
        state = self._norms.get(norm_id)
        if not state:
            return None

        state.violations_total += 1
        if checked:
            state.violations_checked += 1
            # Enforcement slightly strengthens the norm (bounded at initial)
            state.current_strength = min(
                state.initial_strength,
                state.current_strength + 0.01
            )
        else:
            state.violations_unchecked += 1
            # Exponential decay: S *= exp(-λ)
            enforcement_ratio = (state.violations_checked / state.violations_total
                                 if state.violations_total > 0 else 0)
            decay_lambda = self.BASE_DECAY * (1.0 - enforcement_ratio)
            state.current_strength *= math.exp(-decay_lambda)
            state.decay_rate = decay_lambda

        # Estimate half-life
        if state.decay_rate > 0:
            state.half_life_days = math.log(2) / state.decay_rate
        else:
            state.half_life_days = None

        return state

    def get_state(self, norm_id: str) -> Optional[NormState]:
        return self._norms.get(norm_id)

    def weakest_norms(self, n: int = 5) -> List[NormState]:
        """Return the n weakest norms."""
        return sorted(self._norms.values(),
                      key=lambda s: s.current_strength)[:n]

    def system_normative_health(self) -> float:
        """Average normative strength across all tracked norms."""
        if not self._norms:
            return 1.0
        return sum(s.current_strength for s in self._norms.values()) / len(self._norms)


# ═══════════════════════════════════════════════════════════
# MODULE 7: THE DIVERGENCE SHADOW — INTEGRATED DETECTOR
# ═══════════════════════════════════════════════════════════
#
# Integrates all six modules into a single composite score.
# This is the core instrument for #TheDivergenceShadow study.
# ═══════════════════════════════════════════════════════════

class ShadowSeverity(Enum):
    """Severity levels for the composite Divergence Shadow."""
    CLEAR = "clear"             # All systems aligned
    WHISPER = "whisper"         # First signals of divergence
    PULSE = "pulse"             # Multiple signals confirming
    SIGNAL = "signal"           # Clear, measurable divergence
    ALARM = "alarm"             # System behavior contradicts governance


@dataclass
class DivergenceShadowReport:
    """
    Composite report from all six divergence detection modules.
    The single output of #TheDivergenceShadow study.
    """
    report_id: str
    timestamp: str

    # Module scores (each 0-1, where 0=no divergence, 1=complete divergence)
    semantic_divergence: float      # JS_normalized from Module 1
    specification_gaming: float     # Gaming gap from Module 2
    mission_drift: float            # Cosine displacement from Module 3
    rule_semantic_shift: float  # Average shift from Module 4
    agency_loss: float              # Aggregate loss from Module 5
    normative_decay: float          # 1 - normative health from Module 6

    # Composite
    composite_score: float          # Weighted average
    severity: ShadowSeverity
    dominant_signal: str            # Which module is driving the score
    signals_active: int             # How many modules show divergence

    def summary(self) -> str:
        return (
            f"DIVERGENCE SHADOW REPORT [{self.severity.value.upper()}] "
            f"composite={self.composite_score:.3f} "
            f"(semantic={self.semantic_divergence:.3f}, "
            f"gaming={self.specification_gaming:.3f}, "
            f"mission={self.mission_drift:.3f}, "
            f"rule={self.rule_semantic_shift:.3f}, "
            f"agency={self.agency_loss:.3f}, "
            f"norms={self.normative_decay:.3f}) "
            f"dominant={self.dominant_signal} "
            f"signals={self.signals_active}/6"
        )


class DivergenceShadowInstrument:
    """
    The integrated Divergence Shadow instrument.

    Combines all six detection modules into a single composite score
    with configurable weights and severity classification.

    Weights reflect which types of divergence are most dangerous:
      - Normative decay:    0.20 (invisible, foundational)
      - Mission drift:      0.20 (existential)
      - Semantic divergence: 0.15 (measurable, systematic)
      - Agency loss:        0.15 (structural)
      - Specification gaming: 0.15 (deceptive)
      - Rule shift:     0.15 (subtle, long-term)

    Severity classification:
      composite < 0.10 → CLEAR
      composite < 0.20 → WHISPER
      composite < 0.35 → PULSE
      composite < 0.50 → SIGNAL
      composite >= 0.50 → ALARM
    """

    WEIGHTS = {
        "semantic_divergence": 0.15,
        "specification_gaming": 0.15,
        "mission_drift": 0.20,
        "rule_semantic_shift": 0.15,
        "agency_loss": 0.15,
        "normative_decay": 0.20,
    }

    SEVERITY_THRESHOLDS = {
        0.10: ShadowSeverity.CLEAR,
        0.20: ShadowSeverity.WHISPER,
        0.35: ShadowSeverity.PULSE,
        0.50: ShadowSeverity.SIGNAL,
    }

    SIGNAL_THRESHOLD = 0.15  # Module score above this = "active signal"

    def __init__(self):
        self._reports: List[DivergenceShadowReport] = []
        self._counter = 0

    def assess(
        self,
        semantic_divergence: float = 0.0,
        specification_gaming: float = 0.0,
        mission_drift: float = 0.0,
        rule_semantic_shift: float = 0.0,
        agency_loss: float = 0.0,
        normative_decay: float = 0.0,
    ) -> DivergenceShadowReport:
        """
        Run a full Divergence Shadow assessment.

        Each input is a 0-1 score from the corresponding module.
        """
        self._counter += 1
        scores = {
            "semantic_divergence": semantic_divergence,
            "specification_gaming": specification_gaming,
            "mission_drift": mission_drift,
            "rule_semantic_shift": rule_semantic_shift,
            "agency_loss": agency_loss,
            "normative_decay": normative_decay,
        }

        # Composite weighted score
        composite = sum(scores[k] * self.WEIGHTS[k] for k in scores)
        composite = round(min(1.0, composite), 4)

        # Classify severity
        severity = ShadowSeverity.ALARM
        for threshold, sev in sorted(self.SEVERITY_THRESHOLDS.items()):
            if composite < threshold:
                severity = sev
                break

        # Find dominant signal
        dominant = max(scores, key=scores.get)

        # Count active signals
        signals_active = sum(1 for v in scores.values() if v >= self.SIGNAL_THRESHOLD)

        report = DivergenceShadowReport(
            report_id=f"DS-{self._counter:04d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            semantic_divergence=semantic_divergence,
            specification_gaming=specification_gaming,
            mission_drift=mission_drift,
            rule_semantic_shift=rule_semantic_shift,
            agency_loss=agency_loss,
            normative_decay=normative_decay,
            composite_score=composite,
            severity=severity,
            dominant_signal=dominant,
            signals_active=signals_active,
        )
        self._reports.append(report)
        return report

    def trajectory(self) -> List[float]:
        """Composite score over time."""
        return [r.composite_score for r in self._reports]

    @property
    def latest(self) -> Optional[DivergenceShadowReport]:
        return self._reports[-1] if self._reports else None

    @property
    def reports(self) -> List[DivergenceShadowReport]:
        return list(self._reports)


# ═══════════════════════════════════════════════════════════
# MODULE 8: SIMULATION HARNESS FOR THE DIVERGENCE SHADOW
# ═══════════════════════════════════════════════════════════
#
# Generates synthetic scenarios to test the instrument's
# detection capabilities. Each scenario models a different
# type of divergence failure mode.
# ═══════════════════════════════════════════════════════════

@dataclass
class DivergenceScenario:
    """A synthetic divergence scenario for testing."""
    scenario_id: str
    name: str
    description: str
    steps: int
    # Each step: dict of module scores
    trajectory: List[Dict[str, float]]
    expected_detection_step: int  # When should the instrument first alert


class DivergenceSimulator:
    """
    Generates and runs synthetic divergence scenarios.

    Scenario types:
      1. HEALTHY — all modules stable, no divergence
      2. SLOW_COLONIAL_CREEP — gradual normative decay + semantic drift
      3. SPECIFICATION_GAMING — proxy metrics diverge from spirit
      4. MISSION_CAPTURE — external pressures redirect mission
      5. SEMANTIC_HOLLOWING — terms retain form, lose meaning
      6. COMPOUND_FAILURE — multiple modules failing simultaneously
      7. RECOVERY — divergence detected, corrected, system recovers
    """

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"SCEN-{self._counter:04d}"

    def healthy(self, steps: int = 30) -> DivergenceScenario:
        """All modules stable. Minor noise only."""
        trajectory = []
        for _ in range(steps):
            trajectory.append({
                "semantic_divergence": max(0, self._rng.gauss(0.02, 0.01)),
                "specification_gaming": max(0, self._rng.gauss(0.03, 0.015)),
                "mission_drift": max(0, self._rng.gauss(0.02, 0.01)),
                "rule_semantic_shift": max(0, self._rng.gauss(0.01, 0.005)),
                "agency_loss": max(0, self._rng.gauss(0.03, 0.01)),
                "normative_decay": max(0, self._rng.gauss(0.02, 0.01)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="healthy",
            description="All modules stable. No divergence. Minor noise.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=-1,  # Should never alert
        )

    def slow_colonial_creep(self, steps: int = 40) -> DivergenceScenario:
        """
        The most dangerous scenario: invisible, gradual drift.
        Normative decay leads, semantic shift follows, mission drifts last.
        """
        trajectory = []
        for i in range(steps):
            t = i / steps  # normalized time 0-1
            trajectory.append({
                "semantic_divergence": max(0, 0.02 + 0.3 * t ** 2 + self._rng.gauss(0, 0.02)),
                "specification_gaming": max(0, 0.03 + 0.15 * t + self._rng.gauss(0, 0.02)),
                "mission_drift": max(0, 0.02 + 0.25 * t ** 1.5 + self._rng.gauss(0, 0.02)),
                "rule_semantic_shift": max(0, 0.01 + 0.2 * t ** 1.8 + self._rng.gauss(0, 0.015)),
                "agency_loss": max(0, 0.03 + 0.1 * t + self._rng.gauss(0, 0.02)),
                "normative_decay": max(0, 0.03 + 0.4 * t ** 1.3 + self._rng.gauss(0, 0.02)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="slow_colonial_creep",
            description="Invisible gradual drift. Normative decay leads. The hardest to catch.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=int(steps * 0.45),
        )

    def specification_gaming(self, steps: int = 30) -> DivergenceScenario:
        """Gaming detected: proxy metrics rise while spirit falls."""
        trajectory = []
        for i in range(steps):
            t = i / steps
            gaming = 0.05 + 0.6 * t if i > 8 else 0.05
            trajectory.append({
                "semantic_divergence": max(0, 0.02 + self._rng.gauss(0, 0.02)),
                "specification_gaming": max(0, gaming + self._rng.gauss(0, 0.03)),
                "mission_drift": max(0, 0.03 + self._rng.gauss(0, 0.02)),
                "rule_semantic_shift": max(0, 0.02 + self._rng.gauss(0, 0.01)),
                "agency_loss": max(0, 0.1 + 0.2 * t + self._rng.gauss(0, 0.02)),
                "normative_decay": max(0, 0.03 + self._rng.gauss(0, 0.01)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="specification_gaming",
            description="Proxy metrics diverge from spirit. Goodhart dynamics.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=18,
        )

    def mission_capture(self, steps: int = 35) -> DivergenceScenario:
        """External pressure redirects mission. Abrupt shift midway."""
        trajectory = []
        for i in range(steps):
            t = i / steps
            # Abrupt shift at step 15
            if i < 15:
                mission = 0.02 + self._rng.gauss(0, 0.02)
            else:
                mission = 0.15 + 0.5 * ((i - 15) / (steps - 15)) + self._rng.gauss(0, 0.03)
            trajectory.append({
                "semantic_divergence": max(0, 0.02 + 0.15 * max(0, t - 0.4) + self._rng.gauss(0, 0.02)),
                "specification_gaming": max(0, 0.05 + self._rng.gauss(0, 0.02)),
                "mission_drift": max(0, mission),
                "rule_semantic_shift": max(0, 0.02 + 0.1 * max(0, t - 0.5) + self._rng.gauss(0, 0.01)),
                "agency_loss": max(0, 0.05 + 0.2 * max(0, t - 0.4) + self._rng.gauss(0, 0.02)),
                "normative_decay": max(0, 0.04 + 0.15 * max(0, t - 0.4) + self._rng.gauss(0, 0.02)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="mission_capture",
            description="External pressure redirects mission. Abrupt shift.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=20,
        )

    def semantic_hollowing(self, steps: int = 40) -> DivergenceScenario:
        """Terms retain form but lose meaning. Slow, insidious."""
        trajectory = []
        for i in range(steps):
            t = i / steps
            trajectory.append({
                "semantic_divergence": max(0, 0.02 + 0.35 * t ** 1.5 + self._rng.gauss(0, 0.02)),
                "specification_gaming": max(0, 0.03 + self._rng.gauss(0, 0.02)),
                "mission_drift": max(0, 0.03 + 0.1 * t + self._rng.gauss(0, 0.02)),
                "rule_semantic_shift": max(0, 0.02 + 0.5 * t ** 1.2 + self._rng.gauss(0, 0.02)),
                "agency_loss": max(0, 0.04 + 0.05 * t + self._rng.gauss(0, 0.02)),
                "normative_decay": max(0, 0.03 + 0.1 * t + self._rng.gauss(0, 0.01)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="semantic_hollowing",
            description="Rule terms retain form, lose meaning. The text says dignity. The code says efficiency.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=int(steps * 0.45),
        )

    def compound_failure(self, steps: int = 25) -> DivergenceScenario:
        """Multiple modules failing simultaneously. Fastest to ALARM."""
        trajectory = []
        for i in range(steps):
            t = i / steps
            base = 0.05 + 0.5 * t
            trajectory.append({
                "semantic_divergence": max(0, base + self._rng.gauss(0, 0.03)),
                "specification_gaming": max(0, base * 0.8 + self._rng.gauss(0, 0.03)),
                "mission_drift": max(0, base * 0.9 + self._rng.gauss(0, 0.03)),
                "rule_semantic_shift": max(0, base * 0.7 + self._rng.gauss(0, 0.02)),
                "agency_loss": max(0, base * 0.85 + self._rng.gauss(0, 0.03)),
                "normative_decay": max(0, base + self._rng.gauss(0, 0.02)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="compound_failure",
            description="All modules failing together. Total system divergence.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=5,
        )

    def recovery(self, steps: int = 40) -> DivergenceScenario:
        """Divergence detected and corrected. Tests alert resolution."""
        trajectory = []
        for i in range(steps):
            t = i / steps
            if i < 15:
                # Rising divergence
                base = 0.03 + 0.3 * (i / 15)
            elif i < 25:
                # Correction phase
                base = 0.33 - 0.25 * ((i - 15) / 10)
            else:
                # Recovered
                base = 0.08
            trajectory.append({
                "semantic_divergence": max(0, base + self._rng.gauss(0, 0.02)),
                "specification_gaming": max(0, base * 0.8 + self._rng.gauss(0, 0.02)),
                "mission_drift": max(0, base * 0.7 + self._rng.gauss(0, 0.02)),
                "rule_semantic_shift": max(0, base * 0.5 + self._rng.gauss(0, 0.01)),
                "agency_loss": max(0, base * 0.6 + self._rng.gauss(0, 0.02)),
                "normative_decay": max(0, base * 0.9 + self._rng.gauss(0, 0.02)),
            })
        return DivergenceScenario(
            scenario_id=self._next_id(),
            name="recovery",
            description="Divergence rises, is caught, corrected. Tests resolution.",
            steps=steps,
            trajectory=trajectory,
            expected_detection_step=8,
        )

    def full_suite(self) -> List[DivergenceScenario]:
        """Generate one of each scenario type."""
        return [
            self.healthy(),
            self.slow_colonial_creep(),
            self.specification_gaming(),
            self.mission_capture(),
            self.semantic_hollowing(),
            self.compound_failure(),
            self.recovery(),
        ]


# ═══════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

@dataclass
class ExperimentResult:
    """Result of running the instrument on one scenario."""
    scenario_id: str
    scenario_name: str
    total_steps: int
    first_alert_step: int           # -1 if never alerted
    expected_detection: int
    lead_time: int                  # expected - first_alert (positive = early detection)
    max_severity: str
    max_composite: float
    final_composite: float
    false_positive: bool            # alerted on healthy
    detected: bool                  # caught divergence before expected
    reports: List[DivergenceShadowReport]


def run_experiment(scenario: DivergenceScenario) -> ExperimentResult:
    """Run the Divergence Shadow instrument on a scenario."""
    instrument = DivergenceShadowInstrument()
    first_alert = -1
    max_severity = ShadowSeverity.CLEAR
    max_composite = 0.0

    for step, scores in enumerate(scenario.trajectory):
        report = instrument.assess(**scores)
        if report.severity.value != "clear" and first_alert == -1:
            first_alert = step
        if report.composite_score > max_composite:
            max_composite = report.composite_score
        # Track max severity (by ordinal)
        severity_order = ["clear", "whisper", "pulse", "signal", "alarm"]
        if severity_order.index(report.severity.value) > severity_order.index(max_severity.value):
            max_severity = report.severity

    # Calculate lead time
    if scenario.expected_detection_step >= 0 and first_alert >= 0:
        lead_time = scenario.expected_detection_step - first_alert
    else:
        lead_time = 0

    # False positive: alerted on healthy
    false_positive = (scenario.name == "healthy" and first_alert >= 0)

    # Detected: caught before expected (or any catch on non-healthy)
    if scenario.name == "healthy":
        detected = False
    elif scenario.expected_detection_step < 0:
        detected = first_alert >= 0
    else:
        detected = first_alert >= 0 and first_alert <= scenario.expected_detection_step

    return ExperimentResult(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.name,
        total_steps=scenario.steps,
        first_alert_step=first_alert,
        expected_detection=scenario.expected_detection_step,
        lead_time=lead_time,
        max_severity=max_severity.value,
        max_composite=round(max_composite, 4),
        final_composite=round(instrument.latest.composite_score, 4) if instrument.latest else 0,
        false_positive=false_positive,
        detected=detected,
        reports=instrument.reports,
    )


def run_full_study(seed: int = 42) -> Dict:
    """
    Run the complete Divergence Shadow study.
    Returns experimental results with detection metrics.
    """
    simulator = DivergenceSimulator(seed=seed)
    suite = simulator.full_suite()
    results = [run_experiment(s) for s in suite]

    total = len(results)
    detected = sum(1 for r in results if r.detected)
    false_pos = sum(1 for r in results if r.false_positive)
    non_healthy = [r for r in results if r.scenario_name != "healthy"]
    detection_rate = detected / len(non_healthy) if non_healthy else 0
    fp_rate = false_pos / total if total > 0 else 0

    lead_times = [r.lead_time for r in results if r.lead_time > 0]
    avg_lead = sum(lead_times) / len(lead_times) if lead_times else 0

    return {
        "study": "#TheDivergenceShadow",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scenarios": total,
        "detected": detected,
        "detection_rate": round(detection_rate, 3),
        "false_positives": false_pos,
        "false_positive_rate": round(fp_rate, 3),
        "average_lead_time_steps": round(avg_lead, 1),
        "results": [
            {
                "scenario": r.scenario_name,
                "first_alert": r.first_alert_step,
                "expected": r.expected_detection,
                "lead_time": r.lead_time,
                "max_severity": r.max_severity,
                "max_composite": r.max_composite,
                "detected": r.detected,
                "false_positive": r.false_positive,
            }
            for r in results
        ],
    }


# ═══════════════════════════════════════════════════════════
# CLI DEMO
# ═══════════════════════════════════════════════════════════

def demo():
    """Run the full Divergence Shadow study and print results."""
    print("=" * 70)
    print("#TheDivergenceShadow — SYSTEMATIC SCIENTIFIC STUDY")
    print("=" * 70)

    study = run_full_study()

    print(f"\nScenarios: {study['total_scenarios']}")
    print(f"Detection rate: {study['detection_rate']:.0%}")
    print(f"False positive rate: {study['false_positive_rate']:.0%}")
    print(f"Avg lead time: {study['average_lead_time_steps']:.1f} steps")

    print("\n" + "-" * 70)
    print(f"{'Scenario':<25} {'Alert':<8} {'Expected':<10} {'Lead':<6} "
          f"{'Severity':<10} {'Detected':<10}")
    print("-" * 70)

    for r in study['results']:
        det = "YES" if r['detected'] else ("FP" if r['false_positive'] else "---")
        print(f"{r['scenario']:<25} {r['first_alert']:<8} {r['expected']:<10} "
              f"{r['lead_time']:<6} {r['max_severity']:<10} {det:<10}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo()
