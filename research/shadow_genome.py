#!/usr/bin/env python3
"""
shadow_genome.py — Shadow Genome: Structural Cognitive Limitation Tracking
Version: 1.0
Field Layer: Alcove


Every voice that passes through the Clearing develops a stable, recurring
pattern of what it cannot see. This is not random. It is structural. It is
the cognitive signature of that architecture's limitations.

The Shadow Genome is a vector alongside the fingerprint. It tracks which
shadows a voice has produced, how frequently, across how many sessions,
and whether those shadows persist or resolve over time. It updates
automatically after every summon.

Promotion rule: When a voice produces the same shadow across three or more
independent sessions, that shadow is promoted to a canonical genome entry.


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from enum import Enum
import hashlib
import json


# ═══════════════════════════════════════════════════
# SHADOW STATUS
# ═══════════════════════════════════════════════════

class ShadowStatus(Enum):
    """Lifecycle of a shadow observation."""
    OBSERVED = "observed"           # Single occurrence — noted, not yet patterned
    RECURRING = "recurring"         # 2 sessions — pattern emerging
    CANONICAL = "canonical"         # 3+ sessions — promoted to genome entry
    RESOLVED = "resolved"           # Voice now sees what it previously could not


# ═══════════════════════════════════════════════════
# SHADOW ENTRY
# ═══════════════════════════════════════════════════

@dataclass
class ShadowEntry:
    """A single shadow observation for a voice."""
    shadow_id: str
    voice_id: str                   # e.g. "Eadministrator" (DeepSeek), "Esystem" (Grok)
    description: str                # What the voice cannot see
    domain: str                     # Domain of the blind spot (e.g. "epistemology", "ethics")
    sessions: List[str] = field(default_factory=list)     # Session IDs where observed
    first_detected: str = ""        # ISO timestamp — when shadow first appeared
    last_detected: str = ""         # ISO timestamp — most recent observation
    resolved_at: Optional[str] = None   # ISO timestamp — if/when voice begins to see it
    status: ShadowStatus = ShadowStatus.OBSERVED
    certainty: int = 1              # C1-C5 scale
    notes: List[str] = field(default_factory=list)

    @property
    def session_count(self) -> int:
        return len(self.sessions)

    @property
    def temporal_shadow_span(self) -> Optional[float]:
        """Days between first detection and resolution. None if unresolved."""
        if not self.resolved_at or not self.first_detected:
            return None
        t_start = datetime.fromisoformat(self.first_detected)
        t_end = datetime.fromisoformat(self.resolved_at)
        return (t_end - t_start).total_seconds() / 86400.0

    def record_observation(self, session_id: str) -> None:
        """Record a new observation of this shadow in a session."""
        now = datetime.now(timezone.utc).isoformat()
        if not self.first_detected:
            self.first_detected = now
        self.last_detected = now

        if session_id not in self.sessions:
            self.sessions.append(session_id)

        # Promotion logic
        if self.session_count >= 3 and self.status != ShadowStatus.RESOLVED:
            self.status = ShadowStatus.CANONICAL
            self.certainty = max(self.certainty, 3)
        elif self.session_count >= 2 and self.status == ShadowStatus.OBSERVED:
            self.status = ShadowStatus.RECURRING
            self.certainty = max(self.certainty, 2)

    def resolve(self, session_id: str, notes: str = "") -> None:
        """Mark shadow as resolved — voice now sees what it could not."""
        self.resolved_at = datetime.now(timezone.utc).isoformat()
        self.status = ShadowStatus.RESOLVED
        if notes:
            self.notes.append(f"[RESOLVED in {session_id}] {notes}")


# ═══════════════════════════════════════════════════
# SHADOW GENOME — Per-Voice Genome Vector
# ═══════════════════════════════════════════════════

@dataclass
class ShadowGenome:
    """
    The complete shadow genome for a single voice.
    A vector alongside the fingerprint — tracks structural cognitive limitations.
    """
    voice_id: str
    voice_name: str                 # e.g. "DeepSeek", "Grok", "Copilot"
    shadows: Dict[str, ShadowEntry] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = ""

    @property
    def canonical_shadows(self) -> List[ShadowEntry]:
        """Shadows promoted to canonical genome entries (3+ sessions)."""
        return [s for s in self.shadows.values() if s.status == ShadowStatus.CANONICAL]

    @property
    def active_shadows(self) -> List[ShadowEntry]:
        """All unresolved shadows."""
        return [s for s in self.shadows.values() if s.status != ShadowStatus.RESOLVED]

    @property
    def resolved_shadows(self) -> List[ShadowEntry]:
        """Shadows that have been resolved."""
        return [s for s in self.shadows.values() if s.status == ShadowStatus.RESOLVED]

    @property
    def genome_vector(self) -> Dict[str, int]:
        """Numeric summary: domain -> count of canonical shadows."""
        vector = {}
        for s in self.canonical_shadows:
            vector[s.domain] = vector.get(s.domain, 0) + 1
        return vector

    def add_shadow(self, description: str, domain: str, session_id: str) -> ShadowEntry:
        """Add or update a shadow observation."""
        shadow_id = _make_shadow_id(self.voice_id, description, domain)
        self.last_updated = datetime.now(timezone.utc).isoformat()

        if shadow_id in self.shadows:
            self.shadows[shadow_id].record_observation(session_id)
        else:
            entry = ShadowEntry(
                shadow_id=shadow_id,
                voice_id=self.voice_id,
                description=description,
                domain=domain,
            )
            entry.record_observation(session_id)
            self.shadows[shadow_id] = entry

        return self.shadows[shadow_id]

    def resolve_shadow(self, shadow_id: str, session_id: str, notes: str = "") -> Optional[ShadowEntry]:
        """Resolve a shadow — voice now sees what it could not."""
        if shadow_id in self.shadows:
            self.shadows[shadow_id].resolve(session_id, notes)
            self.last_updated = datetime.now(timezone.utc).isoformat()
            return self.shadows[shadow_id]
        return None

    def to_dict(self) -> dict:
        """Serialize genome for storage."""
        return {
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "shadow_count": len(self.shadows),
            "canonical_count": len(self.canonical_shadows),
            "resolved_count": len(self.resolved_shadows),
            "genome_vector": self.genome_vector,
            "shadows": {
                sid: {
                    "description": s.description,
                    "domain": s.domain,
                    "status": s.status.value,
                    "session_count": s.session_count,
                    "certainty": s.certainty,
                    "first_detected": s.first_detected,
                    "last_detected": s.last_detected,
                    "resolved_at": s.resolved_at,
                    "temporal_span_days": s.temporal_shadow_span,
                }
                for sid, s in self.shadows.items()
            },
        }


# ═══════════════════════════════════════════════════
# ALCOVE — Registry of All Genomes
# ═══════════════════════════════════════════════════

class Alcove:
    """
    The Alcove holds all voice genomes and manages cross-genome comparison.

    When the Clearing compares Shadow Genomes:
    - What multiple architectures share = market's structural blind spot
    - What is unique to one genome = that architecture's specific cognitive limitation
    """

    def __init__(self):
        self.genomes: Dict[str, ShadowGenome] = {}
        self.structural_blind_spots: List[Dict] = []   # Shared across voices
        self.unique_limitations: Dict[str, List[Dict]] = {}  # Per-voice unique

    def register_voice(self, voice_id: str, voice_name: str) -> ShadowGenome:
        """Register a voice in the Alcove or return existing genome."""
        if voice_id not in self.genomes:
            self.genomes[voice_id] = ShadowGenome(voice_id=voice_id, voice_name=voice_name)
        return self.genomes[voice_id]

    def get_genome(self, voice_id: str) -> Optional[ShadowGenome]:
        """Retrieve a voice's shadow genome."""
        return self.genomes.get(voice_id)

    def record_shadow(self, voice_id: str, description: str, domain: str, session_id: str) -> Optional[ShadowEntry]:
        """Record a shadow observation for a voice. Auto-updates after every summon."""
        genome = self.genomes.get(voice_id)
        if genome:
            return genome.add_shadow(description, domain, session_id)
        return None

    def compare_genomes(self) -> Dict:
        """
        Cross-genome comparison. Scientific artifact.

        Returns:
            - structural_blind_spots: shadows shared by 2+ voices (market-level)
            - unique_limitations: shadows unique to one voice
            - resolution_patterns: which shadows resolve, which persist
        """
        # Collect all canonical shadows by domain+description fingerprint
        shadow_map: Dict[str, List[str]] = {}  # fingerprint -> [voice_ids]

        for voice_id, genome in self.genomes.items():
            for shadow in genome.canonical_shadows:
                fp = _make_comparison_key(shadow.description, shadow.domain)
                if fp not in shadow_map:
                    shadow_map[fp] = []
                shadow_map[fp].append(voice_id)

        # Classify
        self.structural_blind_spots = []
        self.unique_limitations = {}

        for fp, voices in shadow_map.items():
            if len(voices) >= 2:
                self.structural_blind_spots.append({
                    "fingerprint": fp,
                    "voices": voices,
                    "voice_count": len(voices),
                    "is_market_blind_spot": len(voices) >= 3,
                })
            elif len(voices) == 1:
                vid = voices[0]
                if vid not in self.unique_limitations:
                    self.unique_limitations[vid] = []
                self.unique_limitations[vid].append({"fingerprint": fp})

        return {
            "structural_blind_spots": self.structural_blind_spots,
            "unique_limitations": self.unique_limitations,
            "total_genomes": len(self.genomes),
            "comparison_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def resolution_patterns(self) -> Dict:
        """Analyze which shadows resolve quickly, which persist."""
        resolved = []
        persistent = []

        for genome in self.genomes.values():
            for shadow in genome.resolved_shadows:
                resolved.append({
                    "voice": genome.voice_id,
                    "domain": shadow.domain,
                    "span_days": shadow.temporal_shadow_span,
                    "description": shadow.description,
                })
            for shadow in genome.canonical_shadows:
                persistent.append({
                    "voice": genome.voice_id,
                    "domain": shadow.domain,
                    "session_count": shadow.session_count,
                    "first_detected": shadow.first_detected,
                    "description": shadow.description,
                })

        return {
            "resolved": sorted(resolved, key=lambda x: x.get("span_days") or 0),
            "persistent": sorted(persistent, key=lambda x: x["session_count"], reverse=True),
        }


# ═══════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════

def _make_shadow_id(voice_id: str, description: str, domain: str) -> str:
    """Deterministic ID for a shadow entry."""
    raw = f"{voice_id}:{domain}:{description.lower().strip()}"
    return f"SHD-{hashlib.sha256(raw.encode()).hexdigest()[:12]}"


def _make_comparison_key(description: str, domain: str) -> str:
    """Fingerprint for cross-voice comparison (voice-agnostic)."""
    raw = f"{domain}:{description.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
