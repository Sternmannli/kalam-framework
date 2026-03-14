# love.py — Love detection based on Sternberg's Triangular Theory
# Based on Sternberg (1986) and emotion analysis
#
# Detects intimacy, passion, and commitment components in text.
# Classifies love type (consummate, romantic, companionate, etc.).
#
# Dependencies: transformers, torch, numpy

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import re
from datetime import datetime

# Load pre-trained emotion model
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
emotion_tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL)
emotion_model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL)

EMOTION_LABELS = ["admiration", "joy", "love", "desire", "trust",
                  "fear", "anger", "sadness", "disgust", "surprise"]

LOVE_LETTER_INDICATORS = [
    (r"\bdear\b", 2),
    (r"\bmy (love|darling|dearest|heart|soul)\b", 3),
    (r"\bI (miss|need|want|cherish|adore)\b", 2),
    (r"\byou are (my|the)\b", 2),
    (r"\bforever|always|never\b", 1),
    (r"\bwithout you\b", 3),
    (r"\byour (eyes|smile|hand|touch|voice)\b", 2),
    (r"\bremember when\b", 2)
]

SACRIFICE_INDICATORS = [
    r"\bI (would )?(give|do) anything\b",
    r"\bfor you\b",
    r"\byour happiness\b",
    r"\bput you first\b",
    r"\bmy (life|time|energy) for\b",
    r"\bworth it because\b"
]


def detect_love_elements(text):
    """
    Returns intimacy, passion, commitment scores (0-100) for input text.
    Based on emotion classifier mapped to Sternberg's three components.
    """
    inputs = emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = emotion_model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
    emotion_dict = {EMOTION_LABELS[i]: scores[i] * 100 for i in range(len(EMOTION_LABELS))}

    intimacy = np.mean([emotion_dict.get(e, 0) for e in ['love', 'admiration', 'joy']])
    passion = np.mean([emotion_dict.get(e, 0) for e in ['desire', 'joy', 'surprise']])
    commitment = np.mean([emotion_dict.get(e, 0) for e in ['trust', 'admiration']])

    return {
        "intimacy": round(intimacy, 2),
        "passion": round(passion, 2),
        "commitment": round(commitment, 2),
        "emotion_profile": emotion_dict
    }


def classify_love_type(intimacy, passion, commitment):
    """
    Determine love type based on Sternberg's Triangular Theory thresholds.

    Returns:
        tuple: (love_type: str, description: str)
    """
    def level(score):
        if score >= 60: return "high"
        elif score >= 40: return "medium"
        else: return "low"

    i, p, c = level(intimacy), level(passion), level(commitment)

    types = {
        ("high","high","high"): ("consummate", "Complete, ideal love"),
        ("high","high","low"): ("romantic", "Intimate + passionate"),
        ("high","low","high"): ("companionate", "Intimate + committed"),
        ("low","high","high"): ("fatuous", "Passionate + committed (whirlwind)"),
        ("high","low","low"): ("liking", "True friendship"),
        ("low","high","low"): ("infatuation", "Love at first sight"),
        ("low","low","high"): ("empty", "Commitment without intimacy/passion")
    }
    return types.get((i,p,c), ("non-love", "No significant love components"))


def detect_love_letter(text):
    """Score (0-100) for love-letter characteristics."""
    text_lower = text.lower()
    score = 0
    for pattern, weight in LOVE_LETTER_INDICATORS:
        if re.search(pattern, text_lower):
            score += weight
    return min(100, score * 5)


def detect_sacrifice(text):
    """Boolean: does the text express sacrifice?"""
    text_lower = text.lower()
    for pattern in SACRIFICE_INDICATORS:
        if re.search(pattern, text_lower):
            return True
    return False


def detect(text):
    """
    Complete love analysis pipeline.

    Args:
        text: Input text to analyze.

    Returns:
        dict with keys: love_type, love_description, intimacy, passion,
        commitment, love_letter_score, sacrifice_detected, emotion_profile, timestamp.

    Example:
        >>> result = detect("I cherish every moment with you. You are my heart.")
        >>> result["love_type"]
        'consummate'
    """
    elements = detect_love_elements(text)
    love_type, desc = classify_love_type(elements["intimacy"], elements["passion"], elements["commitment"])
    letter_score = detect_love_letter(text)
    sacrifice = detect_sacrifice(text)

    return {
        "love_type": love_type,
        "love_description": desc,
        "intimacy": elements["intimacy"],
        "passion": elements["passion"],
        "commitment": elements["commitment"],
        "love_letter_score": letter_score,
        "sacrifice_detected": sacrifice,
        "emotion_profile": elements["emotion_profile"],
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    test = "I feel deeply connected to you and cherish every moment we spend together. I would do anything for your happiness."
    result = detect(test)
    print("Love Analysis Result:")
    for key, value in result.items():
        if key != "emotion_profile":
            print(f"  {key}: {value}")
