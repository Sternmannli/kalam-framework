#!/usr/bin/env python3
"""
decay.py — The Decay Function (Halflife Logic)
Version: 1.0

Linked Rules:  (append-only),  (dignity-first)

Prevents Symbolic Sclerosis — the state where historical weight
drowns out the signal of the present user.

Rules:
  1. No deletion — patterns recede, they do not vanish ()
  2. Weight decay — after N cycles without invocation, weight decreases
  3. Deep Hum state — patterns below threshold enter the Deep Hum archive
  4. Reactivation — any invocation or link restores full weight immediately
  5. Contestation reset — contested patterns reset and enter active review

"A system that cannot forget the irrelevant cannot truly listen to the new."


"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional
from enum import Enum


class PatternState(Enum):
    """Where is a pattern in its lifecycle?"""
    ACTIVE = "active"           # Full weight, recently invoked
    FADING = "fading"           # Weight declining, not recently used
    DEEP_HUM = "deep_hum"      # Below threshold — archived but not deleted
    CONTESTED = "contested"     # Under active review after contestation


@dataclass
class DecayRecord:
    """Tracks decay state for a single pattern."""
    pattern_id: str
    initial_weight: float
    current_weight: float
    state: PatternState
    cycles_since_invocation: int
    invocation_count: int
    contestation_count: int
    created_at: str
    last_invoked_at: Optional[str] = None
    last_contested_at: Optional[str] = None
    entered_deep_hum_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "weight": round(self.current_weight, 4),
            "state": self.state.value,
            "cycles_dormant": self.cycles_since_invocation,
            "invocations": self.invocation_count,
            "contestations": self.contestation_count,
        }


class DecayEngine:
    """
    The Halflife Logic engine. Manages pattern weight decay.

    Usage:
        engine = DecayEngine()
        engine.register("P#EMERGE-2001", weight=1.0)
        engine.tick()  # advance one cycle
        engine.invoke("P#EMERGE-2001")  # reactivate
        engine.contest("P#EMERGE-2001")  # flag for review
        active = engine.list_active()
        deep = engine.list_deep_hum()
    """

    # Configurable parameters
    HALFLIFE_CYCLES = 30        # Cycles until weight halves
    DEEP_HUM_THRESHOLD = 0.1   # Below this weight → Deep Hum
    FADING_THRESHOLD = 0.5     # Below this weight → Fading
    INITIAL_WEIGHT = 1.0       # Default starting weight

    def __init__(self):
        self._patterns: Dict[str, DecayRecord] = {}
        self._cycle_count = 0

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def register(self, pattern_id: str, weight: float = None) -> DecayRecord:
        """Register a new pattern with initial weight."""
        if pattern_id in self._patterns:
            return self._patterns[pattern_id]

        record = DecayRecord(
            pattern_id=pattern_id,
            initial_weight=weight or self.INITIAL_WEIGHT,
            current_weight=weight or self.INITIAL_WEIGHT,
            state=PatternState.ACTIVE,
            cycles_since_invocation=0,
            invocation_count=0,
            contestation_count=0,
            created_at=self._now(),
        )
        self._patterns[pattern_id] = record
        return record

    def tick(self) -> Dict[str, int]:
        """
        Advance one cycle. Apply decay to all patterns.

        Returns counts of state transitions that occurred.
        """
        self._cycle_count += 1
        transitions = {"to_fading": 0, "to_deep_hum": 0}

        for record in self._patterns.values():
            if record.state == PatternState.CONTESTED:
                continue  # Contested patterns don't decay

            record.cycles_since_invocation += 1

            # Exponential decay: w = w0 * (0.5)^(t/halflife)
            decay_factor = math.pow(0.5, record.cycles_since_invocation / self.HALFLIFE_CYCLES)
            record.current_weight = record.initial_weight * decay_factor

            # State transitions
            old_state = record.state
            if record.current_weight < self.DEEP_HUM_THRESHOLD:
                record.state = PatternState.DEEP_HUM
                if old_state != PatternState.DEEP_HUM:
                    record.entered_deep_hum_at = self._now()
                    transitions["to_deep_hum"] += 1
            elif record.current_weight < self.FADING_THRESHOLD:
                record.state = PatternState.FADING
                if old_state == PatternState.ACTIVE:
                    transitions["to_fading"] += 1
            else:
                record.state = PatternState.ACTIVE

        return transitions

    def invoke(self, pattern_id: str) -> Optional[DecayRecord]:
        """
        Invoke a pattern — restores full weight immediately.
        "Any user invocation or link restores full weight."
        """
        record = self._patterns.get(pattern_id)
        if record is None:
            return None

        record.current_weight = record.initial_weight
        record.cycles_since_invocation = 0
        record.invocation_count += 1
        record.last_invoked_at = self._now()
        record.state = PatternState.ACTIVE
        record.entered_deep_hum_at = None
        return record

    def contest(self, pattern_id: str) -> Optional[DecayRecord]:
        """
        Contest a pattern — resets weight and enters active review.
        "If a user contests a pattern, its weight resets and it enters active review."
        """
        record = self._patterns.get(pattern_id)
        if record is None:
            return None

        record.current_weight = record.initial_weight
        record.cycles_since_invocation = 0
        record.contestation_count += 1
        record.last_contested_at = self._now()
        record.state = PatternState.CONTESTED
        record.entered_deep_hum_at = None
        return record

    def resolve_contestation(self, pattern_id: str) -> Optional[DecayRecord]:
        """Resolve a contestation — return pattern to active state."""
        record = self._patterns.get(pattern_id)
        if record is None or record.state != PatternState.CONTESTED:
            return None
        record.state = PatternState.ACTIVE
        return record

    def get(self, pattern_id: str) -> Optional[DecayRecord]:
        """Get a pattern's decay record."""
        return self._patterns.get(pattern_id)

    def list_active(self) -> List[DecayRecord]:
        """List all active patterns (full or near-full weight)."""
        return [r for r in self._patterns.values() if r.state == PatternState.ACTIVE]

    def list_fading(self) -> List[DecayRecord]:
        """List all fading patterns."""
        return [r for r in self._patterns.values() if r.state == PatternState.FADING]

    def list_deep_hum(self) -> List[DecayRecord]:
        """List all patterns in the Deep Hum archive."""
        return [r for r in self._patterns.values() if r.state == PatternState.DEEP_HUM]

    def list_contested(self) -> List[DecayRecord]:
        """List all contested patterns awaiting review."""
        return [r for r in self._patterns.values() if r.state == PatternState.CONTESTED]

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    @property
    def total_patterns(self) -> int:
        return len(self._patterns)

    def state_counts(self) -> Dict[str, int]:
        """Count patterns in each state."""
        counts = {s.value: 0 for s in PatternState}
        for r in self._patterns.values():
            counts[r.state.value] += 1
        return counts
