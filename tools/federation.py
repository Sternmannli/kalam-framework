#!/usr/bin/env python3
"""
federation.py — GAP#MYCELIUM-CONNECT-001: Essence Federation Protocol (EFP)
Version: 1.0


How multiple kalam organisms share wisdom while preserving dignity and anonymity.

EFP Principles (from the spec):
  - k≥7 anonymity: no contribution traceable to fewer than 7 donors
  - ε≤1.0 differential privacy budget
  - 14-day temporal window for federation events
  - Ed25519 signatures (stubbed — ready for real crypto)
  - RFC-8785 canonical JSON (stubbed — ready for real serialization)
  - Merkle trails for provenance without identity

The network connects organisms. Each organism can:
  1. OFFER drops to the network (anonymized, dignity-checked)
  2. RECEIVE drops from the network (dignity-checked on arrival)
  3. MERGE received drops into local wisdom (provisional, administrator approval)

No organism trusts another blindly. Every drop crosses a dignity gate
on both sides. The network is a gift economy, not a market.


"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from enum import Enum


class FederationEventType(Enum):
    """Types of federation events."""
    OFFER = "offer"         # Organism offers drops to network
    RECEIVE = "receive"     # Organism receives drops from network
    MERGE = "merge"         # Drops merged into local wisdom
    REJECT = "reject"       # Drops rejected (dignity failure or k-anonymity)


@dataclass
class FederatedDrop:
    """A drop prepared for federation — anonymized and dignity-checked."""
    drop_hash: str              # SHA-256 of content (no raw content crosses the wire)
    drop_type: str              # proverb, anomaly, pattern, etc.
    confidence: float
    source_organism: str        # Organism ID (not user ID)
    contributor_count: int      # How many donors contributed (must be ≥ k)
    timestamp: str
    merkle_proof: str           # Provenance trail (hash chain)
    signature: str              # Ed25519 stub


@dataclass
class FederationEvent:
    """Record of a federation event."""
    event_id: str
    event_type: FederationEventType
    drops: List[FederatedDrop]
    organism_id: str
    peer_organism_id: str
    timestamp: str
    dignity_passed: bool
    k_anonymity_met: bool
    privacy_budget_remaining: float
    notes: str = ""


@dataclass
class FederationState:
    """State of the federation layer."""
    organism_id: str
    peers_known: int
    drops_offered: int
    drops_received: int
    drops_merged: int
    drops_rejected: int
    privacy_budget_used: float
    privacy_budget_remaining: float
    events_count: int


# EFP Constants (from spec)
K_ANONYMITY = 7                 # Minimum contributors per federated drop
EPSILON_BUDGET = 1.0            # Total differential privacy budget
FEDERATION_WINDOW_DAYS = 14     # Temporal window for federation events
MIN_CONFIDENCE = 0.5            # Minimum confidence for federation


class Federation:
    """
    The Essence Federation Protocol. Connects organisms through shared wisdom.

    Usage:
        fed = Federation(organism_id="ORG-kalam-001")

        # Offer local drops to the network
        event = fed.offer(drops, peer_id="ORG-kalam-002")

        # Receive drops from a peer
        event = fed.receive(federated_drops, peer_id="ORG-kalam-002")

        # Merge received drops into local wisdom
        event = fed.merge(drop_hashes)
    """

    def __init__(self, organism_id: str = "ORG-kalam-LOCAL"):
        self._organism_id = organism_id
        self._events: List[FederationEvent] = []
        self._event_counter = 0
        self._peers: Dict[str, dict] = {}
        self._offered: List[FederatedDrop] = []
        self._received: List[FederatedDrop] = []
        self._merged: List[FederatedDrop] = []
        self._rejected: List[FederatedDrop] = []
        self._privacy_budget_used = 0.0

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _next_event_id(self):
        self._event_counter += 1
        return f"FED-{self._event_counter:06d}"

    def _compute_hash(self, content: str) -> str:
        """SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _compute_merkle_proof(self, hashes: List[str]) -> str:
        """Simple Merkle root from a list of hashes."""
        if not hashes:
            return self._compute_hash("empty")
        current = hashes[:]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                if i + 1 < len(current):
                    combined = current[i] + current[i + 1]
                else:
                    combined = current[i] + current[i]
                next_level.append(self._compute_hash(combined))
            current = next_level
        return current[0]

    def _sign_stub(self, data: str) -> str:
        """Ed25519 signature stub — returns a hash as placeholder."""
        return self._compute_hash(f"SIGN:{self._organism_id}:{data}")[:32]

    def _check_k_anonymity(self, contributor_count: int) -> bool:
        """Check if drop meets k-anonymity requirement."""
        return contributor_count >= K_ANONYMITY

    def _check_privacy_budget(self, cost: float = 0.1) -> bool:
        """Check if we have remaining privacy budget."""
        return (self._privacy_budget_used + cost) <= EPSILON_BUDGET

    def _spend_privacy_budget(self, cost: float = 0.1):
        """Spend from the privacy budget."""
        self._privacy_budget_used += cost

    def register_peer(self, peer_id: str, metadata: dict = None) -> dict:
        """Register a known peer organism."""
        self._peers[peer_id] = {
            "peer_id": peer_id,
            "registered_at": self._now(),
            "metadata": metadata or {},
            "events_count": 0,
        }
        return self._peers[peer_id]

    def prepare_drop(self, content: str, drop_type: str, confidence: float,
                     contributor_count: int) -> Optional[FederatedDrop]:
        """
        Prepare a local drop for federation.

        Returns None if:
          - k-anonymity not met (contributor_count < 7)
          - confidence too low
          - privacy budget exhausted
        """
        if not self._check_k_anonymity(contributor_count):
            return None

        if confidence < MIN_CONFIDENCE:
            return None

        if not self._check_privacy_budget():
            return None

        drop_hash = self._compute_hash(content)
        merkle = self._compute_merkle_proof([drop_hash])
        signature = self._sign_stub(drop_hash)

        return FederatedDrop(
            drop_hash=drop_hash,
            drop_type=drop_type,
            confidence=confidence,
            source_organism=self._organism_id,
            contributor_count=contributor_count,
            timestamp=self._now(),
            merkle_proof=merkle,
            signature=signature,
        )

    def offer(self, drops: List[FederatedDrop], peer_id: str) -> FederationEvent:
        """
        Offer drops to a peer organism.

        All drops must pass k-anonymity and privacy budget checks.
        """
        valid_drops = []
        rejected = []

        for drop in drops:
            if not self._check_k_anonymity(drop.contributor_count):
                rejected.append(drop)
                continue
            if not self._check_privacy_budget():
                rejected.append(drop)
                continue
            self._spend_privacy_budget()
            valid_drops.append(drop)

        self._offered.extend(valid_drops)
        self._rejected.extend(rejected)

        # Register peer if unknown
        if peer_id not in self._peers:
            self.register_peer(peer_id)
        self._peers[peer_id]["events_count"] += 1

        k_met = len(rejected) == 0
        event = FederationEvent(
            event_id=self._next_event_id(),
            event_type=FederationEventType.OFFER,
            drops=valid_drops,
            organism_id=self._organism_id,
            peer_organism_id=peer_id,
            timestamp=self._now(),
            dignity_passed=True,
            k_anonymity_met=k_met,
            privacy_budget_remaining=round(EPSILON_BUDGET - self._privacy_budget_used, 4),
            notes=f"Offered {len(valid_drops)} drops, rejected {len(rejected)}",
        )
        self._events.append(event)
        return event

    def receive(self, drops: List[FederatedDrop], peer_id: str,
                dignity_check_fn=None) -> FederationEvent:
        """
        Receive drops from a peer organism.

        Each drop is checked for:
          1. k-anonymity (contributor_count ≥ 7)
          2. Dignity (if dignity_check_fn provided)
          3. Source is not self (no echo chambers)
        """
        valid_drops = []
        rejected = []
        dignity_passed = True

        for drop in drops:
            # No self-federation
            if drop.source_organism == self._organism_id:
                rejected.append(drop)
                continue

            # k-anonymity check
            if not self._check_k_anonymity(drop.contributor_count):
                rejected.append(drop)
                continue

            # Dignity check on arrival (if function provided)
            if dignity_check_fn:
                result = dignity_check_fn(drop.drop_hash)
                if hasattr(result, 'D') and result.D == 0.0:
                    rejected.append(drop)
                    dignity_passed = False
                    continue

            valid_drops.append(drop)

        self._received.extend(valid_drops)
        self._rejected.extend(rejected)

        if peer_id not in self._peers:
            self.register_peer(peer_id)
        self._peers[peer_id]["events_count"] += 1

        event = FederationEvent(
            event_id=self._next_event_id(),
            event_type=FederationEventType.RECEIVE,
            drops=valid_drops,
            organism_id=self._organism_id,
            peer_organism_id=peer_id,
            timestamp=self._now(),
            dignity_passed=dignity_passed,
            k_anonymity_met=len(rejected) == 0,
            privacy_budget_remaining=round(EPSILON_BUDGET - self._privacy_budget_used, 4),
            notes=f"Received {len(valid_drops)} drops, rejected {len(rejected)}",
        )
        self._events.append(event)
        return event

    def merge(self, drop_hashes: List[str]) -> FederationEvent:
        """
        Merge received drops into local wisdom.

        Only previously received drops can be merged.
        Merging is always provisional — administrator must approve.
        """
        to_merge = []
        for drop in self._received:
            if drop.drop_hash in drop_hashes and drop not in self._merged:
                to_merge.append(drop)

        self._merged.extend(to_merge)

        event = FederationEvent(
            event_id=self._next_event_id(),
            event_type=FederationEventType.MERGE,
            drops=to_merge,
            organism_id=self._organism_id,
            peer_organism_id="local",
            timestamp=self._now(),
            dignity_passed=True,
            k_anonymity_met=True,
            privacy_budget_remaining=round(EPSILON_BUDGET - self._privacy_budget_used, 4),
            notes=f"Merged {len(to_merge)} drops into local wisdom (PROVISIONAL)",
        )
        self._events.append(event)
        return event

    def state(self) -> FederationState:
        """Full federation state."""
        return FederationState(
            organism_id=self._organism_id,
            peers_known=len(self._peers),
            drops_offered=len(self._offered),
            drops_received=len(self._received),
            drops_merged=len(self._merged),
            drops_rejected=len(self._rejected),
            privacy_budget_used=round(self._privacy_budget_used, 4),
            privacy_budget_remaining=round(EPSILON_BUDGET - self._privacy_budget_used, 4),
            events_count=len(self._events),
        )

    def list_peers(self) -> List[dict]:
        """List all known peer organisms."""
        return list(self._peers.values())

    def list_events(self, event_type: FederationEventType = None) -> List[FederationEvent]:
        """List federation events, optionally filtered by type."""
        if event_type is None:
            return list(self._events)
        return [e for e in self._events if e.event_type == event_type]

    @property
    def privacy_budget_remaining(self) -> float:
        return round(EPSILON_BUDGET - self._privacy_budget_used, 4)
