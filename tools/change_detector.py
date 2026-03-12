"""
Change Detection — classify state transitions in time series data.

Detects four modes:
- RUPTURE: sudden drop exceeding a threshold in a single step
- SMOOTH: gradual decline over a sliding window
- RECOVERY: value rising after a prior drop
- STABLE: no significant change detected

Usage:
    values = [1.0, 0.95, 0.90, 0.45, 0.50]
    mode = detect_change_mode(values)
    # mode == ChangeMode.RECOVERY
"""

from enum import Enum
from typing import List


RUPTURE_THRESHOLD = 0.4
SMOOTH_WINDOW = 3
SMOOTH_TOTAL_DROP = 0.3


class ChangeMode(Enum):
    """Classification of a state transition."""
    RUPTURE = "rupture"
    SMOOTH = "smooth"
    STABLE = "stable"
    RECOVERY = "recovery"


def detect_change_mode(
    values: List[float],
    rupture_threshold: float = RUPTURE_THRESHOLD,
    smooth_window: int = SMOOTH_WINDOW,
    smooth_total_drop: float = SMOOTH_TOTAL_DROP,
) -> ChangeMode:
    """
    Classify the change pattern in a sequence of numeric values.

    Args:
        values: time-ordered sequence of measurements (most recent last)
        rupture_threshold: minimum single-step drop to classify as RUPTURE
        smooth_window: number of recent steps to consider for SMOOTH detection
        smooth_total_drop: minimum cumulative drop over the window for SMOOTH

    Returns:
        ChangeMode indicating the detected pattern
    """
    if len(values) < 2:
        return ChangeMode.STABLE

    last_delta = values[-1] - values[-2]

    # Check for rupture: large single-step drop
    if last_delta < 0 and abs(last_delta) >= rupture_threshold:
        return ChangeMode.RUPTURE

    # Check for recovery: rising after a prior drop
    if last_delta > 0 and len(values) >= 3:
        prior_delta = values[-2] - values[-3]
        if prior_delta < 0:
            return ChangeMode.RECOVERY

    # Check for smooth decline over the window
    if len(values) >= smooth_window:
        window = values[-smooth_window:]
        total_drop = window[0] - window[-1]
        if total_drop >= smooth_total_drop:
            all_declining = all(
                window[i] >= window[i + 1] for i in range(len(window) - 1)
            )
            if all_declining:
                return ChangeMode.SMOOTH

    return ChangeMode.STABLE
