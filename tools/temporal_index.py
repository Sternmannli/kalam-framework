"""
Dual Temporal Index — short-term and long-term event tracking.

Events are assigned to a short-term track (≤ SHORT_TERM_DAYS from now)
or a long-term track. Cross-track discovery finds patterns that span
both windows.

Usage:
    idx = DualTemporalIndex(short_term_days=7)
    idx.add("evt-1", datetime.now())
    idx.add("evt-2", datetime.now() - timedelta(days=30))
    idx.rebalance()
    recent = idx.query_short_term()
    old = idx.query_long_term()
    cross = idx.cross_track_discovery()
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


SHORT_TERM_DAYS = 7


class DualTemporalIndex:
    """Maintains two temporal tracks with automatic rebalancing."""

    def __init__(self, short_term_days: int = SHORT_TERM_DAYS):
        self.short_term_days = short_term_days
        self._short: Dict[str, datetime] = {}
        self._long: Dict[str, datetime] = {}

    def add(self, event_id: str, timestamp: datetime) -> str:
        """Add an event. Returns 'short' or 'long' based on assignment."""
        track = self._assign_track(timestamp)
        if track == "short":
            self._short[event_id] = timestamp
        else:
            self._long[event_id] = timestamp
        return track

    def _assign_track(self, timestamp: datetime) -> str:
        cutoff = datetime.now() - timedelta(days=self.short_term_days)
        return "short" if timestamp >= cutoff else "long"

    def rebalance(self) -> int:
        """Move expired short-term events to long-term. Returns count moved."""
        cutoff = datetime.now() - timedelta(days=self.short_term_days)
        moved = 0
        expired = [
            (eid, ts) for eid, ts in self._short.items() if ts < cutoff
        ]
        for eid, ts in expired:
            del self._short[eid]
            self._long[eid] = ts
            moved += 1
        return moved

    def query_short_term(self) -> List[Tuple[str, datetime]]:
        """Return all short-term events, most recent first."""
        return sorted(self._short.items(), key=lambda x: x[1], reverse=True)

    def query_long_term(self) -> List[Tuple[str, datetime]]:
        """Return all long-term events, most recent first."""
        return sorted(self._long.items(), key=lambda x: x[1], reverse=True)

    def cross_track_discovery(self) -> Dict[str, int]:
        """Summary statistics across both tracks."""
        return {
            "short_term_count": len(self._short),
            "long_term_count": len(self._long),
            "total": len(self._short) + len(self._long),
            "short_term_days": self.short_term_days,
        }

    def state(self) -> dict:
        """Serializable snapshot."""
        return {
            "short_term_days": self.short_term_days,
            "short": {eid: ts.isoformat() for eid, ts in self._short.items()},
            "long": {eid: ts.isoformat() for eid, ts in self._long.items()},
        }
