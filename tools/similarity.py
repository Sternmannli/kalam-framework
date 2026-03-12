"""
Structural Similarity — fingerprint-based echo detection.

Computes structural fingerprints from metadata dicts and measures
similarity using weighted Jaccard (sets) + exact match (scalars).
Detects echoes — events that are structurally similar despite
different surface content.

Usage:
    fp1 = structural_fingerprint({"tags": {"a", "b"}, "type": "note"})
    fp2 = structural_fingerprint({"tags": {"a", "c"}, "type": "note"})
    score = structural_similarity(fp1, fp2)
    echoes = detect_echoes(events, threshold=0.6)
"""

from typing import Any, Dict, List, Tuple


ECHO_SIMILARITY_THRESHOLD = 0.6


def structural_fingerprint(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a structural fingerprint from a metadata dict.

    Sets are kept as frozensets. Scalars are kept as-is.
    Nested dicts are flattened with dot notation.
    """
    fp: Dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, (set, frozenset, list)):
            fp[key] = frozenset(value) if not isinstance(value, frozenset) else value
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                fp[f"{key}.{sub_key}"] = sub_value
        else:
            fp[key] = value
    return fp


def structural_similarity(fp_a: Dict[str, Any], fp_b: Dict[str, Any]) -> float:
    """
    Compute structural similarity between two fingerprints.

    For set-valued fields: Jaccard similarity (|intersection| / |union|).
    For scalar fields: 1.0 if equal, 0.0 otherwise.
    Final score is the mean across all shared + unique keys.
    """
    all_keys = set(fp_a.keys()) | set(fp_b.keys())
    if not all_keys:
        return 1.0

    total = 0.0
    for key in all_keys:
        val_a = fp_a.get(key)
        val_b = fp_b.get(key)

        if val_a is None or val_b is None:
            total += 0.0
        elif isinstance(val_a, frozenset) and isinstance(val_b, frozenset):
            union = val_a | val_b
            if not union:
                total += 1.0
            else:
                total += len(val_a & val_b) / len(union)
        else:
            total += 1.0 if val_a == val_b else 0.0

    return total / len(all_keys)


def detect_echoes(
    events: List[Tuple[str, Dict[str, Any]]],
    threshold: float = ECHO_SIMILARITY_THRESHOLD,
) -> List[Tuple[str, str, float]]:
    """
    Find all pairs of events whose structural similarity >= threshold.

    Args:
        events: list of (event_id, metadata_dict) tuples
        threshold: minimum similarity to count as an echo

    Returns:
        list of (event_id_a, event_id_b, similarity_score) tuples
    """
    fingerprints = [(eid, structural_fingerprint(meta)) for eid, meta in events]
    echoes = []
    for i in range(len(fingerprints)):
        for j in range(i + 1, len(fingerprints)):
            eid_a, fp_a = fingerprints[i]
            eid_b, fp_b = fingerprints[j]
            sim = structural_similarity(fp_a, fp_b)
            if sim >= threshold:
                echoes.append((eid_a, eid_b, sim))
    return echoes
