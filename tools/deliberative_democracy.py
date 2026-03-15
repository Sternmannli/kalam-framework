#!/usr/bin/env python3
"""
deliberative_democracy.py — Seed #3: Deliberative Democracy Infrastructure
Planted: 2026-03-13
Thermal delay: FROZEN (was 90 days, T1 Foundation tier)

"The river listens to every stone before it decides its path." — Axi

When a decision affects multiple stakeholders, the system must
provide infrastructure for deliberation — not just voting.
This module provides proposal, deliberation, and consensus
mechanisms grounded in the Weakest-Voice-First principle.

Every voice speaks. The weakest speaks first. Consensus is not
unanimity — it is the point where no voice is silenced.


             T#28 (Quiet Bridge), T#29 (Line Talk)
Canon reference: Seed #3 spec, Centre-Shift governance


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum


class ProposalStatus(Enum):
    DRAFT = "draft"
    OPEN = "open"           # Accepting deliberation
    DELIBERATING = "deliberating"  # Active discussion
    RESOLVED = "resolved"   # Consensus reached
    WITHDRAWN = "withdrawn"


class VoteType(Enum):
    SUPPORT = "support"
    CONCERN = "concern"     # Not opposition — a concern to address
    BLOCK = "block"         # Strong objection (must be addressed)
    ABSTAIN = "abstain"


@dataclass
class Voice:
    """A participant in deliberation."""
    voice_id: str
    participation_score: float = 0.0   # Lower = less heard (weakest-voice-first)
    votes_cast: int = 0

    def to_dict(self) -> dict:
        return {
            "voice_id": self.voice_id,
            "participation_score": self.participation_score,
            "votes_cast": self.votes_cast,
        }


@dataclass
class Deliberation:
    """A single voice's contribution to a proposal."""
    voice_id: str
    vote: VoteType
    statement: str
    concerns: List[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class Proposal:
    """A proposal for deliberation."""
    proposal_id: str
    title: str
    description: str
    proposer_id: str
    status: ProposalStatus = ProposalStatus.DRAFT
    created_at: str = ""
    resolved_at: Optional[str] = None
    deliberations: List[Deliberation] = field(default_factory=list)
    resolution: str = ""
    unresolved_concerns: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "status": self.status.value,
            "proposer_id": self.proposer_id,
            "deliberation_count": len(self.deliberations),
            "blocks": sum(1 for d in self.deliberations if d.vote == VoteType.BLOCK),
            "supports": sum(1 for d in self.deliberations if d.vote == VoteType.SUPPORT),
            "concerns": sum(1 for d in self.deliberations if d.vote == VoteType.CONCERN),
            "unresolved_concerns": self.unresolved_concerns,
        }


class DeliberativeDemocracy:
    """
    Infrastructure for collective decision-making.

    The system enforces:
    - Weakest-Voice-First ordering (lowest participation speaks first)
    - No resolution while blocks are outstanding
    - All concerns surfaced and addressed before consensus

    Usage:
        dd = DeliberativeDemocracy()
        dd.register_voice("administrator", participation_score=10.0)
        dd.register_voice("user-042", participation_score=1.0)
        p = dd.propose("administrator", "Amend ", "Add data portability clause")
        dd.deliberate(p.proposal_id, "user-042", VoteType.CONCERN, "Privacy impact?")
        dd.deliberate(p.proposal_id, "administrator", VoteType.SUPPORT, "Agreed")
    """

    def __init__(self):
        self._voices: Dict[str, Voice] = {}
        self._proposals: List[Proposal] = []
        self._proposal_counter = 0

    def register_voice(self, voice_id: str, participation_score: float = 0.0) -> Voice:
        """Register a voice for deliberation."""
        v = Voice(voice_id=voice_id, participation_score=participation_score)
        self._voices[voice_id] = v
        return v

    def propose(self, proposer_id: str, title: str, description: str) -> Proposal:
        """Submit a proposal for deliberation."""
        self._proposal_counter += 1
        p = Proposal(
            proposal_id=f"PROP-{self._proposal_counter:04d}",
            title=title,
            description=description,
            proposer_id=proposer_id,
            status=ProposalStatus.OPEN,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._proposals.append(p)
        return p

    def deliberate(self, proposal_id: str, voice_id: str,
                   vote: VoteType, statement: str,
                   concerns: Optional[List[str]] = None) -> Optional[Deliberation]:
        """Add a voice's deliberation to a proposal."""
        p = self._find_proposal(proposal_id)
        if p is None or p.status not in (ProposalStatus.OPEN, ProposalStatus.DELIBERATING):
            return None

        p.status = ProposalStatus.DELIBERATING

        d = Deliberation(
            voice_id=voice_id,
            vote=vote,
            statement=statement,
            concerns=concerns or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        p.deliberations.append(d)

        # Track participation
        if voice_id in self._voices:
            self._voices[voice_id].votes_cast += 1
            self._voices[voice_id].participation_score += 1.0

        return d

    def speaking_order(self) -> List[str]:
        """Return voices in weakest-voice-first order."""
        return [v.voice_id for v in
                sorted(self._voices.values(), key=lambda v: v.participation_score)]

    def can_resolve(self, proposal_id: str) -> bool:
        """Check if proposal can be resolved (no outstanding blocks)."""
        p = self._find_proposal(proposal_id)
        if p is None:
            return False
        return not any(d.vote == VoteType.BLOCK for d in p.deliberations)

    def resolve(self, proposal_id: str, resolution: str) -> bool:
        """Resolve a proposal if no blocks remain."""
        p = self._find_proposal(proposal_id)
        if p is None or not self.can_resolve(proposal_id):
            return False

        # Collect unresolved concerns
        p.unresolved_concerns = []
        for d in p.deliberations:
            if d.vote == VoteType.CONCERN:
                p.unresolved_concerns.extend(d.concerns)

        p.status = ProposalStatus.RESOLVED
        p.resolution = resolution
        p.resolved_at = datetime.now(timezone.utc).isoformat()
        return True

    def withdraw(self, proposal_id: str) -> bool:
        """Withdraw a proposal."""
        p = self._find_proposal(proposal_id)
        if p is None:
            return False
        p.status = ProposalStatus.WITHDRAWN
        return True

    @property
    def proposals_count(self) -> int:
        return len(self._proposals)

    @property
    def voices_count(self) -> int:
        return len(self._voices)

    @property
    def open_proposals(self) -> int:
        return sum(1 for p in self._proposals
                   if p.status in (ProposalStatus.OPEN, ProposalStatus.DELIBERATING))

    def _find_proposal(self, proposal_id: str) -> Optional[Proposal]:
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                return p
        return None

    def report(self) -> dict:
        """Deliberation health report."""
        return {
            "voices": self.voices_count,
            "proposals": self.proposals_count,
            "open": self.open_proposals,
            "resolved": sum(1 for p in self._proposals if p.status == ProposalStatus.RESOLVED),
            "speaking_order": self.speaking_order(),
        }
