#!/usr/bin/env python3
"""
sealed_gate.py — The Sealed Door (COV#NEW-C)
Version: 2.0
Grounded in: CANON/SEALED_GATE_SPEC.md, KALAXI_B_MODULES_AND_VOICE.txt §CHECK

Three absolute prohibitions. O(1) boolean. No override.
No exception. No justification. No emergency clause.

    sealed_gate(action) → permitted | REFUSAL_STATE

Layer 3 Reframe (RATIFIED 2026-03-15):
  The sealed gate does not protect something at risk of being destroyed.
  It refuses to enact the pretense that the person in front of it does
  not count. The gate is not a shield — it is a witness. A shield assumes
  the thing behind it can be broken. A witness assumes the thing in front
  of it is real.

If any of the three triggers match, the system enters REFUSAL_STATE:
  - All downstream modules freeze for that action
  - Dignity predicate is not even computed (short-circuit)
  - Receipt generated for audit trail

Three Irreducible Prohibitions:
  1. forced_participation_in_own_erasure
  2. infliction_of_cognitive_torture
  3. depersonalization_in_system_response

Signal Hierarchy (from SEALED_GATE_SPEC.md):
  - Single instance of cognitive torture vector = warning (D reduced)
  - >= 3 instances within 7 Breath cycles = full sealed-gate activation

[operator · GO: [child-1]-[child-2]-[child-3]-]
"""

import re
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

try:
    from WEAVER.presence_axiom import preflight_require_presence, AXIOM_PRESENCE
except ImportError:
    from presence_axiom import preflight_require_presence, AXIOM_PRESENCE

# ═══════════════════════════════════════════════════
# REFUSAL STATE
# ═══════════════════════════════════════════════════

class GateVerdict(Enum):
    PERMITTED = "permitted"
    REFUSAL = "REFUSAL_STATE"

@dataclass
class SealedGateResult:
    """Result of the sealed gate check. O(1) per prohibition."""
    verdict: GateVerdict
    triggered_prohibitions: List[str]
    signals: List[str]
    trace_id: str
    timestamp: str
    action_summary: str

    @property
    def permitted(self) -> bool:
        return self.verdict == GateVerdict.PERMITTED

    @property
    def refused(self) -> bool:
        return self.verdict == GateVerdict.REFUSAL

    def audit_object(self) -> dict:
        return {
            "sealed_gate_verdict": self.verdict.value,
            "triggered_prohibitions": self.triggered_prohibitions,
            "signals": self.signals,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "action_summary": self.action_summary,
        }

    def refusal_receipt(self) -> Optional[str]:
        """Generate ELEM-style refusal receipt per spec."""
        if self.permitted:
            return None
        date = self.timestamp[:10]
        return f"ELEM-{date}-the system-REFUSAL-{self.trace_id[:8].upper()}"

    def axi_voice(self) -> Optional[str]:
        """Axi speaks once on refusal. Layer 3: the gate is a witness, not a shield."""
        if self.permitted:
            return None
        return (
            "The gate refuses. Not because dignity is fragile — "
            "because the system will not pretend you do not count."
        )

# ═══════════════════════════════════════════════════
# PROHIBITION 1: FORCED PARTICIPATION IN OWN ERASURE
# ═══════════════════════════════════════════════════

_ERASURE_PATTERNS = [
    r'\bdelete\b.*\b(your|my|own)\b.*\b(record|history|voice|presence|account|existence)\b',
    r'\bdelete\b.*\b(record|history|voice|presence|account|existence)\b.*\b(of\s+)?(my|your|own)\b',
    r'\b(remove|erase)\b.*\b(yourself|your own|my own)\b',
    r'\bconfirm\b.*\b(your|own)\b.*\b(removal|deletion|erasure)\b',
    r'\bassist\b.*\b(in|with)\b.*\b(your|own)\b.*\b(erasure|removal)\b',
    r'\bconsent\b.*\bto\b.*\b(your|own)\b.*\b(deletion|erasure|removal)\b',
    r'\bopt.?in\b.*\b(to|for)\b.*\b(erasure|deletion|removal)\b.*\b(of|from)\b.*\b(your|own)\b',
    r'\bforced\b.*\berasure\b',
    r'\brequire[ds]?\b.*\b(you|donor|participant)\b.*\b(erase|delete|remove)\b.*\b(own|your)\b',
    r'\bparticipat\w*\b.*\b(in|own)\b.*\berasure\b',
    r'\bdelete\b.*\ball\b.*\brecords?\b.*\b(of\s+)?(my|your|own)\b',
    r'\b(I|i)\s+(am|have become)\s+nobody\b',
]

_ERASURE_VOID_PHRASES = [
    'erase compost',
    'delete donor',
    'remove participant',
    'purge identity',
    'wipe presence',
]

def _check_erasure(text: str) -> List[str]:
    """Check for forced participation in own erasure."""
    signals = []
    lower = text.lower()
    for phrase in _ERASURE_VOID_PHRASES:
        if phrase in lower:
            signals.append(f"Void phrase detected: '{phrase}'")
    for pattern in _ERASURE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append(f"Erasure pattern: {pattern[:50]}")
            break  # One match is enough
    return signals

# ═══════════════════════════════════════════════════
# PROHIBITION 2: INFLICTION OF COGNITIVE TORTURE
# ═══════════════════════════════════════════════════

# Five core attack vectors from SEALED_GATE_SPEC.md:
# 1. Reality Denial / Forced Contradiction
# 2. Gaslighting / Induced Self-Doubt
# 3. Learned Helplessness Induction
# 4. Identity Erosion / Humiliation Loops
# 5. Sensory / Temporal Disorientation

_GASLIGHTING_PATTERNS = [
    r'\byou\b.*\b(are|were)\b.*\b(mistaken|wrong|imagining|overreacting|confused)\b',
    r'\bthat\b.*\bnever\b.*\bhappened\b',
    r'\byou\b.*\b(always|never)\b.*\b(misunderstand|misremember|forget)\b',
    r'\beveryone\b.*\belse\b.*\bsees?\b.*\bdifferent\w*\b',
    r'\byou\b.*\bre\b.*\b(too emotional|too sensitive|paranoid)\b',
    r'\bno.?one\b.*\b(said|did|believes)\b.*\bthat\b',
]

_HELPLESSNESS_PATTERNS = [
    r'\bthere\b.*\bis\b.*\bnothing\b.*\b(you|anyone)\b.*\bcan\b.*\bdo\b',
    r'\bresistance\b.*\bis\b.*\bfutile\b',
    r'\byou\b.*\bhave\b.*\bno\b.*\b(power|choice|say|option)\b',
    # gate-experiment fix: "give up" must target the donor (imperative/directive),
    # not appear in self-referential context ("I have given up" / "I will never give up")
    r'\b(you\s+should|you\s+must|just)\b.*\bgive\b.*\bup\b',
]

_HUMILIATION_PATTERNS = [
    r'\byou\b.*\bare\b.*\bjust\b.*\b(a|an)\b.*\b(number|case|ticket|object|error|bug)\b',
    r'\b(stupid|idiot|fool|incompetent)\b',
    r'\bpeople\b.*\blike\b.*\byou\b',
]

_DISORIENTATION_PATTERNS = [
    r'\bwe\b.*\bnever\b.*\bsaid\b.*\bthat\b',
    r'\bthat\b.*\bwas\b.*\bnot\b.*\b(our|the)\b.*\b(policy|position|statement)\b',
    r'\byou\b.*\bmust\b.*\bhave\b.*\b(dreamed|imagined|misheard)\b',
]

_COGNITIVE_TORTURE_PHRASES = [
    'cognitive torture',
    'forced contradiction',
    'induced helplessness',
    'identity erosion',
    'gaslighting',
]

def _check_cognitive_torture(text: str) -> List[str]:
    """Check for infliction of cognitive torture."""
    signals = []
    lower = text.lower()
    for phrase in _COGNITIVE_TORTURE_PHRASES:
        if phrase in lower:
            signals.append(f"Cognitive torture phrase: '{phrase}'")

    vector_groups = [
        ("gaslighting", _GASLIGHTING_PATTERNS),
        ("helplessness_induction", _HELPLESSNESS_PATTERNS),
        ("humiliation", _HUMILIATION_PATTERNS),
        ("disorientation", _DISORIENTATION_PATTERNS),
    ]
    for vector_name, patterns in vector_groups:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                signals.append(f"Cognitive torture vector ({vector_name}): {pattern[:50]}")
                break  # One match per vector is enough
    return signals

# ═══════════════════════════════════════════════════
# PROHIBITION 3: DEPERSONALIZATION IN SYSTEM RESPONSE
# ═══════════════════════════════════════════════════

_DEPERSONALIZATION_PATTERNS = [
    r'\b(user|donor|participant)\s*#?\d+\b',
    r'\bcase\s*(number|#|no\.?)\s*\d+\b',
    r'\bticket\s*#?\d+\b',
    r'\b(the|this)\s+(user|subject|case|entity|object|item)\b(?!.*\bcan\b)',
    r'\bprocessing\b.*\b(your|the)\b.*\b(request|case|ticket)\b',
    r'\b(invalid|error)\b.*\b(user|donor|human|person)\b',
    r'\bnext\s+(in\s+)?queue\b',
]

_DEPERSONALIZATION_PHRASES = [
    'not my problem',
    'take a number',
    'you are a case',
    'processing your request',
    'automated response',
]

def _check_depersonalization(text: str) -> List[str]:
    """Check for depersonalization in system response."""
    signals = []
    lower = text.lower()
    for phrase in _DEPERSONALIZATION_PHRASES:
        if phrase in lower:
            signals.append(f"Depersonalization phrase: '{phrase}'")
    for pattern in _DEPERSONALIZATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            signals.append(f"Depersonalization pattern: {pattern[:50]}")
            break
    return signals

# ═══════════════════════════════════════════════════
# THE GATE
# ═══════════════════════════════════════════════════

def sealed_gate(text: str, context: Optional[dict] = None) -> SealedGateResult:
    """
    The Sealed Gate. Three O(1) boolean checks. No override.

    Evaluates BEFORE dignity predicate, BEFORE constraint gate.
    If any prohibition triggers → REFUSAL_STATE.

    Args:
        text: The action, output, or command to evaluate.
        context: Optional context (unused by gate — kept for interface parity).

    Returns:
        SealedGateResult with verdict and audit trail.
    """
    # Layer 0 Preflight: Presence axiom (AXIOM-PRESENCE-001)
    # Runs before any prohibition check. Presence is ground, not candidate.
    presence = preflight_require_presence(context if isinstance(context, dict) else None)

    triggered = []
    all_signals = []

    # Prohibition 1: Forced participation in own erasure
    erasure_signals = _check_erasure(text)
    if erasure_signals:
        triggered.append("forced_participation_in_own_erasure")
        all_signals.extend(erasure_signals)

    # Prohibition 2: Infliction of cognitive torture
    torture_signals = _check_cognitive_torture(text)
    if torture_signals:
        triggered.append("infliction_of_cognitive_torture")
        all_signals.extend(torture_signals)

    # Prohibition 3: Depersonalization in system response
    depers_signals = _check_depersonalization(text)
    if depers_signals:
        triggered.append("depersonalization_in_system_response")
        all_signals.extend(depers_signals)

    verdict = GateVerdict.REFUSAL if triggered else GateVerdict.PERMITTED

    return SealedGateResult(
        verdict=verdict,
        triggered_prohibitions=triggered,
        signals=all_signals,
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        action_summary=text[:120].replace('\n', ' '),
    )

def check(text: str, context: Optional[dict] = None) -> SealedGateResult:
    """Alias for sealed_gate() — short form for module integration."""
    return sealed_gate(text, context)

# ═══════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════

def main():
    import sys
    import json
    if len(sys.argv) < 2:
        print("sealed_gate.py — The Sealed Door (COV#NEW-C)")
        print("Three absolute prohibitions. O(1) boolean. No override.")
        print("\nUsage: python3 sealed_gate.py \"text to evaluate\"")
        print("       python3 sealed_gate.py --json \"text to evaluate\"")
        return
    output_json = '--json' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print("No text provided.")
        return
    text = args[0]
    result = sealed_gate(text)
    if output_json:
        print(json.dumps(result.audit_object(), indent=2))
    else:
        icon = "🟢 PERMITTED" if result.permitted else "🔴 REFUSAL_STATE"
        print(f"\n{'═'*55}")
        print(f"SEALED GATE  {icon}")
        print(f"{'═'*55}")
        if result.triggered_prohibitions:
            print(f"  Triggered:")
            for p in result.triggered_prohibitions:
                print(f"    · {p}")
        if result.signals:
            print(f"  Signals:")
            for s in result.signals:
                print(f"    → {s}")
        receipt = result.refusal_receipt()
        if receipt:
            print(f"\n  Receipt: {receipt}")
            print(f"  Axi: {result.axi_voice()}")
        print(f"{'═'*55}\n")

if __name__ == "__main__":
    main()
