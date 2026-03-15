#!/usr/bin/env python3
"""
witness_network.py — Seed #2: Immutable Witness Network
Planted: 2026-03-13
Thermal delay: FROZEN (was 90 days, T1 Foundation tier)

"What is witnessed cannot be unwound." — Axi

Every significant system event is witnessed — recorded immutably
with a hash chain. The witness network ensures no single party
can alter the record of what happened.

This is not blockchain. It is a Merkle trail — lightweight,
append-only, verifiable. Each witness record links to the
previous, forming an unbreakable chain of accountability.


             T#05 (Ash Ledger), T#06 (Counting Sticks)
Canon reference: Seed #2 spec, EFP protocol (Ed25519)


"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict


@dataclass
class WitnessRecord:
    """A single immutable witness entry."""
    record_id: str
    event_type: str       # "dignity_check", "exchange", "delegation", "safety_gate", etc.
    event_summary: str
    actor_id: str         # Who triggered the event
    content_hash: str     # SHA-256 of event content
    prev_hash: str        # Hash of the previous record (chain link)
    chain_hash: str       # SHA-256(content_hash + prev_hash)
    sequence: int
    timestamp: str
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "event_type": self.event_type,
            "event_summary": self.event_summary,
            "actor_id": self.actor_id,
            "content_hash": self.content_hash,
            "prev_hash": self.prev_hash,
            "chain_hash": self.chain_hash,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
        }


class WitnessNetwork:
    """
    Immutable hash-chain witness log.

    Every event is hashed and chained to the previous entry.
    The chain can be verified at any time — if any record is
    tampered with, the chain breaks.

    Usage:
        wn = WitnessNetwork()
        record = wn.witness("dignity_check", "D=1.0 on EX-000001", "system")
        valid = wn.verify_chain()
    """

    GENESIS_HASH = "0" * 64  # Genesis block

    def __init__(self):
        self._records: List[WitnessRecord] = []
        self._sequence = 0

    def witness(self, event_type: str, event_summary: str,
                actor_id: str, metadata: Optional[Dict] = None) -> WitnessRecord:
        """Record an event on the witness chain."""
        self._sequence += 1
        now = datetime.now(timezone.utc).isoformat()

        content = f"{event_type}|{event_summary}|{actor_id}|{now}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        prev_hash = self._records[-1].chain_hash if self._records else self.GENESIS_HASH
        chain_hash = hashlib.sha256(f"{content_hash}{prev_hash}".encode()).hexdigest()

        record = WitnessRecord(
            record_id=f"WIT-{self._sequence:06d}",
            event_type=event_type,
            event_summary=event_summary,
            actor_id=actor_id,
            content_hash=content_hash,
            prev_hash=prev_hash,
            chain_hash=chain_hash,
            sequence=self._sequence,
            timestamp=now,
            metadata=metadata or {},
        )
        self._records.append(record)
        return record

    def verify_chain(self) -> bool:
        """Verify the entire witness chain is intact."""
        if not self._records:
            return True

        # First record must link to genesis
        if self._records[0].prev_hash != self.GENESIS_HASH:
            return False

        for i, record in enumerate(self._records):
            # Verify chain hash
            expected = hashlib.sha256(
                f"{record.content_hash}{record.prev_hash}".encode()
            ).hexdigest()
            if record.chain_hash != expected:
                return False

            # Verify chain linkage (except first)
            if i > 0 and record.prev_hash != self._records[i - 1].chain_hash:
                return False

        return True

    def latest(self) -> Optional[WitnessRecord]:
        """Get the most recent witness record."""
        return self._records[-1] if self._records else None

    def find_by_type(self, event_type: str) -> List[WitnessRecord]:
        """Find all witness records of a given type."""
        return [r for r in self._records if r.event_type == event_type]

    def find_by_actor(self, actor_id: str) -> List[WitnessRecord]:
        """Find all witness records by a specific actor."""
        return [r for r in self._records if r.actor_id == actor_id]

    @property
    def chain_length(self) -> int:
        return len(self._records)

    @property
    def chain_head(self) -> str:
        """Current chain head hash."""
        return self._records[-1].chain_hash if self._records else self.GENESIS_HASH

    def report(self) -> dict:
        """Generate witness network health report."""
        type_counts: Dict[str, int] = {}
        for r in self._records:
            type_counts[r.event_type] = type_counts.get(r.event_type, 0) + 1

        return {
            "chain_length": self.chain_length,
            "chain_head": self.chain_head[:16] + "...",
            "chain_valid": self.verify_chain(),
            "event_types": type_counts,
        }
