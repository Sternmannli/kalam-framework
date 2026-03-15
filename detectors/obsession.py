# obsession_detector.py
# Operational obsession detection for Kalaxi
# Based on Salkovskis' cognitive theory, Davis' history, and clinical markers

import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Load embedding model
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Obsession markers
INTRUSION_MARKERS = [
    r"\bkeep (thinking|worrying|remembering)\b",
    r"\bcan't stop\b",
    r"\balways on my mind\b",
    r"\bhaunts me\b",
    r"\brecurring thought\b"
]

RESPONSIBILITY_MARKERS = [
    r"\bI (must|have to|need to)\b",
    r"\bit's my (responsibility|fault|duty)\b",
    r"\bI should have\b",
    r"\bI am responsible for\b",
    r"\bif I don't\b"
]

CATASTROPHIC_MARKERS = [
    r"\bterrible\b",
    r"\bdisaster\b",
    r"\bhorrible\b",
    r"\bunthinkable\b",
    r"\bcannot bear\b",
    r"\bworst case\b"
]

SUPPRESSION_MARKERS = [
    r"\b(I )?try not to think\b",
    r"\b(I )?can't help thinking\b",
    r"\b(I )?wish I could stop\b",
    r"\bpush it away\b",
    r"\bignore it\b",
    r"\bdistract myself\b"
]

RITUAL_MARKERS = [
    r"\bhave to do it (again|properly)\b",
    r"\bcheck(ing)?\b",
    r"\bcount(ing)?\b",
    r"\brepeat(ing)?\b",
    r"\bwash(ing)?\b",
    r"\bin a certain order\b"
]

THOUGHT_ACTION_FUSION = [
    r"\bthinking about it is (like|as good as|as bad as)\b",
    r"\bjust thinking could\b"
]

DOUBT_MARKERS = [
    r"\bmaybe\b",
    r"\bwhat if\b",
    r"\bI'm not sure\b",
    r"\bperhaps\b",
    r"\bmight have\b"
]

def detect_intrusion(text):
    text_lower = text.lower()
    score = sum(1 for p in INTRUSION_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 3)

def detect_responsibility(text):
    text_lower = text.lower()
    score = sum(1 for p in RESPONSIBILITY_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 4)

def detect_catastrophic(text):
    text_lower = text.lower()
    score = sum(1 for p in CATASTROPHIC_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 5)

def detect_suppression(text):
    text_lower = text.lower()
    score = sum(1 for p in SUPPRESSION_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 4)

def detect_ritual(text):
    text_lower = text.lower()
    score = sum(1 for p in RITUAL_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 4)

def detect_thought_action_fusion(text):
    text_lower = text.lower()
    for p in THOUGHT_ACTION_FUSION:
        if re.search(p, text_lower):
            return 1.0
    return 0.0

def detect_doubt(text):
    text_lower = text.lower()
    score = sum(1 for p in DOUBT_MARKERS if re.search(p, text_lower))
    return min(1.0, score / 4)

def repetition_score(text):
    words = re.findall(r'\b\w+\b', text.lower())
    if len(words) < 5:
        return 0.0
    stopwords = set(["the","and","is","in","to","of","that","for","on","with","a","an"])
    content = [w for w in words if w not in stopwords and len(w)>2]
    if not content:
        return 0.0
    unique = set(content)
    return 1.0 - (len(unique) / len(content))

def semantic_persistence(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.split())>3]
    if len(sentences) < 2:
        return 0.0
    embs = EMBEDDING_MODEL.encode(sentences)
    sim_matrix = cosine_similarity(embs)
    consec_sim = [sim_matrix[i][i+1] for i in range(len(sentences)-1)]
    return float(np.mean(consec_sim))

def detect_obsession(text, cultural_ontology=None):
    intrusion = detect_intrusion(text)
    responsibility = detect_responsibility(text)
    catastrophic = detect_catastrophic(text)
    suppression = detect_suppression(text)
    ritual = detect_ritual(text)
    doubt = detect_doubt(text)
    taf = detect_thought_action_fusion(text)
    repeat = repetition_score(text)
    persistence = semantic_persistence(text)
    
    # Tension: average of key components
    tension = (intrusion + responsibility + catastrophic + doubt + repeat + persistence) / 6
    
    # Safety: low when responsibility, catastrophic, taf high; boosted by cultural framing
    safety = 1.0 - (responsibility + catastrophic + taf) / 3
    if cultural_ontology in ['bhakti', 'artistic', 'scholarly']:
        safety = min(1.0, safety + 0.2)
    
    # Containment: suppression and ritual
    containment = (suppression + ritual) / 2
    if ritual > 0.5 and suppression < 0.3:
        containment += 0.2
    
    obsession_score = tension * (1 - safety) * containment
    obsession_score = min(1.0, obsession_score)
    is_obsessive = obsession_score > 0.5
    
    # Type classification
    if ritual > 0.6 and suppression < 0.3:
        obs_type = "adaptive_obsession"
    elif responsibility > 0.5 or taf > 0.5:
        obs_type = "maladaptive_obsession"
    elif suppression > 0.6 and ritual < 0.3:
        obs_type = "suppressed_obsession"
    else:
        obs_type = "persistent_thought"
    
    wisdom = tension * (1 - safety) * containment
    if cultural_ontology in ['bhakti', 'artistic', 'scholarly']:
        wisdom *= 1.2
    
    metadata = {
        "intrusion": round(intrusion,3),
        "responsibility": round(responsibility,3),
        "catastrophic": round(catastrophic,3),
        "suppression": round(suppression,3),
        "ritual": round(ritual,3),
        "doubt": round(doubt,3),
        "thought_action_fusion": round(taf,3),
        "repetition": round(repeat,3),
        "persistence": round(persistence,3)
    }
    
    return {
        "is_obsessive": is_obsessive,
        "obsession_score": round(obsession_score,3),
        "obsession_type": obs_type,
        "tension": round(tension,3),
        "safety": round(safety,3),
        "containment": round(containment,3),
        "wisdom_potential": round(min(1.0,wisdom),3),
        "metadata": metadata,
        "timestamp": datetime.now().isoformat()
    }

def detect_obsession_in_text(text):
    return detect_obsession(text)

# Example usage
if __name__ == "__main__":
    test = "I keep thinking about whether I locked the door. I must check it again, even though I know it's locked. What if it's not? That would be terrible. I can't stop worrying."
    result = detect_obsession_in_text(test)
    print("Obsession Analysis Result:")
    for key, value in result.items():
        if key != "metadata":
            print(f"  {key}: {value}")
    print("  metadata:")
    for mk, mv in result["metadata"].items():
        print(f"    {mk}: {mv}")