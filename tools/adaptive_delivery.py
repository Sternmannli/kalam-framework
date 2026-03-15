#!/usr/bin/env python3
"""
personalized_parables.py — Seed #7: Personalized Parables
Planted: 2026-03-13
Thermal delay: FROZEN (was 14 days, T3 Wisdom tier)

"The same river speaks differently to the farmer and the fish." — Axi

Proverbs are universal but their meaning lands differently
depending on who hears them. This module adapts wisdom delivery
to the user's context — their domain, their history, their
current emotional state — without changing the proverb itself.

The proverb stays. The frame changes.


             T#16 (Wind Door — environmental negotiation)
Canon reference: Seed #7 spec, ENKI multi-language delivery


"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class UserContext:
    """Context for personalizing wisdom delivery."""
    user_id: str
    domains: List[str] = field(default_factory=list)      # What domains they engage with
    history_count: int = 0                                  # How many exchanges
    recent_themes: List[str] = field(default_factory=list)  # Recent pattern types
    preferred_style: str = "direct"                         # "direct", "narrative", "questioning"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domains": self.domains,
            "history_count": self.history_count,
            "preferred_style": self.preferred_style,
        }


@dataclass
class ParableDelivery:
    """A personalized delivery of a proverb."""
    delivery_id: str
    proverb_id: str
    proverb_text: str
    user_id: str
    frame: str               # The contextual framing
    delivery_style: str
    relevance_score: float   # 0.0 = generic, 1.0 = perfectly matched
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "delivery_id": self.delivery_id,
            "proverb_id": self.proverb_id,
            "proverb_text": self.proverb_text,
            "user_id": self.user_id,
            "frame": self.frame,
            "relevance_score": round(self.relevance_score, 4),
        }


class PersonalizedParables:
    """
    Adapts proverb delivery to user context without altering the proverb.

    The proverb is immutable. The frame is alive:
    - For a farmer: "This proverb is about patience with the soil."
    - For a developer: "This proverb is about patience with the build."
    - The proverb itself: "What ripens too fast rots first."

    Usage:
        pp = PersonalizedParables()
        pp.register_user("D-001", domains=["technology", "ethics"])
        delivery = pp.deliver("P#EMERGE-0022", "Capture fast. Tend slow.",
                              "D-001", user_theme="velocity")
    """

    # Frame templates by style
    FRAME_TEMPLATES = {
        "direct": "In your domain of {domain}: {proverb}",
        "narrative": "Consider this — one who works in {domain} might hear: {proverb}",
        "questioning": "What would it mean, in {domain}, if {proverb}?",
    }

    def __init__(self):
        self._users: Dict[str, UserContext] = {}
        self._deliveries: List[ParableDelivery] = []
        self._delivery_counter = 0

    def register_user(self, user_id: str, domains: Optional[List[str]] = None,
                       preferred_style: str = "direct") -> UserContext:
        """Register a user's context for personalization."""
        ctx = UserContext(
            user_id=user_id,
            domains=domains or [],
            preferred_style=preferred_style,
        )
        self._users[user_id] = ctx
        return ctx

    def update_context(self, user_id: str, domain: Optional[str] = None,
                       theme: Optional[str] = None) -> None:
        """Update user context after an interaction."""
        ctx = self._users.get(user_id)
        if ctx is None:
            return
        ctx.history_count += 1
        if domain and domain not in ctx.domains:
            ctx.domains.append(domain)
        if theme:
            ctx.recent_themes.append(theme)
            # Keep only last 10 themes
            ctx.recent_themes = ctx.recent_themes[-10:]

    def deliver(self, proverb_id: str, proverb_text: str,
                user_id: str, user_theme: str = "") -> ParableDelivery:
        """Deliver a proverb with personalized framing."""
        self._delivery_counter += 1
        ctx = self._users.get(user_id)

        # Build frame based on user context
        style = ctx.preferred_style if ctx else "direct"
        domain = user_theme or (ctx.domains[0] if ctx and ctx.domains else "your work")
        relevance = self._compute_relevance(proverb_text, ctx, user_theme)

        template = self.FRAME_TEMPLATES.get(style, self.FRAME_TEMPLATES["direct"])
        frame = template.format(domain=domain, proverb=proverb_text)

        delivery = ParableDelivery(
            delivery_id=f"PARABLE-{self._delivery_counter:04d}",
            proverb_id=proverb_id,
            proverb_text=proverb_text,
            user_id=user_id,
            frame=frame,
            delivery_style=style,
            relevance_score=relevance,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._deliveries.append(delivery)

        # Update context
        if ctx:
            ctx.history_count += 1

        return delivery

    def _compute_relevance(self, proverb_text: str,
                           ctx: Optional[UserContext],
                           theme: str) -> float:
        """Compute how relevant this proverb is to the user's context."""
        if ctx is None:
            return 0.3  # Generic delivery

        score = 0.3  # Base
        # Domain match
        if theme and theme in ctx.domains:
            score += 0.3
        # History depth (more history = better matching possible)
        if ctx.history_count > 5:
            score += 0.2
        # Theme recency
        if theme and theme in ctx.recent_themes:
            score += 0.2
        return min(1.0, score)

    def deliveries_for_user(self, user_id: str) -> List[ParableDelivery]:
        """Get all deliveries for a specific user."""
        return [d for d in self._deliveries if d.user_id == user_id]

    @property
    def users_count(self) -> int:
        return len(self._users)

    @property
    def deliveries_count(self) -> int:
        return len(self._deliveries)

    @property
    def avg_relevance(self) -> float:
        if not self._deliveries:
            return 0.0
        return sum(d.relevance_score for d in self._deliveries) / len(self._deliveries)

    def report(self) -> dict:
        """Personalized parables health report."""
        return {
            "users_registered": self.users_count,
            "deliveries": self.deliveries_count,
            "avg_relevance": round(self.avg_relevance, 4),
        }
