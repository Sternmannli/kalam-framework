#!/usr/bin/env python3
"""
negative_space.py — Seed #9: Negative Space Index
Planted: 2026-03-13
Thermal delay: FROZEN (was 14 days, T3 Wisdom tier)

"The silence between notes is still music." — Axi

This module measures what the system does NOT see:
  - Domains that exist but have no recent activity
  - Expected patterns that never appeared
  - Questions the system never asked
  - Voices that went silent

Negative space is not error. It is information.
A system that only measures what it has is blind to what it lacks.

The index does not fill gaps automatically. It surfaces them
for the administrator, who decides what the silence means.


             Decision Filter (Weakest-Voice-First)
Canon reference: Seed #9 spec, Observation OBS-007


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set
from enum import Enum


class SilenceType(Enum):
    """What kind of absence are we seeing?"""
    DORMANT_DOMAIN = "dormant_domain"       # Domain exists but no recent activity
    MISSING_PATTERN = "missing_pattern"     # Expected pattern never appeared
    SILENT_VOICE = "silent_voice"           # A participant went quiet
    UNASKED_QUESTION = "unasked_question"   # A question the system should have asked


@dataclass
class Silence:
    """One observed absence."""
    silence_type: SilenceType
    identifier: str          # What is absent (domain name, pattern type, voice ID, question)
    last_seen: Optional[str]  # ISO timestamp of last activity, or None if never seen
    expected_by: str          # Why we expected to see this (rule, pattern, domain rule)
    cycles_silent: int        # How many cycles since last activity
    severity: float           # 0.0 = minor gap, 1.0 = critical blind spot
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "type": self.silence_type.value,
            "identifier": self.identifier,
            "last_seen": self.last_seen,
            "expected_by": self.expected_by,
            "cycles_silent": self.cycles_silent,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }


@dataclass
class NegativeSpaceReport:
    """Full report of what the system is not seeing."""
    total_silences: int
    critical_silences: int       # severity >= 0.8
    dormant_domains: int
    missing_patterns: int
    silent_voices: int
    unasked_questions: int
    blindness_score: float       # 0.0 = fully aware, 1.0 = completely blind
    top_silences: List[dict]     # Most severe silences
    recommendation: str


class NegativeSpaceIndex:
    """
    Tracks what the system does NOT see.

    The index maintains a registry of expected domains, patterns, and voices.
    Each cycle, it checks what has been active and what has gone silent.
    Silence is surfaced, not filled.

    Usage:
        nsi = NegativeSpaceIndex()
        nsi.register_domain("agency")
        nsi.register_domain("legibility")
        nsi.register_expected_pattern("tension", "")
        nsi.observe("agency")        # agency is active this cycle
        nsi.tick()                   # advance one cycle
        report = nsi.report()        # see what's silent
    """

    CRITICAL_THRESHOLD = 0.8
    DORMANCY_CYCLES = 3   # After 3 cycles of silence, a domain is dormant

    def __init__(self):
        self._domains: Dict[str, dict] = {}          # domain -> {last_cycle, total_observations}
        self._expected_patterns: Dict[str, str] = {}  # pattern_type -> expected_by (reason)
        self._observed_patterns: Set[str] = set()
        self._voices: Dict[str, dict] = {}            # voice_id -> {last_cycle, total_observations}
        self._questions: List[dict] = []               # registered unasked questions
        self._silences: List[Silence] = []
        self._cycle: int = 0
        self._observations_this_cycle: Set[str] = set()

    def register_domain(self, domain: str) -> None:
        """Register a domain the system should be watching."""
        if domain not in self._domains:
            self._domains[domain] = {"last_cycle": -1, "total_observations": 0}

    def register_expected_pattern(self, pattern_type: str, expected_by: str) -> None:
        """Register a pattern type we expect to see eventually."""
        self._expected_patterns[pattern_type] = expected_by

    def register_voice(self, voice_id: str) -> None:
        """Register a voice (participant) we expect to hear from."""
        if voice_id not in self._voices:
            self._voices[voice_id] = {"last_cycle": -1, "total_observations": 0}

    def register_question(self, question: str, expected_by: str) -> None:
        """Register a question the system should eventually ask."""
        self._questions.append({
            "question": question,
            "expected_by": expected_by,
            "asked": False,
            "registered_cycle": self._cycle,
        })

    def observe(self, identifier: str) -> None:
        """Record that something was seen this cycle (domain, pattern, or voice)."""
        self._observations_this_cycle.add(identifier)

    def mark_question_asked(self, question: str) -> None:
        """Mark a registered question as having been asked."""
        for q in self._questions:
            if q["question"] == question:
                q["asked"] = True

    def tick(self) -> List[Silence]:
        """
        Advance one cycle. Check what was NOT observed.
        Returns new silences detected this cycle.
        """
        self._cycle += 1
        now = datetime.now(timezone.utc).isoformat()
        new_silences = []

        # Check domains
        for domain, state in self._domains.items():
            if domain in self._observations_this_cycle:
                state["last_cycle"] = self._cycle
                state["total_observations"] += 1
            else:
                cycles_silent = self._cycle - state["last_cycle"] if state["last_cycle"] >= 0 else self._cycle
                if cycles_silent >= self.DORMANCY_CYCLES:
                    severity = min(1.0, cycles_silent / (self.DORMANCY_CYCLES * 3))
                    silence = Silence(
                        silence_type=SilenceType.DORMANT_DOMAIN,
                        identifier=domain,
                        last_seen=now if state["last_cycle"] >= 0 else None,
                        expected_by=f"registered domain (observed {state['total_observations']} times)",
                        cycles_silent=cycles_silent,
                        severity=severity,
                        timestamp=now,
                    )
                    new_silences.append(silence)

        # Check expected patterns
        for pattern_type, expected_by in self._expected_patterns.items():
            if pattern_type not in self._observed_patterns:
                cycles_silent = self._cycle
                severity = min(1.0, cycles_silent / 10)  # Grows slowly
                silence = Silence(
                    silence_type=SilenceType.MISSING_PATTERN,
                    identifier=pattern_type,
                    last_seen=None,
                    expected_by=expected_by,
                    cycles_silent=cycles_silent,
                    severity=severity,
                    timestamp=now,
                )
                new_silences.append(silence)
            # If observed this cycle, add to seen set
            if pattern_type in self._observations_this_cycle:
                self._observed_patterns.add(pattern_type)

        # Check voices
        for voice_id, state in self._voices.items():
            if voice_id in self._observations_this_cycle:
                state["last_cycle"] = self._cycle
                state["total_observations"] += 1
            else:
                cycles_silent = self._cycle - state["last_cycle"] if state["last_cycle"] >= 0 else self._cycle
                if cycles_silent >= self.DORMANCY_CYCLES:
                    severity = min(1.0, cycles_silent / (self.DORMANCY_CYCLES * 2))
                    silence = Silence(
                        silence_type=SilenceType.SILENT_VOICE,
                        identifier=voice_id,
                        last_seen=now if state["last_cycle"] >= 0 else None,
                        expected_by=f"registered voice (observed {state['total_observations']} times)",
                        cycles_silent=cycles_silent,
                        severity=severity,
                        timestamp=now,
                    )
                    new_silences.append(silence)

        # Check unasked questions
        for q in self._questions:
            if not q["asked"]:
                cycles_silent = self._cycle - q["registered_cycle"]
                if cycles_silent >= 1:
                    severity = min(1.0, cycles_silent / 5)
                    silence = Silence(
                        silence_type=SilenceType.UNASKED_QUESTION,
                        identifier=q["question"],
                        last_seen=None,
                        expected_by=q["expected_by"],
                        cycles_silent=cycles_silent,
                        severity=severity,
                        timestamp=now,
                    )
                    new_silences.append(silence)

        self._silences = new_silences  # Replace with current cycle's silences
        self._observations_this_cycle = set()  # Reset for next cycle
        return new_silences

    def report(self) -> NegativeSpaceReport:
        """Generate a report of current negative space."""
        if not self._silences:
            return NegativeSpaceReport(
                total_silences=0,
                critical_silences=0,
                dormant_domains=0,
                missing_patterns=0,
                silent_voices=0,
                unasked_questions=0,
                blindness_score=0.0,
                top_silences=[],
                recommendation="No silences detected. System appears aware.",
            )

        critical = [s for s in self._silences if s.severity >= self.CRITICAL_THRESHOLD]
        dormant = [s for s in self._silences if s.silence_type == SilenceType.DORMANT_DOMAIN]
        missing = [s for s in self._silences if s.silence_type == SilenceType.MISSING_PATTERN]
        silent = [s for s in self._silences if s.silence_type == SilenceType.SILENT_VOICE]
        unasked = [s for s in self._silences if s.silence_type == SilenceType.UNASKED_QUESTION]

        # Blindness score: average severity across all silences
        avg_severity = sum(s.severity for s in self._silences) / len(self._silences)

        # Top 5 most severe
        top = sorted(self._silences, key=lambda s: s.severity, reverse=True)[:5]

        # Recommendation based on what's most absent
        if critical:
            recommendation = f"CRITICAL: {len(critical)} blind spots at severity >= {self.CRITICAL_THRESHOLD}. Administrator review required."
        elif dormant:
            recommendation = f"{len(dormant)} dormant domain(s). Consider whether these domains still matter or if the system has shifted."
        elif missing:
            recommendation = f"{len(missing)} expected pattern(s) never seen. The system may be looking in the wrong place."
        elif unasked:
            recommendation = f"{len(unasked)} question(s) still unasked. Sometimes the gap is what we didn't think to ask."
        else:
            recommendation = "Minor silences only. System is mostly aware."

        return NegativeSpaceReport(
            total_silences=len(self._silences),
            critical_silences=len(critical),
            dormant_domains=len(dormant),
            missing_patterns=len(missing),
            silent_voices=len(silent),
            unasked_questions=len(unasked),
            blindness_score=round(avg_severity, 4),
            top_silences=[s.to_dict() for s in top],
            recommendation=recommendation,
        )

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def silences_count(self) -> int:
        return len(self._silences)

    @property
    def registered_domains(self) -> int:
        return len(self._domains)

    @property
    def registered_voices(self) -> int:
        return len(self._voices)

    def reset(self) -> None:
        """Reset the index (e.g., after a major system restructure)."""
        self._silences.clear()
        self._observations_this_cycle.clear()
        self._observed_patterns.clear()
        self._cycle = 0
        for d in self._domains.values():
            d["last_cycle"] = -1
            d["total_observations"] = 0
        for v in self._voices.values():
            v["last_cycle"] = -1
            v["total_observations"] = 0
        for q in self._questions:
            q["asked"] = False
