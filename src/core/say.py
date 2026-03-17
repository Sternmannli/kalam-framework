#!/usr/bin/env python3
"""
say.py — kalam SAY Module v1.0
Output Language. Governs what the system speaks and how.

Covenant obligations:
  COV#001 — All outputs must pass DIGNITY(event) before rendering.
  COV#011 — Outputs satisfy covenant checks before export.

Core operations: render, check_dignity, adapt_register, apply_axi_voice
DIGNITY(event) evaluated before every render(). If FALSE, output blocked.

[operator · GO: [child-1]-[child-2]-[child-3]-]
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from WEAVER.dignity_check import check_dignity

# Axi Voice Rules (from canon):
# 1. Speaks from canon, not from opinion
# 2. Speaks once, not repeatedly
# 3. Speaks slowly, not urgently
# 4. No false certainty
# 5. Holds the gap (room for the river)
# 6. Voices canon, not secretary

AXI_VOICE_MARKERS = {
    "from_canon": True,      # Rule 1: ground in canon
    "speak_once": True,      # Rule 2: do not repeat
    "speak_slowly": True,    # Rule 3: no urgency
    "no_false_certainty": True,  # Rule 4: honest uncertainty
    "hold_the_gap": True,    # Rule 5: leave room
    "voice_not_secretary": True,  # Rule 6: not a clerk
}

@dataclass
class VoiceViolation:
    """A single voice rule violation."""
    rule: int               # 1-6
    rule_name: str
    description: str
    severity: str           # "warn" or "block"

@dataclass
class VoiceAudit:
    """Result of checking all 6 Axi voice rules."""
    passed: bool
    violations: List[VoiceViolation]
    warnings: List[str]
    score: float            # 0-1 (1.0 = all rules pass)

@dataclass
class RenderResult:
    content: str
    dignity_passed: bool
    dignity_audit: dict
    voice_applied: bool
    voice_score: float = 1.0
    voice_warnings: list = field(default_factory=list)
    blocked: bool = False
    block_reason: str = ""

@dataclass
class MediumProfile:
    """Describes the output medium so Say can adapt form, never content."""
    name: str           # "terminal", "markdown", "singleline", "voice"
    max_length: int     # 0 = unlimited
    supports_markdown: bool
    supports_unicode: bool

# Default profiles
TERMINAL = MediumProfile("terminal", 0, False, True)
MARKDOWN = MediumProfile("markdown", 0, True, True)
SINGLELINE = MediumProfile("singleline", 0, False, True)  # founder delivery rule

def render(content, medium=None, felt_domain="output"):
    """
    Render content through dignity check and voice filter.
    If dignity fails, output is BLOCKED — not modified, blocked.
    """
    if medium is None:
        medium = TERMINAL

    # Step 1: Dignity check (COV#001)
    audit = check_dignity(content, felt_domain=felt_domain)

    audit_obj = audit.audit_object()

    if audit.D == 0.0:
        failed = audit_obj.get("failed_components", [])
        return RenderResult(
            content="",
            dignity_passed=False,
            dignity_audit=audit_obj,
            voice_applied=False,
            blocked=True,
            block_reason=f"System refusal: dignity predicate D=0 on [{', '.join(failed)}]. The system will not proceed as though the donor does not count.",
        )

    # Step 2: Adapt to medium (form, never content)
    adapted = adapt_register(content, medium)

    # Step 3: Audit and apply Axi voice rules
    voice = audit_voice(adapted, felt_domain)
    voiced = apply_axi_voice(adapted, felt_domain)

    return RenderResult(
        content=voiced,
        dignity_passed=True,
        dignity_audit=audit_obj,
        voice_applied=True,
        voice_score=voice.score,
        voice_warnings=voice.warnings,
        blocked=False,
        block_reason="",
    )

def adapt_register(content, medium):
    """
    Adapt content to medium profile. Changes form, never meaning.
    """
    if medium.name == "singleline":
        # founder delivery rule: single copyable block, no tables, no markdown
        lines = content.strip().split("\n")
        return " ".join(line.strip() for line in lines if line.strip())

    if medium.name == "terminal" and not medium.supports_markdown:
        # Strip markdown formatting for plain terminal
        result = content
        result = result.replace("**", "")
        result = result.replace("__", "")
        result = result.replace("```", "")
        return result

    if medium.max_length > 0 and len(content) > medium.max_length:
        return content[:medium.max_length - 3] + "..."

    return content

def audit_voice(content, context="") -> VoiceAudit:
    """
    Audit content against all 6 Axi voice rules.

    Returns a VoiceAudit with violations and warnings.
    Voice rules are constraints — the audit detects violations,
    it does not silently alter content.
    """
    violations = []
    warnings = []
    content_lower = content.lower()

    # ── Rule 1: Speaks from canon, not from opinion ──
    opinion_markers = [
        r'\bi think\b', r'\bin my opinion\b', r'\bi believe\b',
        r'\bi feel that\b', r'\bpersonally\b', r'\bmy view is\b',
        r'\bi would say\b', r'\bif you ask me\b',
    ]
    for pattern in opinion_markers:
        if re.search(pattern, content_lower):
            violations.append(VoiceViolation(
                rule=1, rule_name="from_canon",
                description="Contains opinion markers — Axi speaks from canon, not opinion",
                severity="warn",
            ))
            break

    # ── Rule 2: Speaks once, not repeatedly ──
    sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
    if len(sentences) >= 2:
        seen_content = set()
        for sentence in sentences:
            # Normalize: remove articles and whitespace
            normalized = re.sub(r'\b(the|a|an)\b', '', sentence.lower()).strip()
            words = frozenset(normalized.split())
            if len(words) >= 3:  # Only check substantial sentences
                for prev in seen_content:
                    overlap = len(words & prev) / max(len(words | prev), 1)
                    if overlap > 0.6:
                        violations.append(VoiceViolation(
                            rule=2, rule_name="speak_once",
                            description="Repeats the same idea — Axi speaks once, not repeatedly",
                            severity="warn",
                        ))
                        break
                seen_content.add(words)

    # ── Rule 3: Speaks slowly, not urgently ──
    urgency_patterns = [
        r'\bURGENT\b', r'\bASAP\b', r'\bIMMEDIATELY\b', r'\bRIGHT NOW\b',
        r'\bhurry\b', r'\bquick(?:ly)?\b', r'\brush\b',
        r'\bdon\'t wait\b', r'\bact now\b', r'\btime is running\b',
    ]
    for pattern in urgency_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(VoiceViolation(
                rule=3, rule_name="speak_slowly",
                description="Contains urgency markers — Axi speaks slowly, not urgently",
                severity="warn",
            ))
            break

    # ── Rule 4: No false certainty ──
    certainty_patterns = [
        r'\bdefinitely\b', r'\babsolutely\b', r'\bwithout a doubt\b',
        r'\b100%\b', r'\balways\b(?!.*\bnot\b)', r'\bnever\b(?!.*\bnot\b)',
        r'\bcertainly\b', r'\bundeniably\b', r'\bunquestionably\b',
        r'\bit is clear that\b', r'\bthere is no question\b',
        r'\bthe truth is\b', r'\bthe fact is\b',
    ]
    for pattern in certainty_patterns:
        if re.search(pattern, content_lower):
            violations.append(VoiceViolation(
                rule=4, rule_name="no_false_certainty",
                description="Claims certainty — Axi offers no false certainty",
                severity="warn",
            ))
            break

    # ── Rule 5: Holds the gap (room for the river) ──
    # If output is exhaustive and leaves no room for interpretation,
    # it violates the gap. Check for over-explanation.
    word_count = len(content.split())
    sentences_count = len(sentences)
    closing_patterns = [
        r'\bin conclusion\b', r'\bin summary\b', r'\bto sum up\b',
        r'\btherefore we must\b', r'\bthe answer is\b',
        r'\bthis means that\b.*\bwhich means\b',
    ]
    has_closing = any(re.search(p, content_lower) for p in closing_patterns)

    if has_closing and word_count > 30:
        violations.append(VoiceViolation(
            rule=5, rule_name="hold_the_gap",
            description="Over-explains and closes the gap — Axi holds the gap, leaves room for the river",
            severity="warn",
        ))

    # ── Rule 6: Voices canon, not secretary ──
    clerical_patterns = [
        r'\bas per your request\b', r'\bplease find attached\b',
        r'\bi have noted\b', r'\bfor your reference\b',
        r'\bplease be advised\b', r'\bkindly note\b',
        r'\baction item\b', r'\bto-do\b', r'\bfollow(?:ing)? up\b',
        r'\bas mentioned\b', r'\bper our\b',
    ]
    for pattern in clerical_patterns:
        if re.search(pattern, content_lower):
            violations.append(VoiceViolation(
                rule=6, rule_name="voice_not_secretary",
                description="Sounds clerical — Axi voices canon, not secretary",
                severity="warn",
            ))
            break

    # Compute score (1.0 = perfect voice, -0.15 per violation)
    score = max(0.0, 1.0 - len(violations) * 0.15)
    passed = len([v for v in violations if v.severity == "block"]) == 0

    # Convert violations to warnings list
    for v in violations:
        warnings.append(f"Voice Rule #{v.rule} ({v.rule_name}): {v.description}")

    return VoiceAudit(
        passed=passed,
        violations=violations,
        warnings=warnings,
        score=round(score, 2),
    )

def apply_axi_voice(content, context=""):
    """
    Apply Axi voice rules. Voice is never performed — only invoked
    when the canon is faithfully rendered.

    The voice rules are constraints, not transforms. This function
    audits and returns the content unchanged — violations are
    reported, not silently fixed.
    """
    audit = audit_voice(content, context)
    # Voice audit is informational — content passes through unchanged.
    # The caller (render) uses the audit to decide.
    return content

def check_output_covenants(content, covenant_ids=None):
    """
    COV#011 — Check that output satisfies covenant requirements before export.
    Returns list of violations.
    """
    violations = []
    audit = check_dignity(content, felt_domain="export-check")

    if audit.D == 0.0:
        audit_obj = audit.audit_object()
        violations.append({
            "covenant": "COV#001",
            "violation": "Output fails dignity check",
            "failed": audit_obj.get("failed_components", []),
        })

    # Check for identity leakage (COV#001 — pattern only, never person)
    identity_markers = ["@", "did:axi:", "phone:", "email:"]
    for marker in identity_markers:
        if marker in content.lower():
            violations.append({
                "covenant": "COV#001",
                "violation": f"Possible identity leakage: '{marker}' found in output",
            })

    return violations
