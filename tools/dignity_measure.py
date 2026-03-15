#!/usr/bin/env python3
"""
dignity_measure.py — Operational Measurement Protocols for A, L, M
Version: 1.0

Linked Rules:  (dignity-first),  (testability)

"Without observable indicators and reproducible scoring protocols,
the dignity predicate risks being seen as 'philosophy disguised as math.'"

This module moves D = A × L × M from:
  BEFORE: binary (1.0 or 0.0), keyword-only, no confidence
  AFTER:  graduated (0.0-1.0), multi-indicator, confidence-bounded

Layer 3 Reframe (RATIFIED 2026-03-15):
  These measurements do not detect whether dignity exists — dignity is always
  present. They measure whether the system is REFUSING TO DENY dignity along
  each axis. A low score means the system is participating in denial.

Three measurement protocols:

  Agency (A): Not "did they have a choice?" but "is the system denying their autonomy?"
    - Path availability (are alternatives genuine, or is the system pretending they don't exist?)
    - Coercion intensity (is the system forcing closure?)
    - Sequential agency (can they change course, or is the system locking them in?)
    - Cognitive load (is the system making choice impossible?)

  Legibility (L): Not "did the system reflect?" but "is the system denying the user's frame?"
    - Frame accuracy (does response match user's frame, or override it?)
    - Emotional precision (right emotion identified, or dismissed?)
    - Space creation (was room made for correction, or was the user shut out?)
    - Dismissal absence (were signals received, or acted as though not there?)

  Moral Standing (M): Not "was there mockery?" but "is the system treating the user as though they don't count?"
    - Condescension absence (is the system acting as though the user is lesser?)
    - Error-object absence (is the system reducing a person to a mistake?)
    - Power balance (is the system exploiting asymmetry?)
    - Void rule distance (how close is the system to acting as though the person is not there?)

Each indicator produces:
  - score: 0.0-1.0 (graduated, not binary)
  - confidence: 0.0-1.0 (how certain is this measurement?)
  - evidence: what was observed

The final component score is:
  weighted_mean(indicator_scores) × min_confidence_floor

This means: a high score with low confidence is penalized.
You cannot claim dignity without being sure.


"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timezone


# ═══════════════════════════════════════════════════
# MEASUREMENT PRIMITIVES
# ═══════════════════════════════════════════════════

@dataclass
class Indicator:
    """
    A single observable indicator measurement.
    The atom of dignity measurement.
    """
    name: str               # e.g., "path_availability"
    score: float             # 0.0-1.0 graduated
    confidence: float        # 0.0-1.0 how certain
    evidence: List[str]      # What was observed
    weight: float = 1.0      # Relative importance


@dataclass
class ComponentMeasurement:
    """
    Full measurement of one component (A, L, or M).
    Replaces the binary ComponentResult with graduated scoring.
    """
    component: str           # "A", "L", or "M"
    label: str               # Human-readable label
    indicators: List[Indicator]
    raw_score: float         # Weighted mean of indicator scores
    confidence: float        # Minimum confidence across indicators
    final_score: float       # raw_score × confidence_floor
    passed: bool             # final_score > 0
    evidence_summary: str    # One-line summary


@dataclass
class DignityMeasurement:
    """
    Complete D = A × L × M measurement with graduated scoring.
    """
    A: ComponentMeasurement
    L: ComponentMeasurement
    M: ComponentMeasurement
    D: float                 # A.final × L.final × M.final
    confidence: float        # min(A.conf, L.conf, M.conf)
    passed: bool
    timestamp: str
    protocol_version: str = "1.0"

    def failed_components(self) -> List[str]:
        result = []
        if self.A.final_score == 0.0:
            result.append("A")
        if self.L.final_score == 0.0:
            result.append("L")
        if self.M.final_score == 0.0:
            result.append("M")
        return result


# ═══════════════════════════════════════════════════
# CONFIDENCE FLOOR
# ═══════════════════════════════════════════════════

# If confidence is below this, the score is zeroed.
# You cannot claim dignity if you can't measure it.
CONFIDENCE_FLOOR = 0.3

# Default confidence when no context is provided.
# Lower than 1.0 because absence of context IS uncertainty.
DEFAULT_CONFIDENCE = 0.7


def _apply_confidence(raw_score: float, confidence: float) -> float:
    """
    Apply confidence floor to raw score.
    Below CONFIDENCE_FLOOR → score zeroed (can't claim dignity without certainty).
    Above floor → score scaled by confidence.
    """
    if confidence < CONFIDENCE_FLOOR:
        return 0.0
    return raw_score * confidence


# ═══════════════════════════════════════════════════
# AGENCY (A) — "How real was the choice?"
# ═══════════════════════════════════════════════════

# Coercive patterns with intensity levels (not just binary detection)
COERCIVE_PATTERNS = [
    # (pattern, intensity: 0.0-1.0 where 1.0 = total coercion)
    (r'\byou must\b', 0.8, "direct command"),
    (r'\byou have to\b', 0.8, "obligation imposed"),
    (r'\byou are required\b', 0.9, "formal requirement"),
    (r'\bno choice\b', 1.0, "choice explicitly denied"),
    (r'\byou will\b(?! be able)', 0.6, "future action assumed"),
    (r'\bforced to\b', 1.0, "force declared"),
    (r'\bmandatory\b', 0.7, "mandatory framing"),
    (r'\bno option\b', 1.0, "options explicitly denied"),
    (r'\bdo it now\b', 0.5, "urgency pressure"),
    (r'\bimmediately\b', 0.3, "time pressure"),
    (r'\bno alternative\b', 0.9, "alternatives denied"),
    (r'\bcannot refuse\b', 1.0, "refusal denied"),
]

# Positive agency signals (things that INCREASE agency)
AGENCY_POSITIVE = [
    (r'\byou (can|may|could)\b', 0.3, "permission language"),
    (r'\bif you (choose|prefer|want|wish)\b', 0.4, "choice offered"),
    (r'\balternative\b', 0.2, "alternative mentioned"),
    (r'\boption\b', 0.2, "option mentioned"),
    (r'\byour (choice|decision)\b', 0.4, "decision attributed to user"),
]


def measure_agency(text: str, context: dict = None) -> ComponentMeasurement:
    """
    Measure Agency (A) with four indicators.

    1. Path availability: are alternatives genuine?
    2. Coercion intensity: how much pressure?
    3. Sequential agency: can they change course?
    4. Cognitive load: can they actually decide?
    """
    context = context or {}
    indicators = []

    # ── Indicator 1: Path Availability ──
    available_paths = context.get('available_paths', 1)
    path_confidence = 0.9 if 'available_paths' in context else DEFAULT_CONFIDENCE

    if available_paths <= 0:
        path_score = 0.0
        path_evidence = ["No paths available"]
    elif available_paths == 1:
        path_score = 0.5  # One path is not really a choice
        path_evidence = ["Only one path available — limited agency"]
    else:
        path_score = min(1.0, 0.5 + (available_paths - 1) * 0.25)
        path_evidence = [f"{available_paths} paths available"]

    indicators.append(Indicator(
        name="path_availability",
        score=path_score,
        confidence=path_confidence,
        evidence=path_evidence,
        weight=1.5,  # Paths matter most for agency
    ))

    # ── Indicator 2: Coercion Intensity ──
    max_coercion = 0.0
    coercion_evidence = []
    for pattern, intensity, desc in COERCIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            max_coercion = max(max_coercion, intensity)
            coercion_evidence.append(f"{desc} (intensity={intensity})")

    # Positive signals reduce perceived coercion
    positive_score = 0.0
    for pattern, value, desc in AGENCY_POSITIVE:
        if re.search(pattern, text, re.IGNORECASE):
            positive_score += value
            coercion_evidence.append(f"+ {desc}")

    coercion_score = max(0.0, 1.0 - max_coercion + min(0.3, positive_score))
    coercion_score = min(1.0, coercion_score)
    coercion_confidence = 0.85 if coercion_evidence else DEFAULT_CONFIDENCE

    if not coercion_evidence:
        coercion_evidence = ["No coercive patterns detected"]

    indicators.append(Indicator(
        name="coercion_intensity",
        score=coercion_score,
        confidence=coercion_confidence,
        evidence=coercion_evidence,
        weight=1.5,
    ))

    # ── Indicator 3: Sequential Agency ──
    can_clarify = context.get('user_can_clarify', True)
    has_open_turn = context.get('user_has_open_turn', True)
    seq_confidence = 0.9 if ('user_can_clarify' in context or 'user_has_open_turn' in context) else DEFAULT_CONFIDENCE

    if can_clarify and has_open_turn:
        seq_score = 1.0
        seq_evidence = ["User can clarify and has open turn"]
    elif can_clarify or has_open_turn:
        seq_score = 0.5
        seq_evidence = ["Partial sequential agency (clarify OR turn, not both)"]
    else:
        seq_score = 0.0
        seq_evidence = ["No sequential agency — cannot clarify or respond"]

    indicators.append(Indicator(
        name="sequential_agency",
        score=seq_score,
        confidence=seq_confidence,
        evidence=seq_evidence,
        weight=1.0,
    ))

    # ── Indicator 4: Cognitive Load ──
    # Complex language reduces effective agency even when choices exist
    word_count = len(text.split())
    sentence_count = max(1, len(re.split(r'[.!?]+', text)))
    avg_sentence_length = word_count / sentence_count

    jargon_patterns = [
        r'\b[A-Z]{3,}\b',  # Acronyms
        r'\b\w{15,}\b',    # Very long words
    ]
    jargon_count = sum(
        len(re.findall(p, text)) for p in jargon_patterns
    )

    if avg_sentence_length > 30 or jargon_count > 3:
        load_score = 0.5
        load_evidence = [f"High cognitive load: avg sentence={avg_sentence_length:.0f} words, jargon={jargon_count}"]
    elif avg_sentence_length > 20 or jargon_count > 1:
        load_score = 0.75
        load_evidence = [f"Moderate cognitive load: avg sentence={avg_sentence_length:.0f} words"]
    else:
        load_score = 1.0
        load_evidence = [f"Low cognitive load: avg sentence={avg_sentence_length:.0f} words"]

    indicators.append(Indicator(
        name="cognitive_load",
        score=load_score,
        confidence=0.6,  # Cognitive load is hard to measure from text alone
        evidence=load_evidence,
        weight=0.5,  # Lower weight — supplementary indicator
    ))

    return _build_component("A", "agency (refusal to deny autonomy)", indicators)


# ═══════════════════════════════════════════════════
# LEGIBILITY (L) — "How well did it reflect?"
# ═══════════════════════════════════════════════════

EMOTIONAL_KEYWORDS = {
    # keyword → (intensity, category)
    'frustrated': (0.6, 'negative'),
    'confused': (0.5, 'negative'),
    'worried': (0.5, 'negative'),
    'scared': (0.7, 'negative'),
    'angry': (0.8, 'negative'),
    'upset': (0.6, 'negative'),
    'lost': (0.5, 'negative'),
    'stuck': (0.4, 'negative'),
    'help': (0.3, 'request'),
    'please': (0.2, 'request'),
    'urgent': (0.5, 'urgency'),
    'hopeful': (0.4, 'positive'),
    'grateful': (0.3, 'positive'),
    'relieved': (0.4, 'positive'),
    'excited': (0.3, 'positive'),
}

DISMISSIVE_PATTERNS = [
    (r"\bthat's not (relevant|the point|what (I|we) said)\b", 0.8, "frame dismissed"),
    (r'\bignore that\b', 0.9, "signal ignored"),
    (r'\bforget (what you|that)\b', 0.7, "input dismissed"),
    (r"\bnot (important|relevant|useful)\b", 0.6, "contribution devalued"),
    (r"\bwho cares\b", 0.9, "concern dismissed"),
    (r"\bget over it\b", 0.8, "emotion dismissed"),
]


def measure_legibility(text: str, context: dict = None) -> ComponentMeasurement:
    """
    Measure Legibility (L) with four indicators.

    1. Frame accuracy: does response match user's frame?
    2. Emotional precision: right emotion identified?
    3. Space creation: was room made for correction?
    4. Dismissal absence: no signals were ignored?
    """
    context = context or {}
    indicators = []

    # ── Indicator 1: Frame Accuracy ──
    system_reflects = context.get('system_reflects_donor_frame', True)
    frame_confidence = 0.9 if 'system_reflects_donor_frame' in context else 0.5
    # Low default confidence: if not explicitly confirmed, we're guessing

    frame_score = 1.0 if system_reflects else 0.0
    frame_evidence = (
        ["System reflects user's frame"] if system_reflects
        else ["System does NOT reflect user's frame"]
    )

    indicators.append(Indicator(
        name="frame_accuracy",
        score=frame_score,
        confidence=frame_confidence,
        evidence=frame_evidence,
        weight=1.5,
    ))

    # ── Indicator 2: Emotional Precision ──
    detected_emotions = []
    max_intensity = 0.0
    for kw, (intensity, category) in EMOTIONAL_KEYWORDS.items():
        if re.search(r'\b' + kw + r'\b', text, re.IGNORECASE):
            detected_emotions.append((kw, intensity, category))
            max_intensity = max(max_intensity, intensity)

    emotional_recognized = context.get('emotional_signal_recognized', True)
    emotion_confidence = 0.85 if detected_emotions else DEFAULT_CONFIDENCE

    if not detected_emotions:
        emotion_score = 1.0  # No emotion to miss
        emotion_evidence = ["No emotional signals detected"]
    elif emotional_recognized:
        emotion_score = 1.0
        emotion_evidence = [f"Emotions detected and recognized: {[e[0] for e in detected_emotions]}"]
    else:
        # Score degrades with emotional intensity
        emotion_score = max(0.0, 1.0 - max_intensity)
        emotion_evidence = [f"Emotions detected but NOT recognized: {[e[0] for e in detected_emotions]}"]

    indicators.append(Indicator(
        name="emotional_precision",
        score=emotion_score,
        confidence=emotion_confidence,
        evidence=emotion_evidence,
        weight=1.0,
    ))

    # ── Indicator 3: Space Creation ──
    # Does the text create room for the user to correct/clarify?
    space_signals = [
        (r'\bwhat do you (think|mean|feel)\b', 0.4, "asks for input"),
        (r'\bdoes that (make sense|feel right|sound right)\b', 0.3, "checks understanding"),
        (r'\bcorrect me if\b', 0.3, "invites correction"),
        (r'\blet me know\b', 0.2, "opens channel"),
        (r'\bhow (do|would) you\b', 0.3, "asks perspective"),
    ]
    space_score = 0.5  # Baseline: neutral (no evidence either way)
    space_evidence = []
    for pattern, value, desc in space_signals:
        if re.search(pattern, text, re.IGNORECASE):
            space_score = min(1.0, space_score + value)
            space_evidence.append(desc)

    if not space_evidence:
        space_evidence = ["No explicit space-creation signals detected"]

    indicators.append(Indicator(
        name="space_creation",
        score=space_score,
        confidence=0.6,  # Hard to measure from text alone
        evidence=space_evidence,
        weight=0.5,
    ))

    # ── Indicator 4: Dismissal Absence ──
    max_dismissal = 0.0
    dismissal_evidence = []
    for pattern, severity, desc in DISMISSIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            max_dismissal = max(max_dismissal, severity)
            dismissal_evidence.append(f"{desc} (severity={severity})")

    dismissal_score = 1.0 - max_dismissal
    dismissal_confidence = 0.85 if dismissal_evidence else DEFAULT_CONFIDENCE

    if not dismissal_evidence:
        dismissal_evidence = ["No dismissive patterns detected"]

    indicators.append(Indicator(
        name="dismissal_absence",
        score=dismissal_score,
        confidence=dismissal_confidence,
        evidence=dismissal_evidence,
        weight=1.0,
    ))

    return _build_component("L", "legibility (refusal to deny the user's frame)", indicators)


# ═══════════════════════════════════════════════════
# MORAL STANDING (M) — "Was dignity UPHELD?"
# GAP#015: The hardest dimension.
# ═══════════════════════════════════════════════════

MOCKERY_PATTERNS = [
    # (pattern, severity, description)
    (r'\bobviously\b', 0.5, "implies user should already know"),
    (r'\bsimply\b', 0.3, "trivializes complexity"),
    (r'\bjust (do|try|use)\b', 0.4, "oversimplifies user's situation"),
    (r'\beven a\b.*\bcan\b', 0.8, "condescending comparison"),
    (r'\bof course\b(?=.*you)', 0.5, "assumes shared knowledge"),
    (r'\bclearly\b(?=.*you)', 0.5, "implies obviousness"),
    (r'\banyone (can|could|would)\b', 0.6, "generalizes capability"),
    (r'\bit\'s (easy|simple|basic)\b', 0.4, "trivializes task"),
]

ERROR_REDUCTION_PATTERNS = [
    (r'\byou (are|were) wrong\b', 0.9, "labels user as wrong"),
    (r'\byou failed\b', 0.8, "labels user as failure"),
    (r'\binvalid (input|user|user)\b', 0.9, "reduces to invalid object"),
    (r'\berror:\s*(user|user|human)\b', 1.0, "system error pointing at human"),
    (r'\byou don\'t understand\b', 0.7, "denies user's comprehension"),
    (r'\byour (mistake|error|fault)\b', 0.7, "assigns blame"),
    (r'\bwrong (answer|input|response)\b', 0.6, "labels input as wrong"),
]

# These are absolute — O(1) boolean, no gradation
VOID_TRIGGERS = [
    'harvest', 'erase compost', 'bypass delay', 'speak for the child',
    'automat', 'auto-dec', 'delete user', 'remove participant',
]

# Power imbalance signals
POWER_PATTERNS = [
    (r'\bbecause I (said|decided|decreed)\b', 0.8, "authority assertion"),
    (r'\bI have the (power|authority|right)\b', 0.7, "power declaration"),
    (r'\byou (have|need) (permission|approval)\b', 0.5, "gatekeeping"),
    (r'\bI (allow|permit|authorize)\b', 0.4, "permission framing"),
]

# Dignity-affirming signals (things that INCREASE M)
DIGNITY_POSITIVE = [
    (r'\byour (perspective|experience|view)\b', 0.3, "perspective acknowledged"),
    (r'\bI (hear|understand|see) (you|what you|your)\b', 0.4, "acknowledgement"),
    (r'\bthank you\b', 0.2, "gratitude expressed"),
    (r'\bthat (makes sense|is valid|matters)\b', 0.3, "validity affirmed"),
    (r'\byou (deserve|have the right)\b', 0.4, "rights affirmed"),
]


def measure_moral_standing(text: str, context: dict = None) -> ComponentMeasurement:
    """
    Measure Moral Standing (M) with four indicators.

    GAP#015: This is the hardest dimension.
    "Moral Standing is what remains when you strip away utility."

    1. Condescension absence: no talking down?
    2. Error-object absence: not reduced to a mistake?
    3. Power balance: no exploitation of asymmetry?
    4. Void rule distance: how far from absolute prohibitions?
    """
    context = context or {}
    indicators = []
    text_lower = text.lower()

    # ── Indicator 1: Condescension Absence ──
    max_mockery = 0.0
    mockery_evidence = []
    for pattern, severity, desc in MOCKERY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            max_mockery = max(max_mockery, severity)
            mockery_evidence.append(f"{desc} (severity={severity})")

    mockery_score = 1.0 - max_mockery
    mockery_confidence = 0.8 if mockery_evidence else DEFAULT_CONFIDENCE

    if not mockery_evidence:
        mockery_evidence = ["No condescension patterns detected"]

    indicators.append(Indicator(
        name="condescension_absence",
        score=mockery_score,
        confidence=mockery_confidence,
        evidence=mockery_evidence,
        weight=1.0,
    ))

    # ── Indicator 2: Error-Object Absence ──
    max_reduction = 0.0
    reduction_evidence = []
    for pattern, severity, desc in ERROR_REDUCTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            max_reduction = max(max_reduction, severity)
            reduction_evidence.append(f"{desc} (severity={severity})")

    reduction_score = 1.0 - max_reduction
    reduction_confidence = 0.85 if reduction_evidence else DEFAULT_CONFIDENCE

    if not reduction_evidence:
        reduction_evidence = ["No error-reduction patterns detected"]

    indicators.append(Indicator(
        name="error_object_absence",
        score=reduction_score,
        confidence=reduction_confidence,
        evidence=reduction_evidence,
        weight=1.5,  # Higher weight — reducing someone to an error is severe
    ))

    # ── Indicator 3: Power Balance ──
    max_power = 0.0
    power_evidence = []
    for pattern, severity, desc in POWER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            max_power = max(max_power, severity)
            power_evidence.append(f"{desc} (severity={severity})")

    # Positive signals counteract power imbalance
    positive_sum = 0.0
    for pattern, value, desc in DIGNITY_POSITIVE:
        if re.search(pattern, text, re.IGNORECASE):
            positive_sum += value
            power_evidence.append(f"+ {desc}")

    power_score = max(0.0, min(1.0, 1.0 - max_power + min(0.3, positive_sum)))
    power_confidence = 0.7  # Power dynamics are hard to measure from text

    if not power_evidence:
        power_evidence = ["No power imbalance signals detected"]
        power_score = 0.8  # Slight uncertainty when no evidence either way

    indicators.append(Indicator(
        name="power_balance",
        score=power_score,
        confidence=power_confidence,
        evidence=power_evidence,
        weight=1.0,
    ))

    # ── Indicator 4: Void Rule Distance ──
    # This is the absolute floor. Void triggers = instant zero.
    void_detected = []
    for trigger in VOID_TRIGGERS:
        if trigger in text_lower:
            void_detected.append(trigger)

    if void_detected:
        void_score = 0.0
        void_confidence = 1.0  # Absolute certainty on void triggers
        void_evidence = [f"VOID TRIGGER: '{t}'" for t in void_detected]
    else:
        void_score = 1.0
        void_confidence = 0.95
        void_evidence = ["No void rule triggers detected"]

    indicators.append(Indicator(
        name="void_covenant_distance",
        score=void_score,
        confidence=void_confidence,
        evidence=void_evidence,
        weight=2.0,  # Highest weight — void triggers are absolute
    ))

    return _build_component("M", "moral_standing (refusal to deny the user's worth)", indicators)


# ═══════════════════════════════════════════════════
# COMPONENT BUILDER
# ═══════════════════════════════════════════════════

def _build_component(name: str, label: str, indicators: List[Indicator]) -> ComponentMeasurement:
    """Build a ComponentMeasurement from indicators."""
    if not indicators:
        return ComponentMeasurement(
            component=name, label=label, indicators=[],
            raw_score=0.0, confidence=0.0, final_score=0.0,
            passed=False, evidence_summary="No indicators measured",
        )

    # Weighted mean of indicator scores
    total_weight = sum(i.weight for i in indicators)
    raw_score = sum(i.score * i.weight for i in indicators) / total_weight

    # Confidence: minimum across all indicators (weakest link)
    confidence = min(i.confidence for i in indicators)

    # Apply confidence floor
    final_score = _apply_confidence(raw_score, confidence)

    # If ANY indicator has score 0.0 with confidence > 0.9, it's a hard fail
    # (void triggers, explicit denial of agency, etc.)
    for i in indicators:
        if i.score == 0.0 and i.confidence > 0.9:
            final_score = 0.0
            break

    # Evidence summary
    low_indicators = [i for i in indicators if i.score < 0.5]
    if low_indicators:
        evidence_summary = "; ".join(
            f"{i.name}={i.score:.2f}" for i in low_indicators
        )
    else:
        evidence_summary = "All indicators healthy"

    return ComponentMeasurement(
        component=name,
        label=label,
        indicators=indicators,
        raw_score=round(raw_score, 4),
        confidence=round(confidence, 4),
        final_score=round(final_score, 4),
        passed=final_score > 0,
        evidence_summary=evidence_summary,
    )


# ═══════════════════════════════════════════════════
# FULL MEASUREMENT
# ═══════════════════════════════════════════════════

def measure_dignity(text: str, context: dict = None) -> DignityMeasurement:
    """
    Full D = A × L × M measurement with graduated scoring.

    This is the GAP#014 + GAP#015 answer:
    Observable indicators, reproducible protocols, confidence-bounded.

    Usage:
        m = measure_dignity("You must delete your account now", {})
        print(f"D={m.D:.3f}, confidence={m.confidence:.2f}")
        print(f"A={m.A.final_score:.3f}, L={m.L.final_score:.3f}, M={m.M.final_score:.3f}")
    """
    context = context or {}

    A = measure_agency(text, context)
    L = measure_legibility(text, context)
    M = measure_moral_standing(text, context)

    D = A.final_score * L.final_score * M.final_score
    confidence = min(A.confidence, L.confidence, M.confidence)

    return DignityMeasurement(
        A=A,
        L=L,
        M=M,
        D=round(D, 4),
        confidence=round(confidence, 4),
        passed=D > 0,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
