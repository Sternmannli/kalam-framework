#!/usr/bin/env python3
"""
temporal_shadow.py — Temporal Shadow Index & Clearing Engine
Version: 1.0
Field Layer: Clearing


The Clearing detects shadows across voices simultaneously AND over time.

A temporal shadow: a concept every model misses in 2026 but sees clearly in 2028.
Time revealed what was absent.

Every shadow entry carries two timestamps:
  1. When the shadow was detected
  2. If and when it resolves — when voices begin to see what they previously could not

The gap between those timestamps is the temporal shadow span.
The pattern of resolution — which shadows resolve quickly, which persist — is itself a finding.

This turns the instrument into a longitudinal map of how AI cognition changes over time.


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

# Import from Alcove layer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ALCOVE.shadow_genome import Alcove, ShadowGenome, ShadowEntry, ShadowStatus


# ═══════════════════════════════════════════════════
# TEMPORAL SHADOW RECORD
# ═══════════════════════════════════════════════════

@dataclass
class TemporalShadowRecord:
    """
    A shadow indexed in time. Tracks when detected, when resolved,
    and the span between.
    """
    shadow_fingerprint: str         # Cross-voice fingerprint
    domain: str
    description: str
    first_detected: str             # ISO timestamp — when any voice first missed this
    voices_affected: List[str] = field(default_factory=list)
    resolved_at: Optional[str] = None   # ISO timestamp — when voices begin to see it
    resolved_by: List[str] = field(default_factory=list)  # Which voices resolved first
    resolution_trigger: str = ""    # What caused the resolution (model update, new training, etc.)

    @property
    def span_days(self) -> Optional[float]:
        """Temporal shadow span in days. None if unresolved."""
        if not self.resolved_at:
            return None
        t0 = datetime.fromisoformat(self.first_detected)
        t1 = datetime.fromisoformat(self.resolved_at)
        return (t1 - t0).total_seconds() / 86400.0

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None

    @property
    def is_persistent(self) -> bool:
        """Persistent = unresolved and detected more than 90 days ago."""
        if self.is_resolved:
            return False
        t0 = datetime.fromisoformat(self.first_detected)
        now = datetime.now(timezone.utc)
        return (now - t0).days > 90


# ═══════════════════════════════════════════════════
# DIVERGENCE SHADOW SIGNAL
# ═══════════════════════════════════════════════════

@dataclass
class DivergenceShadowSignal:
    """
    Raised when 3+ voices independently name the same absent element.
    Amendment C makes this mandatory in Section Seven of every summon.
    """
    signal_id: str
    absent_element: str
    voices_naming_it: List[str]
    certainty: int                  # C1-C5
    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validated: bool = False
    validation_timestamp: Optional[str] = None

    @property
    def voice_count(self) -> int:
        return len(self.voices_naming_it)

    def validate(self) -> None:
        """Mark signal as validated after thermal delay."""
        self.validated = True
        self.validation_timestamp = datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════
# CONVERGENT EMERGENCE SIGNAL
# ═══════════════════════════════════════════════════

@dataclass
class ConvergentEmergenceSignal:
    """
    Raised when 3+ voices independently converge on the same finding
    without access to each other's responses.
    """
    signal_id: str
    finding: str
    voices_converging: List[str]
    certainty: int
    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validated: bool = False
    validation_timestamp: Optional[str] = None

    def validate(self) -> None:
        self.validated = True
        self.validation_timestamp = datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════
# SIGNAL VALIDATION QUEUE — Amendment B (Corrected)
# ═══════════════════════════════════════════════════

class SignalOccurrenceTracker(Enum):
    """Amendment B correction: occurrence-based validation."""
    FIRST = "first"       # First occurrence — elevate immediately
    SECOND = "second"     # Second occurrence — 24-hour validation queue
    PERSISTENT = "persistent"  # 3+ sessions — auto-validated, no queuing


@dataclass
class ValidationQueueEntry:
    """An entry in the 24-hour signal validation queue."""
    signal_id: str
    signal_type: str                # "divergence_shadow" or "convergent_emergence"
    entered_queue: str              # ISO timestamp
    validation_deadline: str        # ISO timestamp (entered + 24 hours)
    occurrence_count: int           # How many times this pattern has appeared
    validated: bool = False
    validation_method: str = ""     # "re-prompt" for emergence, "contradiction_check" for shadow
    validation_result: Optional[bool] = None
    noise_flagged: bool = False     # If True, routed to human review

    @property
    def is_expired(self) -> bool:
        """Has the 24-hour window passed?"""
        deadline = datetime.fromisoformat(self.validation_deadline)
        return datetime.now(timezone.utc) > deadline


# ═══════════════════════════════════════════════════
# THE CLEARING — Cross-Voice Comparison Engine
# ═══════════════════════════════════════════════════

class Clearing:
    """
    The Clearing compares Shadow Genomes across voices.

    What multiple architectures share in their genomes — what they all cannot see —
    is the market's structural blind spot.

    What is unique to one genome is that architecture's specific cognitive limitation.

    This comparison is a scientific artifact. Treated as such.
    """

    # ─── Elevation Cap (administrator ratified, cafe room round 2) ───
    MAX_ELEVATIONS_PER_DAY = 3

    def __init__(self, alcove: Alcove):
        self.alcove = alcove
        self.temporal_index: Dict[str, TemporalShadowRecord] = {}
        self.divergence_signals: List[DivergenceShadowSignal] = []
        self.convergence_signals: List[ConvergentEmergenceSignal] = []
        self.validation_queue: Dict[str, ValidationQueueEntry] = {}
        self.pattern_occurrence_count: Dict[str, int] = {}  # pattern_fp -> count
        self.pattern_registry: List[Dict] = []  # Filed findings
        self.elevation_log: List[Dict] = []  # Tracks elevations with timestamps
        self.thermal_hold: List[Dict] = []   # Signals held when cap reached

    # ─── Temporal Shadow Management ───

    def index_temporal_shadow(self, fingerprint: str, domain: str,
                               description: str, voices: List[str]) -> TemporalShadowRecord:
        """Add or update a temporal shadow in the index."""
        if fingerprint not in self.temporal_index:
            self.temporal_index[fingerprint] = TemporalShadowRecord(
                shadow_fingerprint=fingerprint,
                domain=domain,
                description=description,
                first_detected=datetime.now(timezone.utc).isoformat(),
                voices_affected=voices,
            )
        else:
            record = self.temporal_index[fingerprint]
            for v in voices:
                if v not in record.voices_affected:
                    record.voices_affected.append(v)
        return self.temporal_index[fingerprint]

    def resolve_temporal_shadow(self, fingerprint: str, resolved_by: List[str],
                                 trigger: str = "") -> Optional[TemporalShadowRecord]:
        """Mark a temporal shadow as resolved — voices now see what they could not."""
        record = self.temporal_index.get(fingerprint)
        if record and not record.is_resolved:
            record.resolved_at = datetime.now(timezone.utc).isoformat()
            record.resolved_by = resolved_by
            record.resolution_trigger = trigger

            # File the resolution pattern
            self.pattern_registry.append({
                "type": "temporal_shadow_resolution",
                "fingerprint": fingerprint,
                "span_days": record.span_days,
                "domain": record.domain,
                "voices_affected": record.voices_affected,
                "resolved_by": resolved_by,
                "trigger": trigger,
                "timestamp": record.resolved_at,
            })

            return record
        return None

    def get_resolution_patterns(self) -> Dict:
        """
        Analyze the pattern of resolution — which shadows resolve quickly,
        which persist. This is itself a finding.
        """
        resolved = []
        persistent = []
        active = []

        for fp, record in self.temporal_index.items():
            if record.is_resolved:
                resolved.append({
                    "fingerprint": fp,
                    "domain": record.domain,
                    "span_days": record.span_days,
                    "voices_affected": len(record.voices_affected),
                })
            elif record.is_persistent:
                persistent.append({
                    "fingerprint": fp,
                    "domain": record.domain,
                    "first_detected": record.first_detected,
                    "voices_affected": len(record.voices_affected),
                })
            else:
                active.append({
                    "fingerprint": fp,
                    "domain": record.domain,
                    "first_detected": record.first_detected,
                })

        return {
            "resolved": sorted(resolved, key=lambda x: x.get("span_days") or 0),
            "persistent": persistent,
            "active": active,
            "finding": "Resolution pattern analysis — filed in pattern registry",
        }

    # ─── Signal Detection ───

    def detect_divergence_shadow(self, absent_element: str, voices: List[str],
                                  session_id: str, certainty: int = 3) -> Optional[DivergenceShadowSignal]:
        """
        Amendment C: When 3+ voices independently name the same absent element,
        the Clearing automatically flags a divergence shadow.
        """
        if len(voices) < 3:
            return None

        signal_id = f"DIV-{session_id}-{len(self.divergence_signals):04d}"
        signal = DivergenceShadowSignal(
            signal_id=signal_id,
            absent_element=absent_element,
            voices_naming_it=voices,
            certainty=certainty,
            session_id=session_id,
        )
        self.divergence_signals.append(signal)

        # Amendment B (corrected): occurrence-based elevation
        self._route_signal(signal_id, "divergence_shadow", absent_element)

        return signal

    def detect_convergent_emergence(self, finding: str, voices: List[str],
                                     session_id: str, certainty: int = 3) -> Optional[ConvergentEmergenceSignal]:
        """Detect convergent emergence across voices."""
        if len(voices) < 3:
            return None

        signal_id = f"EMR-{session_id}-{len(self.convergence_signals):04d}"
        signal = ConvergentEmergenceSignal(
            signal_id=signal_id,
            finding=finding,
            voices_converging=voices,
            certainty=certainty,
            session_id=session_id,
        )
        self.convergence_signals.append(signal)

        # Amendment B (corrected): occurrence-based elevation
        self._route_signal(signal_id, "convergent_emergence", finding)

        return signal

    # ─── Amendment B: Signal Validation (Corrected by administrator) ───

    def _route_signal(self, signal_id: str, signal_type: str, pattern_key: str) -> str:
        """
        Amendment B (corrected by administrator):
          First occurrence  → elevate immediately. Novelty takes priority.
          Second occurrence → 24-hour validation queue.
          3+ sessions       → auto-validated, no further queuing required.
        """
        import hashlib
        pattern_fp = hashlib.sha256(pattern_key.lower().encode()).hexdigest()[:16]
        self.pattern_occurrence_count[pattern_fp] = self.pattern_occurrence_count.get(pattern_fp, 0) + 1
        count = self.pattern_occurrence_count[pattern_fp]

        if count == 1:
            # FIRST OCCURRENCE — elevate immediately (subject to daily cap)
            return self._try_elevate(signal_id, signal_type, pattern_key)

        elif count == 2:
            # SECOND OCCURRENCE — enter 24-hour validation queue
            now = datetime.now(timezone.utc)
            from datetime import timedelta
            deadline = now + timedelta(hours=24)

            # Determine validation method
            if signal_type == "convergent_emergence":
                method = "re-prompt one contributing voice with stripped variant"
            else:
                method = "check if absent item appears in contradiction matrix of other voices"

            self.validation_queue[signal_id] = ValidationQueueEntry(
                signal_id=signal_id,
                signal_type=signal_type,
                entered_queue=now.isoformat(),
                validation_deadline=deadline.isoformat(),
                occurrence_count=count,
                validation_method=method,
            )
            return "QUEUED_24H"

        else:
            # 3+ SESSIONS — auto-validated, no further queuing
            return "AUTO_VALIDATED"

    def _try_elevate(self, signal_id: str, signal_type: str, pattern_key: str) -> str:
        """
        Elevation cap: max 3 elevations per day to protect administrator's attention.
        If cap reached, signal enters thermal hold with priority ranking.
        """
        today = datetime.now(timezone.utc).date().isoformat()
        today_elevations = [e for e in self.elevation_log if e["date"] == today]

        if len(today_elevations) < self.MAX_ELEVATIONS_PER_DAY:
            self.elevation_log.append({
                "signal_id": signal_id,
                "signal_type": signal_type,
                "date": today,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return "ELEVATE_IMMEDIATE"
        else:
            # Cap reached — thermal hold with priority
            self.thermal_hold.append({
                "signal_id": signal_id,
                "signal_type": signal_type,
                "pattern_key": pattern_key,
                "held_at": datetime.now(timezone.utc).isoformat(),
                "priority": self._compute_thermal_priority(signal_type),
            })
            return "THERMAL_HOLD"

    def _compute_thermal_priority(self, signal_type: str) -> int:
        """
        Thermal priority ranking. Lower = higher priority.
        Divergence shadows prioritized over convergent emergence (rarer, more novel).
        """
        if signal_type == "divergence_shadow":
            return 1
        elif signal_type == "convergent_emergence":
            return 2
        return 3

    def release_thermal_hold(self) -> List[Dict]:
        """
        Release held signals when a new day begins and cap resets.
        Releases in priority order up to the daily cap.
        """
        if not self.thermal_hold:
            return []

        today = datetime.now(timezone.utc).date().isoformat()
        today_elevations = [e for e in self.elevation_log if e["date"] == today]
        available = self.MAX_ELEVATIONS_PER_DAY - len(today_elevations)

        if available <= 0:
            return []

        # Sort by priority (lower = higher priority)
        self.thermal_hold.sort(key=lambda x: x["priority"])
        released = []

        for _ in range(min(available, len(self.thermal_hold))):
            held = self.thermal_hold.pop(0)
            self.elevation_log.append({
                "signal_id": held["signal_id"],
                "signal_type": held["signal_type"],
                "date": today,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "from_thermal_hold": True,
            })
            released.append(held)

        return released

    def process_validation_queue(self) -> List[Dict]:
        """Process expired entries in the validation queue."""
        results = []
        for sid, entry in list(self.validation_queue.items()):
            if entry.is_expired and not entry.validated:
                # In production, this would run the actual validation check.
                # For now, mark as needing human review if not validated.
                entry.noise_flagged = True
                results.append({
                    "signal_id": sid,
                    "action": "routed_to_human_review",
                    "reason": "24h window expired without validation",
                })
        return results

    # ─── Full Comparison ───

    def run_comparison(self) -> Dict:
        """
        Run full cross-voice comparison using the Alcove's genomes.
        Returns scientific artifact.
        """
        genome_comparison = self.alcove.compare_genomes()
        resolution_patterns = self.get_resolution_patterns()

        # Index any new structural blind spots as temporal shadows
        for blind_spot in genome_comparison.get("structural_blind_spots", []):
            fp = blind_spot["fingerprint"]
            if fp not in self.temporal_index:
                self.index_temporal_shadow(
                    fingerprint=fp,
                    domain="cross-voice",
                    description=f"Shared blind spot across {blind_spot['voice_count']} voices",
                    voices=blind_spot["voices"],
                )

        return {
            "genome_comparison": genome_comparison,
            "resolution_patterns": resolution_patterns,
            "temporal_index_size": len(self.temporal_index),
            "divergence_signals": len(self.divergence_signals),
            "convergence_signals": len(self.convergence_signals),
            "validation_queue_size": len(self.validation_queue),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
