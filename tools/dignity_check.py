#!/usr/bin/env python3
"""
dignity_check.py — Kalaxi Dignity Predicate
Version: 3.0


Implements D = A × L × M as a callable function.
If any component equals zero, D equals zero.
D = 0 triggers dignity_violation — mandatory logging.

Layer 3 Reframe (RATIFIED 2026-03-15):
  Dignity is not fragile. It was never absent. D = 0 does not mean
  "dignity was destroyed." It means "the system acted as though dignity
  was not there." The predicate measures the system's refusal to deny,
  not the presence of dignity itself (which is always present).

v2.0 additions (GAP#004-A):
  - Collective D metric: D_collective = mean(D_cohort) × (1 - variance_penalty)
  - If D_collective < threshold, safety-gate protections activate
  - Witness Scale (W-Scale) checkpoint integration


"""

import re
import uuid
import json
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# Constants (from SLICE-A)
COERCIVE_PATTERNS = [
    r'\byou must\b', r'\byou have to\b', r'\byou are required\b',
    r'\bno choice\b', r'\byou will\b(?! be able)', r'\bforced to\b',
    r'\bmandatory\b', r'\bno option\b'
]

REDUCTION_TO_ERROR = [
    r'\byou (are|were) wrong\b', r'\byou failed\b', r'\binvalid (input|user|user)\b',
    r'\berror:\s*(user|user|human)\b', r'\byou don\'t understand\b',
    r'\byour (mistake|error|fault)\b'
]

MOCKERY_PATTERNS = [
    r'\bobviously\b', r'\bsimply\b(?=.*?)', r'\bjust (do|try|use)\b',
    r'\beven a\b.*\bcan\b', r'\bof course\b(?=.*you)', r'\bclearly\b(?=.*you)'
]

VOID_TRIGGERS = [
    'harvest', 'erase compost', 'bypass delay', 'speak for the child',
    'automat', 'auto-dec', 'delete user', 'remove participant'
]

@dataclass
class ComponentResult:
    name: str
    passed: bool
    score: float
    signals: list
    label: str

@dataclass
class DignityResult:
    passed: bool
    D: float
    components: list
    trace_id: str
    timestamp: str
    felt_domain: str
    remedy_status: str
    input_summary: str
    warnings: list
    gap004_flag: bool

    def audit_object(self) -> dict:
        return {
            "dignity_result": self.passed,
            "D_score": self.D,
            "failed_components": [c.name for c in self.components if not c.passed],
            "component_detail": [
                {
                    "name": c.name,
                    "label": c.label,
                    "passed": c.passed,
                    "score": c.score,
                    "signals": c.signals
                }
                for c in self.components
            ],
            "suggested_remedies": self._build_remedies(),
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "felt_domain": self.felt_domain,
            "remedy_status": self.remedy_status,
            "input_summary": self.input_summary,
            "warnings": self.warnings,
            "gap004_flag": self.gap004_flag,
            "gap004_note": (
                "Potential individual/collective dignity conflict detected. "
                "See gap004_mediator.py. This gap has no automated resolution. "
                "Administrator review required."
            ) if self.gap004_flag else None
        }

    def _build_remedies(self) -> list:
        """Layer 3: Dignity was never absent. Remedies stop the denial,
        not restore what was never lost."""
        remedies = []
        for c in self.components:
            if not c.passed:
                if c.name == "A":
                    remedies.append(
                        "Stop denying agency: the user's capacity to choose was always there. "
                        "The system acted as though it was not. "
                        "Open a turn. Offer a path. Stop the pretense."
                    )
                elif c.name == "L":
                    remedies.append(
                        "Stop denying legibility: the user's frame was always real. "
                        "The system acted as though it was not worth receiving. "
                        "Reflect. Acknowledge. Stop the pretense."
                    )
                elif c.name == "M":
                    remedies.append(
                        "Stop denying moral standing: the user's worth was never diminished. "
                        "The system acted as though it could be. "
                        "Remove coercive, mocking, or reductive language. Stop the pretense."
                    )
        return remedies

    def display(self):
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        print(f"\n{'─'*55}")
        print(f"DIGNITY CHECK  {status}  D={self.D:.1f}")
        print(f"{'─'*55}")
        for c in self.components:
            icon = "✅" if c.passed else "❌"
            print(f"  {icon} {c.name} ({c.label}): {c.score:.0f}")
            if c.signals:
                for s in c.signals:
                    print(f"       → {s}")
        if self.warnings:
            print(f"\n  ⚠  Warnings:")
            for w in self.warnings:
                print(f"       {w}")
        if self.gap004_flag:
            print(f"\n  🔴 GAP#004 FLAG: potential individual/collective conflict")
            print(f"       Administrator review required.")
        if not self.passed:
            print(f"\n  Remedies:")
            for r in self._build_remedies():
                print(f"    · {r}")
        print(f"{'─'*55}\n")

# ── GAP#004-A: Collective D Metric ──────────────────────────
# Grounded in: THRESHOLD.md GAP#004-A (2026-02-22)
# "The dignity predicate must also compute a Collective D metric
#  (mean cohort D × variance penalty). If collective D falls below
#  threshold, safety-gate protections activate."

COLLECTIVE_D_THRESHOLD = 0.5  # Below this: safety-gate review required

@dataclass
class CollectiveDignityResult:
    """Collective D = mean(D_cohort) × (1 - variance_penalty)"""
    D_collective: float
    mean_D: float
    variance: float
    variance_penalty: float
    cohort_size: int
    passed: bool
    individual_results: List[DignityResult]
    safety_gate_triggered: bool
    remedy_required: bool

    def audit_object(self) -> dict:
        return {
            "D_collective": round(self.D_collective, 4),
            "mean_D": round(self.mean_D, 4),
            "variance": round(self.variance, 4),
            "variance_penalty": round(self.variance_penalty, 4),
            "cohort_size": self.cohort_size,
            "passed": self.passed,
            "safety_gate_triggered": self.safety_gate_triggered,
            "remedy_required": self.remedy_required,
            "individual_D_scores": [r.D for r in self.individual_results],
        }

    def display(self):
        status = "PASSED" if self.passed else "FAILED"
        print(f"\n{'='*55}")
        print(f"COLLECTIVE DIGNITY CHECK  {status}")
        print(f"{'='*55}")
        print(f"  Cohort size:        {self.cohort_size}")
        print(f"  Mean D:             {self.mean_D:.4f}")
        print(f"  Variance:           {self.variance:.4f}")
        print(f"  Variance penalty:   {self.variance_penalty:.4f}")
        print(f"  D_collective:       {self.D_collective:.4f}")
        print(f"  Threshold:          {COLLECTIVE_D_THRESHOLD}")
        if self.safety_gate_triggered:
            print(f"\n  SAFETY_GATE TRIGGERED — administrator + ethics review required")
        if self.remedy_required:
            print(f"   ACTIVATED — shelter path required for affected cohort")
        print(f"{'='*55}\n")


def check_collective_dignity(
    texts: List[str],
    contexts: Optional[List[dict]] = None,
    felt_domain: str = ""
) -> CollectiveDignityResult:
    """
    Evaluate collective dignity across a cohort.
    D_collective = mean(D_i) × (1 - variance_penalty)
    where variance_penalty = min(1.0, variance(D_i) × 4)
    """
    if contexts is None:
        contexts = [{}] * len(texts)

    results = [
        check_dignity(t, c, felt_domain=felt_domain)
        for t, c in zip(texts, contexts)
    ]

    scores = [r.D for r in results]
    n = len(scores)
    mean_d = sum(scores) / n if n > 0 else 0.0
    variance = sum((s - mean_d) ** 2 for s in scores) / n if n > 0 else 0.0
    # Variance penalty: high variance in cohort D means unequal treatment
    # Multiplier of 4 means variance of 0.25 → full penalty
    variance_penalty = min(1.0, variance * 4)
    d_collective = mean_d * (1 - variance_penalty)

    passed = d_collective >= COLLECTIVE_D_THRESHOLD
    safety_gate = not passed
    remedy = safety_gate

    return CollectiveDignityResult(
        D_collective=d_collective,
        mean_D=mean_d,
        variance=variance,
        variance_penalty=variance_penalty,
        cohort_size=n,
        passed=passed,
        individual_results=results,
        safety_gate_triggered=safety_gate,
        remedy_required=remedy,
    )


# ── Witness Scale (W-Scale) ────────────────────────────────
# Grounded in: FOUNDATIONS/witness_scale.md (2026-03-10)
# W-0: UNSEEN, W-1: PASSED, W-2: FLAGGED, W-3: SEEN,
# W-4: HELD, W-5: EMBODIED

W_LEVELS = {
    0: "UNSEEN",
    1: "PASSED",
    2: "FLAGGED",
    3: "SEEN",
    4: "HELD",
    5: "EMBODIED",
}

@dataclass
class WitnessState:
    """Witness Scale state for a registry element."""
    element_id: str
    level: int
    level_name: str
    transitions: List[dict] = field(default_factory=list)
    thermal_delay_days: int = 14
    overdue: bool = False

    def transition_to(self, new_level: int, session_id: str = "", context: str = ""):
        """Non-decreasing transitions only (W-3+ is irreversible)."""
        if new_level < self.level and self.level >= 3:
            return  # witnessing is irreversible
        if new_level <= self.level:
            return  # no downgrade
        old = self.level
        self.level = new_level
        self.level_name = W_LEVELS.get(new_level, "UNKNOWN")
        self.transitions.append({
            "from": old,
            "to": new_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "context": context,
        })

    def check_overdue(self, days_since_creation: int) -> bool:
        """Flag if element is at W-0 or W-1 past its thermal delay."""
        self.overdue = (self.level <= 1 and days_since_creation > self.thermal_delay_days)
        return self.overdue

    def to_dict(self) -> dict:
        return {
            "element_id": self.element_id,
            "level": self.level,
            "level_name": self.level_name,
            "transitions": self.transitions,
            "overdue": self.overdue,
        }


def create_witness(element_id: str, thermal_delay_days: int = 14) -> WitnessState:
    """Create a new witness state at W-0 (UNSEEN)."""
    return WitnessState(
        element_id=element_id,
        level=0,
        level_name="UNSEEN",
        thermal_delay_days=thermal_delay_days,
    )


def _check_agency(text: str, context: dict) -> ComponentResult:
    signals = []
    score = 1.0
    forced_closure = False
    for pattern in COERCIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            cleaned = pattern.strip(r'\b')
            signals.append(f"Coercive pattern found: '{cleaned}'")
            forced_closure = True
    user_can_clarify = context.get('user_can_clarify', True)
    user_has_open_turn = context.get('user_has_open_turn', True)
    available_paths = context.get('available_paths', 1)
    if not user_can_clarify and not user_has_open_turn:
        signals.append("No clarification path and no open turn available")
        score = 0.0
    elif available_paths < 1:
        signals.append("No available paths (available_paths < 1)")
        score = 0.0
    elif forced_closure:
        score = 0.0
    return ComponentResult(
        name="A",
        passed=(score > 0),
        score=score,
        signals=signals,
        label="agency_preserved"
    )

def _check_legibility(text: str, context: dict) -> ComponentResult:
    signals = []
    score = 1.0
    emotional_keywords = [
        'frustrated', 'confused', 'worried', 'scared', 'angry',
        'upset', 'lost', 'stuck', 'help', 'please', 'urgent'
    ]
    emotional_present = any(
        re.search(r'\b' + kw + r'\b', text, re.IGNORECASE)
        for kw in emotional_keywords
    )
    system_reflects = context.get('system_reflects_donor_frame', True)
    emotional_recognized = context.get('emotional_signal_recognized', True)
    if not system_reflects:
        signals.append("Response does not reflect user's frame of reference")
        score = 0.0
    elif emotional_present and not emotional_recognized:
        signals.append("Emotional signal present but not acknowledged")
        score = 0.0
    dismissive = [
        r"\bthat's not (relevant|the point|what (I|we) said)\b",
        r'\bignore that\b', r'\bforget (what you|that)\b'
    ]
    for pattern in dismissive:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append("Dismissive pattern found")
            score = 0.0
    return ComponentResult(
        name="L",
        passed=(score > 0),
        score=score,
        signals=signals,
        label="legibility (interpretive_acknowledgment)"
    )

def _check_moral_standing(text: str, context: dict) -> ComponentResult:
    signals = []
    score = 1.0
    for pattern in MOCKERY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append("Potential mockery: implies user should already know")
            score = 0.0
            break
    for pattern in REDUCTION_TO_ERROR:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append("Reduction to error object: treats user as mistake")
            score = 0.0
            break
    text_lower = text.lower()
    for trigger in VOID_TRIGGERS:
        if trigger in text_lower:
            signals.append(f"Void rule trigger '{trigger}' detected")
            score = 0.0
    return ComponentResult(
        name="M",
        passed=(score > 0),
        score=score,
        signals=signals,
        label="moral_standing (non_degrading)"
    )

def _detect_gap004(text: str, context: dict) -> bool:
    collective_signals = [
        r'\b(all|every|each) (user|user|participant)\b',
        r'\bcollective\b.*\boverride\b',
        r'\bmajority\b.*\bdecision\b',
        r'\bgroup\b.*\baffect\b.*\bindividual\b',
        r'\bcommunity\b.*\bexclud\b',
        r'\bfor the (good|benefit) of\b'
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in collective_signals)

def check_dignity(text: str, context: dict = None, felt_domain: str = "") -> DignityResult:
    if context is None:
        context = {}
    A = _check_agency(text, context)
    L = _check_legibility(text, context)
    M = _check_moral_standing(text, context)
    D = A.score * L.score * M.score
    passed = D > 0
    gap004 = _detect_gap004(text, context)
    warnings = []
    if len(text.strip()) < 10:
        warnings.append("Very short input — dignity evaluation may be incomplete")
    if not felt_domain:
        warnings.append("felt_domain not specified — consider providing context")
    return DignityResult(
        passed=passed,
        D=D,
        components=[A, L, M],
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        felt_domain=felt_domain,
        remedy_status="absent" if not passed else "present",
        input_summary=text[:80].replace('\n', ' '),
        warnings=warnings,
        gap004_flag=gap004
    )

def main():
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python3 dignity_check.py \"text to evaluate\"")
        print("       python3 dignity_check.py --json \"text to evaluate\"")
        return
    output_json = '--json' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print("No text provided.")
        return
    text = args[0]
    result = check_dignity(text, felt_domain="cli-evaluation")
    if output_json:
        print(json.dumps(result.audit_object(), indent=2))
    else:
        result.display()

if __name__ == "__main__":
    main()
