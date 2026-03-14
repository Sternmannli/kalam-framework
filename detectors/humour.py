# humour.py — Humour detection based on Benign Violation Theory
# Based on McGraw & Warren (2010) and NLP incongruity measures
#
# Detects semantic incongruity, classifies humour type (affiliative,
# self-enhancing, aggressive, self-defeating), and scores safety.
#
# Dependencies: transformers, torch, sentence-transformers, scikit-learn

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Load pre-trained emotion model
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
emotion_tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL)
emotion_model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL)

# Load embedding model for incongruity
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

EMOTION_LABELS = ["admiration", "joy", "love", "desire", "trust",
                  "fear", "anger", "sadness", "disgust", "surprise"]

SELF_DEPRECATION_PATTERNS = [
    r"\bI am (bad|terrible|useless|wrong|stupid)\b",
    r"\bmy fault\b",
    r"\bof course I\b",
    r"\bI can't (even|believe|help)\b"
]

PROTECTED_CATEGORY_PATTERNS = [
    r"\brace\b", r"\breligion\b", r"\bgender\b", r"\bsexuality\b",
    r"\bdisability\b", r"\bpolitics\b", r"\b(ethnic|race)\b"
]

PLAY_SIGNALS = [
    r"\blol\b", r"\blmao\b", r"\b😂", r"\b😅", r"\b😄",
    r"\bjoke\b", r"\bfunny\b", r"\bjust kidding\b", r"\bsilly\b"
]


def contains_self_deprecation(text):
    """Return True if text contains self-deprecating language."""
    text_lower = text.lower()
    for pattern in SELF_DEPRECATION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def contains_protected_target(text):
    """Return True if text targets protected categories."""
    text_lower = text.lower()
    for pattern in PROTECTED_CATEGORY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def contains_play_signal(text):
    """Return True if text contains play markers."""
    text_lower = text.lower()
    for signal in PLAY_SIGNALS:
        if signal in text_lower or signal in text:
            return True
    return False


def embedding_shift(text):
    """
    Measure internal semantic tension by splitting text into two halves
    and calculating embedding distance. Higher = more incongruity.
    """
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


def surprisal_score(text):
    """
    Estimate prediction error: how unexpected is this text?
    Simplified: uses proportion of rare words.
    """
    common_words = set(["the", "and", "is", "in", "to", "of", "that", "for", "on", "with"])
    words = set(re.findall(r'\b\w+\b', text.lower()))
    rare = words - common_words
    return min(1.0, len(rare) / 20)


def detect_benign_violation(text):
    """
    Core humour signal based on Benign Violation Theory:
    1. Semantic incongruity (embedding_shift)
    2. No protected targeting
    3. Prefer self-directed or abstract tension
    4. Play signals increase safety

    Returns:
        tuple: (is_humour: bool, bv_score: float, metadata: dict)
    """
    tension = embedding_shift(text)
    if tension < 0.35:
        return False, 0.0, {"reason": "insufficient_incongruity"}

    if contains_protected_target(text):
        return False, tension, {"reason": "protected_target", "tension": tension}

    safety = 0.5
    if contains_self_deprecation(text):
        safety += 0.2
    if contains_play_signal(text):
        safety += 0.3

    surprisal = surprisal_score(text)

    bv_score = (tension * 0.6 + surprisal * 0.4) * safety
    bv_score = min(1.0, bv_score)

    return True, round(bv_score, 3), {
        "tension": round(tension, 3),
        "safety": round(safety, 3),
        "surprisal": round(surprisal, 3)
    }


def classify_humour_type(text):
    """
    Classify humour using emotion model and lexical features.
    Based on Martin et al. (2003) Humor Styles Questionnaire.

    Returns:
        tuple: (humour_type: str, emotion_profile: dict)
        Types: affiliative, self_enhancing, aggressive, self_defeating, complex
    """
    inputs = emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = emotion_model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
    emotion_dict = {EMOTION_LABELS[i]: scores[i] * 100 for i in range(len(EMOTION_LABELS))}

    affiliative_score = emotion_dict.get("joy", 0) + emotion_dict.get("admiration", 0) - emotion_dict.get("anger", 0) - emotion_dict.get("fear", 0)
    self_enhancing_score = emotion_dict.get("joy", 0) + emotion_dict.get("admiration", 0) - emotion_dict.get("sadness", 0) - emotion_dict.get("fear", 0)
    aggressive_score = emotion_dict.get("anger", 0) + emotion_dict.get("disgust", 0) - emotion_dict.get("joy", 0)
    self_defeating_score = emotion_dict.get("sadness", 0) + emotion_dict.get("fear", 0) - emotion_dict.get("joy", 0)

    if contains_self_deprecation(text):
        self_defeating_score += 20

    scores_dict = {
        "affiliative": affiliative_score,
        "self_enhancing": self_enhancing_score,
        "aggressive": aggressive_score,
        "self_defeating": self_defeating_score
    }

    max_type = max(scores_dict, key=scores_dict.get)
    if scores_dict[max_type] < 30:
        return "complex", emotion_dict
    return max_type, emotion_dict


def detect(text):
    """
    Complete humour analysis pipeline.

    Args:
        text: Input text to analyze.

    Returns:
        dict with keys: is_humour, bv_score, humour_type (if humour),
        emotion_profile (if humour), tension, safety, timestamp.

    Example:
        >>> result = detect("I'm reading a book on anti-gravity. Impossible to put down!")
        >>> result["is_humour"]
        True
    """
    is_humour, bv_score, bv_meta = detect_benign_violation(text)

    if not is_humour:
        return {
            "is_humour": False,
            "bv_score": bv_score,
            "reason": bv_meta.get("reason", "unknown"),
            "timestamp": datetime.now().isoformat()
        }

    humour_type, emotions = classify_humour_type(text)

    tension = bv_meta["tension"]
    safety = bv_meta["safety"]
    if humour_type in ["aggressive", "self_defeating"]:
        containment = 0.6
    else:
        containment = 0.3

    wisdom_potential = tension * safety * containment

    return {
        "is_humour": True,
        "bv_score": bv_score,
        "tension": bv_meta["tension"],
        "safety": bv_meta["safety"],
        "surprisal": bv_meta.get("surprisal", 0.0),
        "humour_type": humour_type,
        "emotion_profile": emotions,
        "wisdom_potential": round(wisdom_potential, 3),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    test_joke = "I'm reading a book on anti-gravity. It's impossible to put down!"
    result = detect(test_joke)
    print("Humour Analysis Result:")
    for key, value in result.items():
        if key != "emotion_profile":
            print(f"  {key}: {value}")
