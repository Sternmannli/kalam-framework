#!/usr/bin/env python3
"""
pacing.py — Synchronization and Pacing Module

Ensures system modules do not race, stall, or drift out of alignment.
Provides stress-based automatic pausing when system load exceeds thresholds.

Core operations: tick, sync, pause, resume, stress_check

Dependencies: none (stdlib only)

Example:
    >>> pacer = Pacer()
    >>> pacer.tick()
    1
    >>> pacer.stress_check(pending_messages=600)
    <StressLevel.EXCEEDED: 'exceeded'>
    >>> pacer.is_paused
    True
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum


class StressLevel(Enum):
    BELOW_THRESHOLD = "below_threshold"
    AT_THRESHOLD = "at_threshold"
    EXCEEDED = "exceeded"


@dataclass
class PacerState:
    cycle: int
    paused: bool
    pause_reason: str
    stress: StressLevel
    last_tick: str
    synced_modules: list


class Pacer:
    """
    Pacing layer. Ensures modules stay synchronized.

    Stress thresholds:
      - pending_messages > 100: AT_THRESHOLD
      - pending_messages > 500: EXCEEDED (auto-pause)
      - unconfirmed > 50: AT_THRESHOLD
      - unconfirmed > 200: EXCEEDED
    """

    MSG_THRESHOLD = 100
    MSG_EXCEEDED = 500
    UNCONFIRMED_THRESHOLD = 50
    UNCONFIRMED_EXCEEDED = 200

    def __init__(self):
        self._cycle = 0
        self._paused = False
        self._pause_reason = ""
        self._synced = []
        self._last_tick = ""
        self._log = []

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def tick(self):
        """Advance one cycle. Returns current cycle number."""
        if self._paused:
            return self._cycle
        self._cycle += 1
        self._last_tick = self._now()
        self._log.append({"event": "tick", "cycle": self._cycle, "timestamp": self._last_tick})
        return self._cycle

    def sync(self, module_ids):
        """Synchronize modules. Returns alignment receipt."""
        now = self._now()
        self._synced = list(module_ids)
        receipt = {"cycle": self._cycle, "modules": self._synced, "timestamp": now, "aligned": True}
        self._log.append({"event": "sync", "cycle": self._cycle, "modules": self._synced, "timestamp": now})
        return receipt

    def pause(self, reason):
        """Deliberate slow-down. Logged, never silent."""
        if not reason or not reason.strip():
            raise ValueError("Pause requires explicit reason.")
        self._paused = True
        self._pause_reason = reason
        self._log.append({"event": "pause", "cycle": self._cycle, "reason": reason, "timestamp": self._now()})
        return {"paused": True, "reason": reason, "cycle": self._cycle}

    def resume(self):
        """Resume after pause."""
        if not self._paused:
            return {"paused": False, "message": "Not paused."}
        old_reason = self._pause_reason
        self._paused = False
        self._pause_reason = ""
        self._log.append({"event": "resume", "cycle": self._cycle, "previous_reason": old_reason, "timestamp": self._now()})
        return {"paused": False, "resumed_from": old_reason, "cycle": self._cycle}

    def stress_check(self, pending_messages=0, unconfirmed_messages=0):
        """Check system stress. Auto-pauses if exceeded."""
        level = StressLevel.BELOW_THRESHOLD
        if pending_messages > self.MSG_THRESHOLD or unconfirmed_messages > self.UNCONFIRMED_THRESHOLD:
            level = StressLevel.AT_THRESHOLD
        if pending_messages > self.MSG_EXCEEDED or unconfirmed_messages > self.UNCONFIRMED_EXCEEDED:
            level = StressLevel.EXCEEDED
            if not self._paused:
                self.pause(f"Stress exceeded: {pending_messages} pending, {unconfirmed_messages} unconfirmed")
        self._log.append({"event": "stress_check", "cycle": self._cycle, "level": level.value, "timestamp": self._now()})
        return level

    @property
    def state(self):
        return PacerState(
            cycle=self._cycle, paused=self._paused, pause_reason=self._pause_reason,
            stress=StressLevel.BELOW_THRESHOLD, last_tick=self._last_tick,
            synced_modules=list(self._synced),
        )

    @property
    def is_paused(self):
        return self._paused

    @property
    def cycle(self):
        return self._cycle
