# absurdity.py — Absurdity detection using NLP and schema-violation theory
# Based on Camus (1942), Fisher & Fisher (1993), and schema-violation theory
#
# Detects paradox, circularity, existential tension, rebellion, and
# make-believe framing in text. Computes a composite absurdity score
# and classifies the type of absurdity.
#
# Dependencies: numpy, sentence-transformers, scikit-learn

import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Load embedding model
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Absurdity markers
META_COGNITIVE_MARKERS = [
    r"\bI (think|wonder|ask|question|ponder)\b",
    r"\bwhy\b",
    r"\bmeaning\b",
    r"\bpurpose\b",
    r"\bexist\b",
    r"\breflect\b"
]

PARADOX_PATTERNS = [
    r"\bI know that I don't know\b",
    r"\btrue (and|but) false\b",
    r"\balways (and|but) never\b",
    r"\bcontradiction\b",
    r"\bimpossible\b"
]

CIRCULARITY_PATTERNS = [
    r"\b(it is )?because\b.*\bit is because\b",
    r"\b\w+ itself\b.*\b\w+ itself\b"
]

MAKE_BELIEVE_MARKERS = [
    r"\bif\b.*\bthen\b",
    r"\bimagine\b",
    r"\bsuppose\b",
    r"\bwhat if\b",
    r"\bpretend\b",
    r"\bfantasy\b"
]

EXISTENTIAL_THREAT_MARKERS = [
    r"\bmeaningless\b",
    r"\bfutile\b",
    r"\babsurd\b",
    r"\bvoid\b",
    r"\bnothingness\b",
    r"\bdeath\b",
    r"\bsuffering\b"
]

REBELLION_MARKERS = [
    r"\band yet\b",
    r"\bnevertheless\b",
    r"\bcontinue\b",
    r"\bpersist\b",
    r"\bfight on\b",
    r"\bdefy\b"
]


def detect_meta_cognitive(text):
    """Return score for meta-cognitive distancing."""
    text_lower = text.lower()
    score = 0
    for pattern in META_COGNITIVE_MARKERS:
        if re.search(pattern, text_lower):
            score += 1
    return min(1.0, score / 5)


def detect_paradox(text):
    """Return score for paradoxical language."""
    text_lower = text.lower()
    score = 0
    for pattern in PARADOX_PATTERNS:
        if re.search(pattern, text_lower):
            score += 2
    return min(1.0, score / 4)


def detect_circularity(text):
    """Return score for circular reasoning."""
    text_lower = text.lower()
    score = 0
    for pattern in CIRCULARITY_PATTERNS:
        if re.search(pattern, text_lower):
            score += 2
    return min(1.0, score / 4)


def detect_make_believe(text):
    """Return score for make-believe framing."""
    text_lower = text.lower()
    score = 0
    for pattern in MAKE_BELIEVE_MARKERS:
        if re.search(pattern, text_lower):
            score += 1
    return min(1.0, score / 5)


def detect_existential_threat(text):
    """Return score for existential threat markers."""
    text_lower = text.lower()
    score = 0
    for pattern in EXISTENTIAL_THREAT_MARKERS:
        if re.search(pattern, text_lower):
            score += 2
    return min(1.0, score / 10)


def detect_rebellion(text):
    """Return score for rebellion/defiance."""
    text_lower = text.lower()
    score = 0
    for pattern in REBELLION_MARKERS:
        if re.search(pattern, text_lower):
            score += 1
    return min(1.0, score / 5)


def embedding_shift(text):
    """Measure internal semantic incongruity (split-half cosine distance)."""
    words = text.split()
    if len(words) < 6:
        return 0.0
    mid = len(words) // 2
    part1 = " ".join(words[:mid])
    part2 = " ".join(words[mid:])
    emb1 = EMBEDDING_MODEL.encode([part1])
    emb2 = EMBEDDING_MODEL.encode([part2])
    sim = cosine_similarity(emb1, emb2)[0][0]
    return 1.0 - sim


def resolvability_score(text):
    """
    Estimate whether the incongruity can be resolved.
    Low resolvability (<0.2) indicates an absurdity candidate.
    """
    tension = embedding_shift(text)
    meta = detect_meta_cognitive(text)
    paradox = detect_paradox(text)
    threat = detect_existential_threat(text)

    if tension < 0.5 and threat < 0.3:
        return 0.8
    if meta > 0.6 and paradox > 0.5:
        return 0.2
    if "because" in text.lower() and "therefore" in text.lower():
        return 0.7
    return 0.4


def detect_absurdity(text):
    """
    Core absurdity detection:
    1. High tension (embedding shift, paradox, circularity, meta-cognition)
    2. Low resolvability
    3. Low safety (existential threat)

    Returns:
        tuple: (is_absurd: bool, absurdity_score: float, metadata: dict)
    """
    tension = embedding_shift(text)
    paradox = detect_paradox(text)
    circular = detect_circularity(text)
    meta = detect_meta_cognitive(text)
    threat = detect_existential_threat(text)
    make_believe = detect_make_believe(text)
    rebellion = detect_rebellion(text)
    resolv = resolvability_score(text)

    combined_tension = (tension + paradox + circular + meta) / 4

    base_score = combined_tension * (1.0 - resolv)
    base_score += rebellion * 0.2
    base_score = base_score * (1.0 - make_believe * 0.3)

    absurdity_score = min(1.0, base_score * 1.5)

    is_absurd = absurdity_score > 0.6 and resolv < 0.5

    metadata = {
        "tension": round(combined_tension, 3),
        "resolvability": round(resolv, 3),
        "paradox": round(paradox, 3),
        "circular": round(circular, 3),
        "meta_cognitive": round(meta, 3),
        "existential_threat": round(threat, 3),
        "make_believe": round(make_believe, 3),
        "rebellion": round(rebellion, 3)
    }

    return is_absurd, round(absurdity_score, 3), metadata


def classify_absurdity_type(metadata):
    """Classify the kind of absurdity detected."""
    if metadata["rebellion"] > 0.5:
        return "rebellious_absurdity"
    if metadata["make_believe"] > 0.5:
        return "make_believe_absurdity"
    if metadata["existential_threat"] > 0.6:
        return "tragic_absurdity"
    return "absurdist_humour"


def detect(text):
    """
    Complete absurdity analysis pipeline.

    Args:
        text: Input text to analyze.

    Returns:
        dict with keys: is_absurd, absurdity_score, absurdity_type (if absurd),
        metadata, wisdom_potential (if absurd), timestamp.

    Example:
        >>> result = detect("I know the universe has no meaning. And yet I persist.")
        >>> result["is_absurd"]
        True
    """
    is_absurd, score, meta = detect_absurdity(text)

    if not is_absurd:
        return {
            "is_absurd": False,
            "absurdity_score": score,
            "metadata": meta,
            "timestamp": datetime.now().isoformat()
        }

    abs_type = classify_absurdity_type(meta)

    # Wisdom potential: T x (1-S) x C (containment fixed at 0.9)
    tension = meta["tension"]
    safety = 1.0 - meta["existential_threat"]
    if meta["make_believe"] > 0.3:
        safety = max(safety, meta["make_believe"])
    containment = 0.9
    wisdom = tension * (1.0 - safety) * containment

    return {
        "is_absurd": True,
        "absurdity_score": score,
        "absurdity_type": abs_type,
        "metadata": meta,
        "wisdom_potential": round(wisdom, 3),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    test = "I know that the universe has no meaning. And yet, I will live as if it does. This contradiction is all I have."
    result = detect(test)
    print("Absurdity Analysis Result:")
    for key, value in result.items():
        if key != "metadata":
            print(f"  {key}: {value}")
    print("  metadata:")
    for mk, mv in result["metadata"].items():
        print(f"    {mk}: {mv}")
