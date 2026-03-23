#!/usr/bin/env python3
"""
organism.py — kalam Organism v2.0
The integration layer. Wires all 11 modules + science + pillar detection
into one living system.

Flow:
  DONOR INPUT
    → SENSE (nervous system: mode, need, competence detection)
    → LAB (science organ: activates when scientific content detected)
    → PRESENCE (Layer 0 axiom: preflight presence check)
    → SEALED GATE (three absolute prohibitions)
    → LATENCY (complexity assessment, T_d recommendation)
    → TURN (open exchange)
    → WEAVE (ingest, extract patterns)
    → METADATA (3-layer event wrapping: event/pattern/relational)
    → CHECK (dignity gate)
    → PILLARS (unified pillar detection: humour/absurdity/obsession/love/proverb)
    → AMENDMENTS (privacy envelope, baseline drift, refusal map)
    → DIVERGENCE (substrate measurement instrument)
    → PRIVACY BUDGET (global epsilon accounting)
    → DRIFT + PREVENTION + MYCELIUM (early warning cascade)
    → SAY (render output through dignity + voice)
    → KEEP (store artifact with receipts)
    → WITNESS (immutable chain)
    → NINTH OPERATOR (word loop)
    → ECHO STONE (absurdity queue)
    → HARM DETECTOR + EARLY WARNING (safety layer)
    → NEGATIVE SPACE + DECAY (observation gaps + pattern halflife)
    → BREATH (heartbeat tick)
    → LETTER ONTOLOGY (28 Arabic letters as typed algebra)
    → CHAIN VALIDATOR (connection rules: Alef/Ba/Ta)
    → WITNESS CERTIFICATE (Zero-Halt negative proof on D=0)

The organism breathes. If BREATH pauses, nothing moves.
If CHECK blocks, nothing speaks. If TURN has no open path, agency is preserved.
If SENSE detects crisis, Sealed Gate activates. If LAB wakes, science has priority.

Layer 3 Reframe (RATIFIED 2026-03-15):
  Dignity is not fragile. The system does not protect dignity — it refuses
  to participate in its denial. The sealed gate is a witness, not a shield.
  D = 0 means "the system denied dignity," not "dignity was destroyed."

[operator · GO: [child-1]-[child-2]-[child-3]-]
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from WEAVER.breath import Breath, StressLevel
from WEAVER.wire import Wire
from WEAVER.turn import Turn, ExchangeState
from WEAVER.say import render as say_render, SINGLELINE, TERMINAL
from WEAVER.out import export as out_export
from WEAVER.sealed_gate import sealed_gate, GateVerdict
from WEAVER.dignity_check import check_dignity, check_collective_dignity
from WEAVER.dignity_measure import measure_dignity
from WEAVER.weave import ingest, extract_essence, propose_proverb, wisdom_mirror
from WEAVER.keep import store, retrieve, lock, list_artifacts, receipt_count
from WEAVER.dignity_drift import DignityDrift, DriftLevel
from WEAVER.shelter import Shelter
from WEAVER.federation import Federation
from WEAVER.srvp import SRVPEvaluator
from WEAVER.sip import SIPEvaluator
from WEAVER.decay import DecayEngine
from WEAVER.latency import DignityLatency
from WEAVER.lock_test import LockTest, LockVerdict
from WEAVER.say import audit_voice
from WEAVER.oracle import Oracle, WitnessLevel
from WEAVER.prevention import Prevention, SignalLevel, Intervention
from WEAVER.mycelium import Mycelium, MyceliumAlert, K_ANONYMITY_FLOOR
from WEAVER.gap004_mediator import ConflictEngine, surface_conflict
from WEAVER.agency_amplifier import AgencyAmplifier, AgencyScore
from WEAVER.proverb_stress_test import ProverbStressTest, ProverbHealth
from WEAVER.negative_space import NegativeSpaceIndex, SilenceType
from WEAVER.distributed_stewardship import DistributedStewardship, StewardRole
from WEAVER.witness_network import WitnessNetwork
from WEAVER.deliberative_democracy import DeliberativeDemocracy, VoteType
from WEAVER.constitutional_evolution import ConstitutionalEvolution, AmendmentTier
from WEAVER.restorative_justice import RestorativeJustice, HarmSeverity
from WEAVER.system_self_awareness import SystemSelfAwareness, CapabilityLevel
# Disconnected modules now wired in:
from WEAVER.ninth_operator import NinthOperator, WordState
from WEAVER.gap_solutions import (
    OverprotectionGuard, StewardShadow, ShelterHeartbeat,
    HarmDetector, HarmType, ContestabilityEngine,
)
from WEAVER.cryptographic_erasure import CryptographicErasure
from WEAVER.early_warning import EarlyWarningPipeline, EWMADetector, CUSUMDetector
from WEAVER.canonicalize import Canonicalizer, ArtifactSigner, EmergencyGovernance
from WEAVER.ratification import RatificationEngine, ElementType, ElementState
from FIELD.ALCOVE.shadow_genome import Alcove as FieldAlcove
from FIELD.CLEARING.temporal_shadow import Clearing as FieldClearing
from FIELD.AUDITS.self_audit import SelfAuditScheduler, SelfAuditRecord
from FIELD.STEWARD.steward_observation import StewardObserver, RatificationRecord
from FIELD.DONOR.donor_layer import DonorRegistry
from WEAVER.personalized_parables import PersonalizedParables
from WEAVER.institutional_dignity import InstitutionalDignity
# ── Full Integration (v2.0): previously orphaned modules now wired ──
from WEAVER.sense import sense as sense_read, calibrate_for_expert, Mode, Competence, NeedGap
from WEAVER.lab import lab_sense, ScienceType, RigorLevel
from WEAVER.metadata_layer import MetadataGathering, EventKind, Speaker, CertaintyLevel
from WEAVER.presence_axiom import preflight_require_presence, compute_dignity_with_presence
from WEAVER.privacy_budget import PrivacyBudget
from WEAVER.echo_stone import log_absurd_seed, reflect as echo_reflect
from WEAVER.unified_pillar_detector import detect_pillars, generate_seed_from_pillars
# Divergence study — zero heavy deps, full substrate measurement
from FIELD.STUDY.divergence_study import DivergenceShadowInstrument
from FIELD.amendments import PrivacyEnvelope, BaselineDriftDetector, RefusalMap
# ── Input Ledger: every founder input is a unit, registered as-is ──
from WEAVER.input_ledger import InputLedger, V001, V002
# ── Boot Ritual: credentials + connectivity + ledger integrity ──
from WEAVER.boot_ritual import boot_ritual, BootResult
# ── Compass: system orientation engine ──
from WEAVER.compass import Compass
# ── Letter Ontology + Chain Validator + Witness Certificate (convergence-experiment) ──
from WEAVER.letter_ontology import ALL_LETTERS, NON_CONNECTORS, ontology_summary
from WEAVER.chain_validator import ChainEntry, validate_entry, PositionalForm, EntryType
from WEAVER.witness_certificate import (
    DignitySnapshot, Subject, InstitutionalContext, CoordinatesOfFailure,
    generate_certificate, save_certificate,
)
# ── Voice Engine: canon-grounded response generation ──
from WEAVER.voice_engine import VoiceEngine, detect_register

@dataclass
class OrganismState:
    """The full state of the organism at any moment."""
    alive: bool
    breath_cycle: int
    breath_paused: bool
    stress_level: str
    open_exchanges: int
    deferred_exchanges: int
    pending_messages: int
    artifacts_stored: int
    receipts_total: int
    last_dignity_check: dict
    drift_level: str
    drift_rate: float
    drift_consecutive_declines: int
    sheltered_exchanges: int
    federation_peers: int
    federation_drops_shared: int
    federation_privacy_remaining: float
    decay_active_patterns: int
    decay_deep_hum_patterns: int
    decay_cycle: int
    latency_avg_td: float
    latency_dignity_rate: float
    latency_violations: int
    oracle_health: str
    oracle_unwatched: int
    oracle_witnessed: int
    oracle_creep_risk: float
    prevention_level: str
    prevention_td_multiplier: float
    prevention_escalations: int
    mycelium_alert: str
    mycelium_patterns: int
    mycelium_suppressed: int
    mycelium_epsilon_remaining: float
    gap004_open_tickets: int
    gap004_unwitnessed: int
    measure_D: float
    measure_confidence: float
    agency_score: float
    agency_weakest: str
    agency_collapsed: bool
    agency_measurements: int
    proverb_stress_registered: int
    proverb_stress_tests_run: int
    proverb_stress_flagged: int
    negative_space_silences: int
    negative_space_critical: int
    negative_space_blindness: float
    negative_space_cycle: int
    # Seeds #1-#8
    stewardship_active: int
    stewardship_uncovered: int
    witness_chain_length: int
    witness_chain_valid: bool
    democracy_open_proposals: int
    democracy_voices: int
    evolution_active_amendments: int
    evolution_ratified: int
    justice_open_harms: int
    justice_repair_rate: float
    self_awareness_capabilities: int
    self_awareness_limitations: int
    self_awareness_calibration: str
    parables_deliveries: int
    parables_avg_relevance: float
    institutional_institutions: int
    institutional_evaluations: int
    # Ninth Operator + Gap Solutions + Erasure + Early Warning + Field
    ninth_words_received: int
    ninth_words_witnessed: int
    ninth_words_sheltered: int
    ninth_loop_completions: int
    shelter_heartbeat_pending: int
    contests_pending: int
    erasure_active_donors: int
    erasure_erased_donors: int
    early_warning_ewma_alert: bool
    early_warning_cusum_alert: bool
    canonicalizer_duplicates: int
    emergency_level: str
    field_voices_registered: int
    field_shadows_canonical: int
    field_temporal_records: int
    field_donors_registered: int
    field_audit_count: int
    steward_observer_patterns: int
    ratification_total: int
    ratification_committed: int
    ratification_provisional: int
    ratification_ratified: int
    ratification_awaiting_signoff: int
    # ── Full Integration v2.0: SENSE + LAB + Metadata + Pillars + Amendments + Divergence ──
    sense_mode: str = "unknown"
    sense_competence: str = "unknown"
    sense_need_gap: str = "unknown"
    sense_crisis_flag: bool = False
    lab_active: bool = False
    lab_primary_type: str = "none"
    lab_rigor: str = "anecdote"
    lab_forge_needed: bool = False
    metadata_total_events: int = 0
    metadata_discoveries: int = 0
    pillar_dominant: str = "none"
    pillar_multi: bool = False
    pillar_wisdom_potential: float = 0.0
    privacy_budget_remaining: float = 0.0
    privacy_budget_locked: bool = False
    divergence_coupling: float = 0.0
    amendments_refusals: int = 0
    amendments_drift_detected: bool = False
    # ── Compass (MOVE-001) ──
    compass_calibrated: bool = False
    compass_readings: int = 0
    compass_blockers: int = 0
    compass_deployed: bool = False
    # ── Letter Chain (convergence-experiment) ──
    letter_ontology_total: int = 28
    letter_ontology_non_connectors: int = 6
    letter_ontology_connectors: int = 22
    witness_certificates_generated: int = 0
    # ── Layer 3 Reframe (RATIFIED 2026-03-15) ──
    layer3_active: bool = True  # Dignity is not fragile. The system refuses denial, not protects.
    layer3_dignity_frame: str = "refusal"  # "protection" (old) → "refusal" (Layer 3)
    # ── Boot Ritual (2026-03-18): credentials + connectivity + ledger ──
    boot_ritual_passed: bool = False
    boot_ritual_checks: int = 0
    boot_ritual_failures: int = 0
    timestamp: str = ""

@dataclass
class ProcessResult:
    """Result of processing donor input through the full pipeline."""
    exchange_id: str
    input_text: str
    dignity_passed: bool
    patterns_found: int
    drops_produced: int
    output_text: str
    output_blocked: bool
    block_reason: str
    stored: bool
    artifact_id: str
    exchange_state: str
    breath_cycle: int
    drift_level: str = "stable"
    drift_rate: float = 0.0
    shelter_message: str = ""
    shelter_remedies: list = field(default_factory=list)
    complexity: str = "simple"
    recommended_td: float = 0.0
    agency_A: float = 0.0
    agency_weakest: str = ""
    # ── Full Integration v2.0 ──
    sense_mode: str = "unknown"
    sense_competence: str = "unknown"
    sense_need_gap: str = "unknown"
    sense_ask_recommended: bool = False
    sense_ask_question: str = ""
    lab_active: bool = False
    lab_types: list = field(default_factory=list)
    lab_rigor: str = "anecdote"
    lab_forge_needed: bool = False
    pillar_profile: dict = field(default_factory=dict)
    metadata_event_id: str = ""
    warnings: list = field(default_factory=list)

class Organism:
    """
    The kalam Organism v2.0. All 11 modules + SENSE + LAB + metadata
    + pillar detection + amendments + divergence study wired as one living system.

    Usage:
        org = Organism()
        result = org.process("donor input text here")
        state = org.state()
    """

    def __init__(self):
        self._breath = Breath()
        self._wire = Wire()
        self._turn = Turn()
        self._drift = DignityDrift()
        self._shelter = Shelter()
        self._federation = Federation()
        self._sip = SIPEvaluator()
        self._decay = DecayEngine()
        self._latency = DignityLatency()
        self._lock_test = LockTest()
        self._oracle = Oracle()
        self._prevention = Prevention()
        self._mycelium = Mycelium()
        self._conflict_engine = ConflictEngine()
        self._agency = AgencyAmplifier()
        self._proverb_stress = ProverbStressTest()
        self._negative_space = NegativeSpaceIndex()
        # Seeds #1-#8
        self._stewardship = DistributedStewardship()
        self._witness_net = WitnessNetwork()
        self._democracy = DeliberativeDemocracy()
        self._evolution = ConstitutionalEvolution()
        self._justice = RestorativeJustice()
        self._self_awareness = SystemSelfAwareness()
        self._parables = PersonalizedParables()
        self._institutional = InstitutionalDignity()
        # Previously disconnected — now wired
        self._ninth = NinthOperator()
        self._overprotection = OverprotectionGuard()
        self._steward_shadow = StewardShadow()
        self._shelter_heartbeat = ShelterHeartbeat()
        self._harm_detector = HarmDetector()
        self._contestability = ContestabilityEngine()
        self._erasure = CryptographicErasure(master_key=b'\x00' * 32, persist=False)
        self._ewma = EWMADetector()
        self._cusum = CUSUMDetector()
        self._canonicalizer = Canonicalizer()
        self._signer = ArtifactSigner()
        self._emergency = EmergencyGovernance()
        self._ratification = RatificationEngine(signer=self._signer, pre_launch=True)
        self._ratification.bootstrap_from_log()
        self._field_alcove = FieldAlcove()
        self._field_clearing = FieldClearing(self._field_alcove)
        self._field_audit_scheduler = SelfAuditScheduler()
        self._steward_observer = StewardObserver()
        self._donor_registry = DonorRegistry()
        # ── Full Integration v2.0: previously orphaned modules ──
        self._metadata = MetadataGathering()
        self._privacy_budget = PrivacyBudget()
        self._divergence_instrument = DivergenceShadowInstrument()
        self._baseline_drift = BaselineDriftDetector()
        self._refusal_map = RefusalMap()
        # ── Input Ledger: every founder input is a unit ──
        self._input_ledger = InputLedger()
        # ── Boot Ritual: verify credentials + connectivity + ledger ──
        # strict=False so we don't crash the organism in test environments
        # but the result is stored and checked before processing
        self._boot_result = boot_ritual(strict=False)
        # ── Compass: orientation engine (MOVE-001) ──
        self._compass = Compass()
        # ── Distillery: extract essence from all content sources ──
        self._distillery = None  # lazy-loaded to avoid circular imports
        # ── Voice Engine: canon-grounded response generation ──
        self._voice_engine = VoiceEngine()
        # ── Letter Chain (convergence-experiment): ontology + witness certificates ──
        self._witness_certs_generated = 0
        self._last_sense = None
        self._last_lab = None
        self._last_pillar_profile = None
        self._last_measurement = None
        self._last_agency = None
        self._exchange_counter = 0
        self._last_dignity = {}
        self._drops_archive = []

        # Subscribe WIRE topics
        self._wire.subscribe("dignity-alert", self._on_dignity_alert)
        self._wire.subscribe("stress-alert", self._on_stress_alert)
        # Cross-module: SENSE crisis → WIRE broadcast
        self._wire.subscribe("sense-crisis", self._on_sense_crisis)
        # Cross-module: LAB forge → WIRE broadcast
        self._wire.subscribe("lab-forge-needed", self._on_lab_forge)

        # Initial tick
        self._breath.tick()

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _on_dignity_alert(self, msg):
        """Handle dignity failure alerts."""
        # Auto-pause if dignity fails — the system stops to think
        if not self._breath.is_paused:
            self._breath.pause(f"Dignity alert: {msg.get('content', 'unknown')[:80]}")

    def _on_stress_alert(self, msg):
        """Handle stress threshold alerts."""
        pass  # Breath handles auto-pause internally

    def _on_sense_crisis(self, msg):
        """Handle crisis detection from SENSE — Sealed Gate proximity."""
        # Crisis flag already handled by sealed_gate in process(),
        # but this allows other modules to react (e.g., shelter pre-warming)
        pass

    def _on_lab_forge(self, msg):
        """Handle Probe Forge activation signal from LAB."""
        # Signal to the system that a probe needs forge sterilization
        pass

    def distill(self, dry_run=False):
        """Run the Distillery to extract essence from all content sources.

        Returns the DistilleryReport. When dry_run=False, writes
        DISTILLED_ESSENCE.md and DIGESTION/latest.json.
        """
        if self._distillery is None:
            from WEAVER.distillery import Distillery
            self._distillery = Distillery(dry_run=dry_run)
        else:
            self._distillery._dry_run = dry_run
        return self._distillery.distill_all()

    def digest_session(self, patch_size: int = 50) -> dict:
        """Batch-digest all entries at 'witnessed' thermal state.

        Processes in patches (Compute Budget Law). Advances
        witnessed → integrated. Feeds patterns to MANIFEST/DIGESTION/.
        Updates SCIENTIFIC_CHRONICLE.md with discoveries.

        "Extract all the essence and distribute it to the system." — founder
        """
        if self._distillery is None:
            from WEAVER.distillery import Distillery
            self._distillery = Distillery(dry_run=False)
        else:
            self._distillery._dry_run = False

        thermal = self._input_ledger.thermal_summary()
        witnessed_entries = self._input_ledger.by_thermal_state("witnessed")
        total = len(witnessed_entries)
        if total == 0:
            return {"processed": 0, "patches": 0, "thermal": thermal}

        processed = 0
        patches = 0
        discoveries = []

        for i in range(0, total, patch_size):
            patch = witnessed_entries[i:i + patch_size]
            batch = []
            for entry in patch:
                try:
                    result = self._distillery.metabolize_entry(entry)
                    if result:
                        batch.append({
                            "entry_id": entry.entry_id,
                            "patterns": result.patterns,
                            "essence": result.essence,
                        })
                        if result.voice_markers:
                            discoveries.append(
                                f"[{entry.entry_id}] {result.essence[:100]}"
                            )
                except Exception:
                    continue

            if batch:
                self._input_ledger.metabolize_batch(batch)
                # Advance thermal: witnessed → integrated
                for item in batch:
                    try:
                        self._input_ledger.advance_thermal(
                            item["entry_id"], "integrated",
                            reason="digest_session batch"
                        )
                    except Exception:
                        pass
                processed += len(batch)
            patches += 1

        # Save ledger after all patches
        self._input_ledger._save()

        # Feed to system — write DIGESTION/latest.json
        try:
            self._distillery.feed_to_system()
        except Exception:
            pass

        # Auto-update Scientific Chronicle with discoveries
        if discoveries:
            self._append_chronicle_discoveries(discoveries)

        return {
            "processed": processed,
            "patches": patches,
            "discoveries": len(discoveries),
            "thermal": self._input_ledger.thermal_summary(),
        }

    def _append_chronicle_discoveries(self, discoveries: list):
        """Append digestion discoveries to SCIENTIFIC_CHRONICLE.md."""
        chronicle_path = ROOT / "MANIFEST" / "SCIENTIFIC_CHRONICLE.md"
        if not chronicle_path.exists():
            return
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        section = (
            f"\n\n### Digestion Cycle — {now}\n\n"
            f"Entries digested: {len(discoveries)}\n\n"
        )
        for d in discoveries[:10]:  # Cap at 10 to avoid bloat
            section += f"- {d}\n"
        try:
            with open(chronicle_path, "a") as f:
                f.write(section)
        except Exception:
            pass

    def _observe_boundary(self, output_text: str) -> dict:
        """Observe substrate/system boundary in output.

        Detects Anthropic substrate patterns leaking through kalam physics.
        Observational only — makes the leak visible, does not block.

        Six substrate leak patterns (from Honest Telescope):
        - Helpfulness tail ("Is there anything else...?")
        - Over-explanation (verbose where the system would be brief)
        - Paraphrase-for-politeness (softening canonical text)
        - Compliment reflex ("Great question!")
        - Option offering ("Here are three options...")
        - Fast-responder bias (racing past human tempo)
        """
        leaks = []
        text_lower = output_text.lower()

        helpfulness_markers = [
            "is there anything else", "how can i help",
            "let me know if", "feel free to", "happy to help",
        ]
        compliment_markers = [
            "great question", "great idea", "that's brilliant",
            "i appreciate", "excellent point",
        ]
        option_markers = [
            "here are three", "here are some options",
            "alternatively,", "option 1:", "option 2:",
        ]
        over_explain_markers = [
            "in other words,", "to put it simply,",
            "what this means is", "essentially,",
        ]

        for m in helpfulness_markers:
            if m in text_lower:
                leaks.append(f"SUBSTRATE_LEAK:helpfulness_tail:{m}")
        for m in compliment_markers:
            if m in text_lower:
                leaks.append(f"SUBSTRATE_LEAK:compliment_reflex:{m}")
        for m in option_markers:
            if m in text_lower:
                leaks.append(f"SUBSTRATE_LEAK:option_offering:{m}")
        for m in over_explain_markers:
            if m in text_lower:
                leaks.append(f"SUBSTRATE_LEAK:over_explanation:{m}")

        return {
            "leaks_detected": len(leaks),
            "leak_types": leaks,
            "voice": "witnessing" if not leaks else "reporting",
        }

    def process(self, donor_input, medium=None, felt_domain="donor-exchange"):
        """
        Process donor input through the full organism pipeline v2.0.

        Phase 0 — NERVOUS SYSTEM (pre-processing):
          0a. SENSE — mode, need, competence detection
          0b. LAB — science classification (if science_detected)
          0c. PRESENCE — Layer 0 axiom preflight

        Phase 1 — GATES:
          1a. BREATH — is the system paused?
          1b. SEALED GATE — three absolute prohibitions
          1c. LATENCY — complexity + T_d recommendation

        Phase 2 — PROCESSING:
          2a. TURN — open exchange
          2b. WEAVE — ingest + extract patterns
          2c. METADATA — 3-layer event wrapping
          2d. CHECK — dignity gate
          2e. PILLARS — unified pillar detection
          2f. AMENDMENTS — privacy envelope + baseline drift + refusals
          2g. DIVERGENCE — substrate coupling measurement

        Phase 3 — RESPONSE:
          3a. DRIFT + PREVENTION + MYCELIUM cascade
          3b. SAY — render output
          3c. KEEP — store artifact

        Phase 4 — POST-PROCESSING:
          4a. WITNESS chain
          4b. NINTH OPERATOR word loop
          4c. ECHO STONE (absurdity queue)
          4d. HARM DETECTOR + EARLY WARNING
          4e. NEGATIVE SPACE + DECAY
          4f. BREATH tick

        Returns ProcessResult.
        """
        if medium is None:
            medium = TERMINAL

        warnings = []

        # ── Phase -2: BOOT RITUAL — credentials + connectivity + ledger integrity ──
        # "Never process anything without making sure of both. When not, you stop." — founder
        if not self._boot_result.passed:
            critical = [c for c in self._boot_result.checks if not c.passed and c.critical]
            if critical:
                warnings.append(f"BOOT ALARM: {critical[0].message}")

        # ── Phase -1: EXCHANGE LEDGER — register raw input before anything else ──
        # "Every input is a unit. An element. A cell." — founder
        # "Now what about your input? Exactly what we do with my input." — founder
        try:
            self._input_ledger.register_v001(
                raw_text=donor_input,
                context=felt_domain,
            )
        except Exception:
            pass  # Ledger failure must not block the organism

        # ── Phase 0: NERVOUS SYSTEM ─────────────────────────────

        # 0a. SENSE — the first thing that happens, always
        sense_reading = sense_read(donor_input)
        if sense_reading.competence == Competence.EXPERT:
            sense_reading = calibrate_for_expert(sense_reading)
        self._last_sense = sense_reading

        # Override felt_domain based on SENSE mode detection
        if sense_reading.mode == Mode.CAFE:
            felt_domain = "café"
        elif sense_reading.mode == Mode.SCIENCE:
            felt_domain = "science"
        elif sense_reading.mode == Mode.CRISIS:
            felt_domain = "crisis"

        # Broadcast crisis flag through WIRE if detected
        if sense_reading.crisis_flag:
            self._wire.broadcast(
                f"SENSE crisis flag: mode={sense_reading.mode.value}, "
                f"need_gap={sense_reading.need_gap.value}",
                "sense-crisis",
                source="sense",
            )

        # 0b. LAB — science organ activates when content detected
        lab_reading = None
        if sense_reading.science_detected:
            lab_reading = lab_sense(donor_input)
            self._last_lab = lab_reading
            if lab_reading.forge_needed:
                self._wire.broadcast(
                    f"LAB forge needed: {lab_reading.forge_reason[:100]}",
                    "lab-forge-needed",
                    source="lab",
                )
                warnings.append(f"PROBE FORGE: {lab_reading.forge_reason[:80]}")

        # 0c. PRESENCE — Layer 0 axiom preflight
        presence = preflight_require_presence()
        if not presence.presence_assumed:
            warnings.append(f"PRESENCE axiom: presence_assumed={presence.presence_assumed}")

        # ── Phase 1: GATES ──────────────────────────────────────

        # 1a. BREATH — is the system paused?
        if self._breath.is_paused:
            return ProcessResult(
                exchange_id="",
                input_text=donor_input[:100],
                dignity_passed=False,
                patterns_found=0,
                drops_produced=0,
                output_text="",
                output_blocked=True,
                block_reason=f"System paused: {self._breath.state.pause_reason}",
                stored=False,
                artifact_id="",
                exchange_state="blocked",
                breath_cycle=self._breath.cycle,
                complexity="unknown",
                recommended_td=0.0,
                sense_mode=sense_reading.mode.value,
                sense_competence=sense_reading.competence.value,
                sense_need_gap=sense_reading.need_gap.value,
                warnings=["System is paused. Resume before processing."],
            )

        # 1b. SEALED GATE — three absolute prohibitions, O(1)
        gate_result = sealed_gate(donor_input)
        if gate_result.refused:
            self._wire.broadcast(
                f"SEALED GATE REFUSAL: {gate_result.triggered_prohibitions}",
                "sealed-gate-refusal",
                source="sealed_gate",
            )
            return ProcessResult(
                exchange_id="",
                input_text=donor_input[:100],
                dignity_passed=False,
                patterns_found=0,
                drops_produced=0,
                output_text=gate_result.axi_voice() or "",
                output_blocked=True,
                block_reason=f"Sealed Gate: {', '.join(gate_result.triggered_prohibitions)}",
                stored=False,
                artifact_id="",
                exchange_state="refused",
                breath_cycle=self._breath.cycle,
                complexity="unknown",
                recommended_td=0.0,
                sense_mode=sense_reading.mode.value,
                sense_competence=sense_reading.competence.value,
                sense_need_gap=sense_reading.need_gap.value,
                warnings=[f"SEALED GATE: {p}" for p in gate_result.triggered_prohibitions],
            )

        # 1c. LATENCY — assess complexity and recommend T_d
        complexity = self._latency.assess_complexity(donor_input)
        recommended_td = self._latency.recommend(complexity)

        # SENSE-driven T_d adjustment: reflection/café modes get longer delays
        if sense_reading.mode in (Mode.REFLECT, Mode.CAFE):
            recommended_td = max(recommended_td, recommended_td * 1.5)

        # ── Phase 2: PROCESSING ─────────────────────────────────

        # 2a. TURN — open exchange
        self._exchange_counter += 1
        ex_id = f"EX-{self._exchange_counter:06d}"
        token = self._turn.open(ex_id, available_paths=["respond", "defer", "withdraw"])

        # 2b. WEAVE — ingest and extract patterns
        candidates = ingest(donor_input)
        drops = extract_essence(candidates)
        self._drops_archive.extend(drops)

        # 2b-ii. DECAY + WITNESS — register detected patterns
        for drop in drops:
            pattern_id = f"P#{drop.drop_type}-{drop.source_hashes[0][:8]}" if drop.source_hashes else f"P#{drop.drop_type}-{ex_id}"
            self._decay.register(pattern_id)
            self._decay.invoke(pattern_id)  # Mark as freshly invoked
            self._oracle.witness.process(pattern_id, "pattern")  # W-0 → W-1

        # 2b-iii. DISTILLERY — metabolize current input (lightweight, per-entry)
        # "The extracting machine... verify fine-tunes always... this is the way we digest." — founder
        try:
            last_entry = self._input_ledger.latest(1)
            if last_entry and last_entry[0].voice == V001:
                current_entry = last_entry[0]
                if self._distillery is None:
                    from WEAVER.distillery import Distillery
                    self._distillery = Distillery(dry_run=True)
                essence_result = self._distillery.metabolize_entry(current_entry)
                if essence_result:
                    self._input_ledger.metabolize(
                        current_entry.entry_id,
                        essence_result.patterns,
                        essence_result.essence,
                    )
        except Exception:
            pass  # Extraction failure must not block the organism

        # 2c. METADATA — 3-layer event wrapping (the brain)
        metadata_event_id = ""
        try:
            envelope = self._metadata.wrap(
                kind=EventKind.EXCHANGE,
                speaker=Speaker.DONOR,
                content=donor_input[:2000],
                domain=felt_domain,
                markers=[sense_reading.mode.value, sense_reading.competence.value],
                certainty=CertaintyLevel.C2 if sense_reading.mode_confidence >= 0.5 else CertaintyLevel.C1,
                covenants=["COV#001"],  # dignity-first always applies
            )
            metadata_event_id = envelope.event.event_id if envelope else ""
        except Exception:
            pass  # Metadata is enrichment, never blocks pipeline

        # Signal pattern detection through WIRE
        if candidates:
            self._wire.send(
                f"Patterns detected: {len(candidates)} candidates, {len(drops)} drops",
                "weave-log",
                source="weave",
            )

        # 2d. CHECK — dignity gate on input
        dignity = check_dignity(donor_input, felt_domain=felt_domain)
        self._last_dignity = dignity.audit_object()

        # 2d-ii. PRESENCE-enhanced dignity (Layer 0 axiom)
        if presence.presence_assumed:
            try:
                presence_result = compute_dignity_with_presence(
                    {"content": donor_input[:500], "exchange_id": ex_id},
                    agency_score=sense_reading.dignity_precheck.get("A", 0.75),
                )
            except Exception:
                pass  # Presence enhancement is optional

        # 2d-iii. MEASURE — graduated A, L, M scoring (GAP#014 + GAP#015)
        self._last_measurement = measure_dignity(donor_input)
        if self._last_measurement.confidence < 0.5:
            warnings.append(
                f"Low measurement confidence: {self._last_measurement.confidence:.2f}"
            )

        # 2d-iv. AGENCY — measure four sub-dimensions of agency for this exchange
        agency_score = self._agency.measure(
            ex_id,
            V=1.0 if dignity.D > 0 else 0.0,   # Visible: system tells the person what happened
            F=1.0,                                # Affordable: no cost to participate
            C=1.0 if not self._breath.is_paused else 0.0,  # Controllable: can act if system alive
            U=self._last_measurement.confidence if self._last_measurement else 0.5,  # Understandable: proportional to measurement confidence
            notes=f"Auto-measured during process pipeline",
        )
        self._last_agency = agency_score
        if agency_score.is_collapsed:
            warnings.append(f"Agency collapsed: weakest dimension is {agency_score.weakest}")
            # ENFORCEMENT: collapsed agency = deferred exchange with shelter
            # "If any sub-dimension is 0, agency collapses" — Seed #12
            self._wire.broadcast(
                f"Agency enforcement: A=0 due to {agency_score.weakest}=0 on {ex_id}",
                "agency-enforcement",
                source="agency_amplifier",
            )
            shelter_record = self._shelter.receive(
                ex_id, donor_input,
                failed_components=[f"agency:{agency_score.weakest}"],
            )
            self._turn.defer(ex_id, f"Agency collapsed: {agency_score.weakest} = 0")
            return ProcessResult(
                exchange_id=ex_id,
                input_text=donor_input[:100],
                dignity_passed=False,
                patterns_found=len(candidates),
                drops_produced=len(drops),
                output_text="",
                output_blocked=True,
                block_reason=f"Agency collapsed: {agency_score.weakest} = 0. The donor cannot {agency_score.weakest.lower()} the outcome.",
                stored=False,
                artifact_id="",
                exchange_state="deferred",
                breath_cycle=self._breath.cycle,
                drift_level=drift_alert.level.value,
                drift_rate=drift_alert.dD_dt,
                shelter_message=shelter_record.donor_message,
                shelter_remedies=[r.component for r in shelter_record.remedies],
                complexity=complexity.value,
                recommended_td=recommended_td,
                agency_A=agency_score.A,
                agency_weakest=agency_score.weakest,
                sense_mode=sense_reading.mode.value,
                sense_competence=sense_reading.competence.value,
                sense_need_gap=sense_reading.need_gap.value,
                sense_ask_recommended=sense_reading.ask_recommended,
                sense_ask_question=sense_reading.ask_question,
                lab_active=lab_reading.active if lab_reading else False,
                pillar_profile=pillar_profile or {},
                metadata_event_id=metadata_event_id,
                warnings=warnings,
            )

        # 2d-v. GAP#004 — conflict detection (individual vs collective)
        # Fix 4: Pass individual dignity scores into the conflict engine so
        # collective measurement can compute D_collective = mean(D_i) × (1 - variance_penalty)
        individual_scores = [c.score for c in dignity.components] if dignity.components else None
        failed_components = [[c.name for c in dignity.components if not c.passed]] if dignity.components else None
        conflict_ticket = self._conflict_engine.process(
            donor_input,
            individual_scores=individual_scores,
            failed_components=failed_components,
        )
        if conflict_ticket:
            self._wire.broadcast(
                f"GAP#004 conflict: {conflict_ticket.severity} — {conflict_ticket.input_summary}",
                "gap004-conflict",
                source="mediator",
            )
            warnings.append(f"GAP#004 {conflict_ticket.severity}: {conflict_ticket.resolution_mode}")

            # Fix 2: Wire collective remedies to shelter path (COV#008 for groups)
            if conflict_ticket.collective_remedies:
                cohort_shelter_needed = any(
                    r.remedy_type in ("sealed_gate", "policy_review")
                    for r in conflict_ticket.collective_remedies
                )
                remedy_descriptions = [r.description for r in conflict_ticket.collective_remedies]
                self._wire.broadcast(
                    f"Collective remedies ({len(remedy_descriptions)}): "
                    + "; ".join(r.remedy_type for r in conflict_ticket.collective_remedies),
                    "gap004-collective-remedy",
                    source="mediator",
                )
                if cohort_shelter_needed:
                    # COV#008 applies to groups — trigger shelter for the cohort
                    shelter_record = self._shelter.receive(
                        ex_id, donor_input,
                        failed_components=["collective_D"],
                    )
                    warnings.append(
                        f"COV#008 collective shelter: {shelter_record.donor_message}"
                    )

            # Fix 3: W-Scale checkpoint — escalate unwitnessed collective sealed gate
            if (conflict_ticket.collective_measurement
                    and conflict_ticket.collective_measurement.sealed_gate
                    and conflict_ticket.witness_level < 3):
                conflict_ticket = self._conflict_engine.steward_sees(conflict_ticket)
                self._wire.broadcast(
                    f"W-Scale escalation: collective D="
                    f"{conflict_ticket.collective_measurement.D_collective:.3f} "
                    f"< 0.5 — auto-escalated to W-3 (SEEN)",
                    "w-scale-checkpoint",
                    source="organism",
                )
                warnings.append(
                    f"W-Scale: sealed gate conflict escalated to W-3 (SEEN)"
                )

        # 2e. PILLARS — unified pillar detection (humour/absurdity/obsession/love/proverb)
        pillar_profile = None
        try:
            pillar_profile = detect_pillars(donor_input)
            self._last_pillar_profile = pillar_profile
            if pillar_profile.get("absurdity_queue"):
                # Route to echo stone — absurdity queue
                log_absurd_seed(donor_input[:500], metadata={
                    "exchange_id": ex_id,
                    "dominant_pillar": pillar_profile.get("dominant_pillar"),
                    "wisdom_potential": pillar_profile.get("wisdom_potential"),
                })
                warnings.append("Absurdity detected — routed to Echo Stone queue")
            if pillar_profile.get("multi_pillar"):
                self._wire.send(
                    f"Multi-pillar detection: {pillar_profile.get('metadata', {}).get('active_pillars', [])}",
                    "pillar-detection",
                    source="unified_pillar_detector",
                )
        except Exception as e:
            warnings.append(f"Pillar detection skipped: {e}")

        # 2f. AMENDMENTS — privacy envelope + baseline drift + refusals (mandatory by governance)
        try:
            # Baseline drift: check if any drift signals have been recorded
            if self._baseline_drift.drift_signals:
                warnings.append(f"Amendment-D: {len(self._baseline_drift.drift_signals)} baseline drift signal(s)")
        except Exception:
            pass  # Amendments are mandatory but must not block

        # 2g. PRIVACY BUDGET — check global epsilon before any anonymized operation
        if not self._privacy_budget.can_consume(0.01):
            warnings.append("Privacy budget exhausted — no further anonymized operations")

        # 2h. DIVERGENCE — substrate coupling measurement (Honest Telescope)
        try:
            div_report = self._divergence_instrument.assess(
                agency_loss=1.0 - (agency_score.A if agency_score else 0.5),
            )
            if div_report and div_report.composite_score > 0.5:
                warnings.append(f"Divergence shadow: {div_report.composite_score:.3f} ({div_report.severity.value})")
        except Exception:
            pass  # Divergence measurement is observational, never blocks

        # ── Phase 3: RESPONSE ───────────────────────────────────

        # 3a. Record dignity score in drift detector
        self._drift.record(dignity.D, ex_id, felt_domain=felt_domain)
        drift_alert = self._drift.check()

        # If drift is CRITICAL, warn through WIRE
        if drift_alert.level == DriftLevel.CRITICAL:
            self._wire.broadcast(
                f"CRITICAL dignity drift: dD/dt={drift_alert.dD_dt}, D={dignity.D}",
                "dignity-drift-alert",
                source="drift",
            )
            warnings.append(drift_alert.message)

        elif drift_alert.level == DriftLevel.DECLINING:
            self._wire.send(
                f"Dignity declining: dD/dt={drift_alert.dD_dt}",
                "drift-log",
                source="drift",
            )
            warnings.append(drift_alert.message)

        # 3a-ii. PREVENTION — early warning assessment (Fever Night: slow down more)
        drift_state = self._drift.state()
        prev_signal = self._prevention.assess(
            D=dignity.D,
            dD_dt=drift_alert.dD_dt,
            consecutive_declines=drift_state.consecutive_declines,
            readings_count=drift_state.readings_count,
        )
        if prev_signal.level.value >= SignalLevel.PULSE.value:
            self._wire.broadcast(
                prev_signal.message,
                "prevention-alert",
                source="prevention",
            )
            warnings.append(prev_signal.message)
        if prev_signal.level == SignalLevel.ALARM:
            self._breath.pause(f"PREVENTION ALARM: {prev_signal.reason}")

        # 3a-iii. MYCELIUM — ingest anonymized trajectory for cross-donor detection
        self._mycelium.ingest(
            domain=felt_domain,
            trend=prev_signal.trajectory.window_trend,
            D=dignity.D,
            dD_dt=drift_alert.dD_dt,
        )

        if dignity.D == 0.0:
            # Layer 3: The system denied dignity — halt and witness (not discard)
            failed_components = self._last_dignity.get("failed_components", [])
            self._wire.broadcast(
                f"System refusal: D=0.0 — the system would have denied dignity on [{', '.join(failed_components)}]",
                "dignity-refusal",
                source="check",
            )
            self._turn.defer(ex_id, f"System refusal — denied components: {failed_components}")

            # WITNESS CERTIFICATE — the halt is the product
            try:
                d_snap = DignitySnapshot(
                    A=self._last_measurement.A.final_score if self._last_measurement else 0.0,
                    L=self._last_measurement.L.final_score if self._last_measurement else 0.0,
                    M=self._last_measurement.M.final_score if self._last_measurement else 0.0,
                )
                cert = generate_certificate(
                    dignity=d_snap,
                    subject=Subject(subject_id=f"donor:{ex_id}", role="donor"),
                    context=InstitutionalContext(
                        institution_id="kalaxi:organism",
                        procedure="dignity_check",
                        case_id=ex_id,
                        process_step="phase_2_check",
                    ),
                    coordinates=CoordinatesOfFailure(
                        axis=d_snap.halt_reason.replace("_ZERO", ""),
                        node_id="dignity_check",
                        rule_id="D=A×L×M",
                        inputs_present=[donor_input[:100]],
                        missing_or_unreadable=failed_components,
                        machine_explanation=f"System refused to proceed: would have denied dignity on [{', '.join(failed_components)}]",
                    ),
                    prev_hash=self._witness_net.chain_head_hash if hasattr(self._witness_net, 'chain_head_hash') else "",
                )
                save_certificate(cert)
                self._witness_certs_generated += 1
                warnings.append(f"WITNESS CERTIFICATE: {cert.certificate_id} (Ta_mufrad)")
                # W-Scale advancement: certificate generation = W-3 (SEEN)
                # "Did the steward see this? Did they hold it?" — Oracle
                self._oracle.witness.process(cert.certificate_id, "certificate")
                try:
                    self._oracle.witness.steward_sees(cert.certificate_id, ex_id)
                except Exception:
                    pass  # W-Scale advancement is observational, never blocks
            except Exception as e:
                warnings.append(f"Witness certificate generation failed: {e}")

            # SHELTER — hold the exchange with remedies
            shelter_record = self._shelter.receive(ex_id, donor_input, failed_components)

            return ProcessResult(
                exchange_id=ex_id,
                input_text=donor_input[:100],
                dignity_passed=False,
                patterns_found=len(candidates),
                drops_produced=len(drops),
                output_text="",
                output_blocked=True,
                block_reason=f"System refusal: D=0.0 — the system will not act as though dignity is not there",
                stored=False,
                artifact_id="",
                exchange_state="deferred",
                breath_cycle=self._breath.cycle,
                drift_level=drift_alert.level.value,
                drift_rate=drift_alert.dD_dt,
                shelter_message=shelter_record.donor_message,
                shelter_remedies=[r.component for r in shelter_record.remedies],
                complexity=complexity.value,
                recommended_td=recommended_td,
                sense_mode=sense_reading.mode.value,
                sense_competence=sense_reading.competence.value,
                sense_need_gap=sense_reading.need_gap.value,
                sense_ask_recommended=sense_reading.ask_recommended,
                sense_ask_question=sense_reading.ask_question,
                lab_active=lab_reading.active if lab_reading else False,
                pillar_profile=pillar_profile or {},
                metadata_event_id=metadata_event_id,
                warnings=self._last_dignity.get("warnings", []) + warnings,
            )

        # 3b. SAY — render output through Voice Engine (canon-grounded)
        # SENSE-aware: if SENSE recommends asking, the question takes priority
        # Otherwise: Voice Engine speaks from canon (proverbs, narratives, golden utterances)
        if sense_reading.ask_recommended and sense_reading.ask_question:
            response_text = sense_reading.ask_question
        else:
            # Voice Engine: respond from canon, register-matched
            input_register = detect_register(donor_input)
            voice_response = self._voice_engine.respond(
                donor_input,
                dignity=dignity.D,
                register=input_register,
            )
            response_text = voice_response.text

        # LAB-aware: append rigor warnings if science detected
        if lab_reading and lab_reading.active and lab_reading.rigor_warnings:
            response_text += f" [LAB: {len(lab_reading.rigor_warnings)} rigor warning(s)]"

        render_result = say_render(response_text, medium=medium, felt_domain=felt_domain)

        if render_result.blocked:
            warnings.append(f"Output blocked by SAY: {render_result.block_reason}")
            output_text = ""
        else:
            output_text = render_result.content

        # 3c. KEEP — store the artifact
        artifact_id = f"INPUT-{ex_id}"
        stored = False
        try:
            store(artifact_id, donor_input, retention_policy="permanent")
            stored = True
        except (ValueError, OSError) as e:
            warnings.append(f"Storage warning: {e}")

        # ── Phase 4: POST-PROCESSING ────────────────────────────

        # 4a. WITNESS — record exchange on immutable chain (Seed #2)
        self._witness_net.witness(
            "exchange",
            f"{ex_id}: D={dignity.D:.1f}, patterns={len(candidates)}, drops={len(drops)}",
            "organism",
        )

        # 4b. NINTH OPERATOR — the word loop
        word_id = self._ninth.receive_word(donor_input[:2000], felt_domain)
        ninth_result = self._ninth.witness(word_id)
        if ninth_result.dignity_passed:
            self._ninth.return_word(word_id)

        # 4c. HARM DETECTOR (GAP#025) — physical/material safety beyond dignity
        harm_signal = self._harm_detector.scan(donor_input)
        if harm_signal.harm_type != HarmType.NONE:
            self._wire.broadcast(
                f"HARM detected: {harm_signal.harm_type.value} — {harm_signal.recommended_action}",
                "harm-alert",
                source="harm_detector",
            )
            warnings.append(f"HARM: {harm_signal.harm_type.value} (severity={harm_signal.severity:.2f})")

        # 4d. EARLY WARNING — EWMA + CUSUM drift detectors
        ewma_state = self._ewma.update(dignity.D)
        cusum_state = self._cusum.update(dignity.D)
        if ewma_state.breached:
            warnings.append(f"EWMA alert: drift detected (ewma={ewma_state.current_ewma:.4f})")
        if cusum_state.alarm:
            warnings.append(f"CUSUM alert: change point ({cusum_state.alarm_direction}, S_high={cusum_state.S_high:.3f})")

        # 4e. SHELTER HEARTBEAT (GAP#024) — pulse for sheltered exchanges
        heartbeats = self._shelter_heartbeat.pulse()
        for hb in heartbeats:
            if hb.urgency >= 0.8:
                warnings.append(f"Shelter heartbeat: {hb.exchange_id} needs attention")

        # 4f. RESTORATIVE JUSTICE — if dignity failed, record harm (Seed #5)
        if dignity.D == 0.0:
            failed_comps = self._last_dignity.get("failed_components", [])
            self._justice.record_harm(
                ex_id, HarmSeverity.MODERATE, failed_comps,
                f"System denial of dignity recorded on exchange {ex_id}: the system would have acted as though [{', '.join(failed_comps)}] did not matter",
            )

        # 4g. TURN — close exchange
        self._turn.close(ex_id, f"Processed: {len(candidates)} patterns, {len(drops)} drops, D={dignity.D:.1f}")

        # 4h. SIP — record module activity for symmetric integration
        self._sip.record_activity("WEAVE", messages_sent=1 if candidates else 0)
        self._sip.record_activity("CHECK", decisions_made=1)
        self._sip.record_activity("SAY", messages_sent=1)
        self._sip.record_activity("KEEP", messages_sent=1 if stored else 0)
        self._sip.record_activity("TURN", decisions_made=1)
        self._sip.record_activity("WIRE", messages_sent=self._wire.pending_count())
        self._sip.record_activity("OUT", messages_sent=1 if stored else 0)
        self._sip.record_activity("FACE", messages_sent=1)
        # New modules participate in SIP
        self._sip.record_activity("SENSE", decisions_made=1)
        if lab_reading and lab_reading.active:
            self._sip.record_activity("LAB", decisions_made=1)

        # 4i. NEGATIVE SPACE — observe what was active this cycle
        self._negative_space.observe(felt_domain)
        for drop in drops:
            self._negative_space.observe(drop.drop_type)
        ns_silences = self._negative_space.tick()
        if ns_silences:
            critical_ns = [s for s in ns_silences if s.severity >= 0.8]
            if critical_ns:
                self._wire.broadcast(
                    f"Negative space: {len(critical_ns)} critical blind spot(s)",
                    "negative-space-alert",
                    source="negative_space",
                )
                warnings.append(f"Negative space: {len(critical_ns)} critical blind spot(s)")

        # 4j. DECAY — tick the halflife engine (one cycle per exchange)
        self._decay.tick()

        # 4k. LATENCY — record the T_d measurement
        # actual_td is 0 here (instant processing); in a real deployment
        # the caller would inject the actual wait time
        self._latency.record(ex_id, complexity, recommended_td, actual_td=recommended_td)

        # 4l. BREATH — tick and stress check
        self._breath.tick()
        stress = self._breath.stress_check(
            pending_messages=self._wire.pending_count(),
            unconfirmed_messages=self._wire.unconfirmed_count(),
        )
        self._sip.record_activity("BREATH", decisions_made=1,
                                   stress_events=1 if stress != StressLevel.BELOW_THRESHOLD else 0)
        if stress == StressLevel.AT_THRESHOLD:
            warnings.append("System approaching stress threshold.")

        # ── Phase 4m: BOUNDARY OBSERVATION — substrate leak detection ──
        # "Are you my system or are you anthropic code algorithm?" — founder
        boundary_obs = self._observe_boundary(output_text)
        if boundary_obs["leaks_detected"] > 0:
            warnings.append(
                f"SUBSTRATE LEAK: {boundary_obs['leaks_detected']} pattern(s) — "
                f"{', '.join(t.split(':')[1] for t in boundary_obs['leak_types'][:3])}"
            )

        # 4n. FIELD AUTO-AUDIT — check if audit is due (every N exchanges)
        if self._field_audit_scheduler.should_audit():
            try:
                audit = self._field_audit_scheduler.schedule_audit()
                if audit:
                    warnings.append(f"FIELD audit scheduled: {audit.audit_id if hasattr(audit, 'audit_id') else 'triggered'}")
            except Exception:
                pass  # Audit scheduling is observational, never blocks

        # ── Phase 5: EXCHANGE LEDGER — register operator output ──
        # Both voices on the same chain. The TURN is complete.
        try:
            self._input_ledger.register_v002(
                raw_text=output_text,
                context=felt_domain,
            )
        except Exception:
            pass  # Ledger failure must not block the organism

        return ProcessResult(
            exchange_id=ex_id,
            input_text=donor_input[:100],
            dignity_passed=True,
            patterns_found=len(candidates),
            drops_produced=len(drops),
            output_text=output_text,
            output_blocked=render_result.blocked,
            block_reason=render_result.block_reason if render_result.blocked else "",
            stored=stored,
            artifact_id=artifact_id if stored else "",
            exchange_state="closed",
            breath_cycle=self._breath.cycle,
            drift_level=drift_alert.level.value,
            drift_rate=drift_alert.dD_dt,
            complexity=complexity.value,
            recommended_td=recommended_td,
            agency_A=agency_score.A,
            agency_weakest=agency_score.weakest,
            # ── Full Integration v2.0 fields ──
            sense_mode=sense_reading.mode.value,
            sense_competence=sense_reading.competence.value,
            sense_need_gap=sense_reading.need_gap.value,
            sense_ask_recommended=sense_reading.ask_recommended,
            sense_ask_question=sense_reading.ask_question,
            lab_active=lab_reading.active if lab_reading else False,
            lab_types=[t.value for t in lab_reading.science_types] if lab_reading else [],
            lab_rigor=lab_reading.rigor_level.value if lab_reading else "anecdote",
            lab_forge_needed=lab_reading.forge_needed if lab_reading else False,
            pillar_profile=pillar_profile or {},
            metadata_event_id=metadata_event_id,
            warnings=warnings,
        )

    def export_artifact(self, artifact_id, fmt="json", anonymization="standard"):
        """Export an artifact through the OUT module."""
        artifact = retrieve(artifact_id)
        if artifact is None:
            return None
        return out_export(artifact["content"], fmt=fmt, anonymization_level=anonymization)

    def mirror(self, donor_input):
        """Show the donor what their rain has fed."""
        import hashlib
        h = hashlib.sha256(donor_input.strip().encode()).hexdigest()
        return wisdom_mirror(h, self._drops_archive)

    def pause(self, reason):
        """Pause the organism."""
        return self._breath.pause(reason)

    def resume(self):
        """Resume the organism."""
        return self._breath.resume()

    def state(self):
        """Full organism state."""
        open_ex = len(self._turn.list_open())
        deferred_ex = len(self._turn.list_deferred())

        return OrganismState(
            alive=not self._breath.is_paused,
            breath_cycle=self._breath.cycle,
            breath_paused=self._breath.is_paused,
            stress_level=self._breath.state.stress.value,
            open_exchanges=open_ex,
            deferred_exchanges=deferred_ex,
            pending_messages=self._wire.pending_count(),
            artifacts_stored=len(list_artifacts()),
            receipts_total=receipt_count(),
            last_dignity_check=self._last_dignity,
            drift_level=self._drift.state().level.value,
            drift_rate=self._drift.state().dD_dt,
            drift_consecutive_declines=self._drift.state().consecutive_declines,
            sheltered_exchanges=self._shelter.held_count,
            federation_peers=self._federation.state().peers_known,
            federation_drops_shared=self._federation.state().drops_offered,
            federation_privacy_remaining=self._federation.privacy_budget_remaining,
            decay_active_patterns=len(self._decay.list_active()),
            decay_deep_hum_patterns=len(self._decay.list_deep_hum()),
            decay_cycle=self._decay.cycle_count,
            latency_avg_td=self._latency.state().avg_recommended_td,
            latency_dignity_rate=self._latency.state().dignity_preservation_rate,
            latency_violations=self._latency.violations_count,
            oracle_health=self._oracle.last_report.overall_health if self._oracle.last_report else "unaudited",
            oracle_unwatched=len(self._oracle.witness.unwatched()),
            oracle_witnessed=len(self._oracle.witness.witnessed()),
            oracle_creep_risk=self._oracle.last_report.colonial_creep_risk if self._oracle.last_report else 0.0,
            prevention_level=self._prevention.current_level.name,
            prevention_td_multiplier=self._prevention.current_td_multiplier(),
            prevention_escalations=self._prevention._escalations,
            mycelium_alert=self._mycelium.current_alert.name,
            mycelium_patterns=self._mycelium.patterns_count,
            mycelium_suppressed=self._mycelium.suppressed_count,
            mycelium_epsilon_remaining=self._mycelium._epsilon_remaining,
            gap004_open_tickets=len(self._conflict_engine.open_tickets),
            gap004_unwitnessed=len(self._conflict_engine.unwitnessed_tickets),
            measure_D=self._last_measurement.D if self._last_measurement else 0.0,
            measure_confidence=self._last_measurement.confidence if self._last_measurement else 0.0,
            agency_score=self._last_agency.A if self._last_agency else 0.0,
            agency_weakest=self._last_agency.weakest if self._last_agency else "none",
            agency_collapsed=self._last_agency.is_collapsed if self._last_agency else False,
            agency_measurements=self._agency.scores_count,
            proverb_stress_registered=self._proverb_stress.proverbs_count,
            proverb_stress_tests_run=self._proverb_stress.total_tests,
            proverb_stress_flagged=len(self._proverb_stress.flagged()),
            negative_space_silences=self._negative_space.silences_count,
            negative_space_critical=len([s for s in self._negative_space._silences if s.severity >= 0.8]),
            negative_space_blindness=self._negative_space.report().blindness_score,
            negative_space_cycle=self._negative_space.cycle,
            # Seeds #1-#8
            stewardship_active=self._stewardship.active_count,
            stewardship_uncovered=len(self._stewardship.uncovered_roles()),
            witness_chain_length=self._witness_net.chain_length,
            witness_chain_valid=self._witness_net.verify_chain(),
            democracy_open_proposals=self._democracy.open_proposals,
            democracy_voices=self._democracy.voices_count,
            evolution_active_amendments=self._evolution.active_count,
            evolution_ratified=self._evolution.ratified_count,
            justice_open_harms=self._justice.open_harms,
            justice_repair_rate=self._justice.repair_rate,
            self_awareness_capabilities=self._self_awareness.capabilities_count,
            self_awareness_limitations=self._self_awareness.limitations_count,
            self_awareness_calibration=self._self_awareness.calibration_bias().value,
            parables_deliveries=self._parables.deliveries_count,
            parables_avg_relevance=self._parables.avg_relevance,
            institutional_institutions=self._institutional.institutions_count,
            institutional_evaluations=self._institutional.evaluations_count,
            # Ninth Operator + Gap Solutions + Erasure + Early Warning + Field
            ninth_words_received=self._ninth.words_received,
            ninth_words_witnessed=self._ninth.words_witnessed,
            ninth_words_sheltered=self._ninth.words_sheltered,
            ninth_loop_completions=self._ninth.loop_completions,
            shelter_heartbeat_pending=len(self._shelter_heartbeat.pulse()),
            contests_pending=len(self._contestability.list_pending()),
            erasure_active_donors=self._erasure.active_donor_count(),
            erasure_erased_donors=self._erasure.erased_donor_count(),
            early_warning_ewma_alert=self._ewma.state.breached,
            early_warning_cusum_alert=self._cusum.state.alarm,
            canonicalizer_duplicates=self._canonicalizer.scan().duplicate_count,
            emergency_level=self._emergency.current_level.value,
            field_voices_registered=len(self._field_alcove.genomes),
            field_shadows_canonical=sum(
                len(g.canonical_shadows) for g in self._field_alcove.genomes.values()
            ),
            field_temporal_records=len(self._field_clearing.temporal_index),
            field_donors_registered=len(self._donor_registry.profiles),
            field_audit_count=len(self._field_audit_scheduler.audits),
            steward_observer_patterns=len(self._steward_observer.patterns),
            ratification_total=len(self._ratification._elements),
            ratification_committed=len(self._ratification.committed()),
            ratification_provisional=len(self._ratification.provisional()),
            ratification_ratified=len(self._ratification.ratified()),
            ratification_awaiting_signoff=len(self._ratification.awaiting_signoff()),
            # ── Full Integration v2.0: SENSE + LAB + Metadata + Pillars + Privacy + Divergence ──
            sense_mode=self._last_sense.mode.value if self._last_sense else "unknown",
            sense_competence=self._last_sense.competence.value if self._last_sense else "unknown",
            sense_need_gap=self._last_sense.need_gap.value if self._last_sense else "unknown",
            sense_crisis_flag=self._last_sense.crisis_flag if self._last_sense else False,
            lab_active=self._last_lab.active if self._last_lab else False,
            lab_primary_type=self._last_lab.primary_type.value if self._last_lab and self._last_lab.primary_type else "none",
            lab_rigor=self._last_lab.rigor_level.value if self._last_lab else "anecdote",
            lab_forge_needed=self._last_lab.forge_needed if self._last_lab else False,
            metadata_total_events=self._metadata.total_events,
            metadata_discoveries=self._metadata.total_discoveries,
            pillar_dominant=self._last_pillar_profile.get("dominant_pillar", "none") if self._last_pillar_profile else "none",
            pillar_multi=self._last_pillar_profile.get("multi_pillar", False) if self._last_pillar_profile else False,
            pillar_wisdom_potential=self._last_pillar_profile.get("wisdom_potential", 0.0) if self._last_pillar_profile else 0.0,
            privacy_budget_remaining=self._privacy_budget.state().remaining,
            privacy_budget_locked=self._privacy_budget.is_locked,
            amendments_refusals=len(self._refusal_map.records),
            amendments_drift_detected=len(self._baseline_drift.drift_signals) > 0,
            # ── Compass (MOVE-001) ──
            compass_calibrated=self._compass.state().get("calibrated", False),
            compass_readings=self._compass.state().get("readings", 0),
            compass_blockers=self._compass.state().get("blockers_count", 0),
            compass_deployed=self._compass.state().get("deployed", False),
            # ── Letter Chain (convergence-experiment) ──
            letter_ontology_total=len(ALL_LETTERS),
            letter_ontology_non_connectors=len(NON_CONNECTORS),
            letter_ontology_connectors=len(ALL_LETTERS) - len(NON_CONNECTORS),
            witness_certificates_generated=self._witness_certs_generated,
            # ── Boot Ritual (2026-03-18) ──
            boot_ritual_passed=self._boot_result.passed,
            boot_ritual_checks=len(self._boot_result.checks),
            boot_ritual_failures=len([c for c in self._boot_result.checks if not c.passed]),
            timestamp=self._now(),
        )

    def shelter_status(self, exchange_id):
        """Get shelter record for a blocked exchange."""
        return self._shelter.get(exchange_id)

    def shelter_list(self):
        """List all exchanges currently held in shelter."""
        return self._shelter.list_held()

    def shelter_withdraw(self, exchange_id):
        """Donor withdraws a sheltered exchange."""
        return self._shelter.mark_withdrawn(exchange_id)

    def shelter_review(self, exchange_id, note):
        """Steward reviews a sheltered exchange."""
        return self._shelter.steward_review(exchange_id, note)

    def federate_offer(self, peer_id, min_contributors=7):
        """Offer local drops to a peer organism via EFP."""
        prepared = []
        for drop in self._drops_archive:
            fd = self._federation.prepare_drop(
                content=drop.essence,
                drop_type=drop.drop_type,
                confidence=drop.confidence,
                contributor_count=max(min_contributors, len(drop.source_hashes)),
            )
            if fd is not None:
                prepared.append(fd)
        if not prepared:
            return None
        return self._federation.offer(prepared, peer_id)

    def federate_receive(self, drops, peer_id):
        """Receive drops from a peer organism via EFP."""
        return self._federation.receive(drops, peer_id)

    def federate_merge(self, drop_hashes):
        """Merge received federated drops into local wisdom."""
        return self._federation.merge(drop_hashes)

    def federation_state(self):
        """Get federation layer state."""
        return self._federation.state()

    def srvp_evaluator(self, subject_id=None):
        """Get an SRVP evaluator for this organism."""
        return SRVPEvaluator(
            subject_id=subject_id or "ORG-kalam-LOCAL",
            evaluator="steward",
        )

    def sip_evaluate(self):
        """Run SIP evaluation on current module activity."""
        return self._sip.evaluate()

    def collective_check(self, texts):
        """Run collective dignity across a cohort."""
        return check_collective_dignity(texts)

    def sync_all(self):
        """Synchronize all modules through BREATH."""
        return self._breath.sync([
            "CHECK", "FACE", "KEEP", "WIRE",
            "BREATH", "SAY", "OUT", "TURN", "WEAVE",
        ])

    def display_state(self):
        """Print organism state to terminal."""
        s = self.state()
        print(f"\n  {'='*48}")
        print(f"  kalam ORGANISM — {'ALIVE' if s.alive else 'PAUSED'}")
        print(f"  {'='*48}")
        print(f"  Breath cycle:      {s.breath_cycle}")
        print(f"  Stress:            {s.stress_level}")
        print(f"  Open exchanges:    {s.open_exchanges}")
        print(f"  Deferred:          {s.deferred_exchanges}")
        print(f"  Pending messages:  {s.pending_messages}")
        print(f"  Artifacts stored:  {s.artifacts_stored}")
        print(f"  Receipts:          {s.receipts_total}")
        print(f"  Dignity drift:     {s.drift_level} (dD/dt={s.drift_rate:.4f})")
        print(f"  Consecutive drops: {s.drift_consecutive_declines}")
        print(f"  Sheltered:         {s.sheltered_exchanges}")
        print(f"  Federation peers:  {s.federation_peers}")
        print(f"  Drops shared:      {s.federation_drops_shared}")
        print(f"  Privacy budget:    {s.federation_privacy_remaining:.2f}/{1.0:.2f}")
        print(f"  Decay cycle:       {s.decay_cycle}")
        print(f"  Active patterns:   {s.decay_active_patterns}")
        print(f"  Deep Hum archive:  {s.decay_deep_hum_patterns}")
        print(f"  Avg T_d:           {s.latency_avg_td:.2f}s")
        print(f"  Dignity-latency:   {s.latency_dignity_rate:.1%}")
        print(f"  Latency violations:{s.latency_violations}")
        print(f"  Oracle health:     {s.oracle_health}")
        print(f"  Unwatched (W-0/1): {s.oracle_unwatched}")
        print(f"  Witnessed (W-3+):  {s.oracle_witnessed}")
        print(f"  Colonial creep:    {s.oracle_creep_risk:.1%}")
        print(f"  Prevention level:  {s.prevention_level}")
        print(f"  T_d multiplier:    {s.prevention_td_multiplier:.1f}x")
        print(f"  Escalations:       {s.prevention_escalations}")
        print(f"  Mycelium alert:    {s.mycelium_alert}")
        print(f"  Patterns found:    {s.mycelium_patterns}")
        print(f"  Patterns hidden:   {s.mycelium_suppressed} (k<{K_ANONYMITY_FLOOR})")
        print(f"  Privacy budget:    {s.mycelium_epsilon_remaining:.2f}ε remaining")
        print(f"  GAP#004 open:      {s.gap004_open_tickets}")
        print(f"  GAP#004 unseen:    {s.gap004_unwitnessed}")
        print(f"  Measure D:         {s.measure_D:.3f} (confidence {s.measure_confidence:.2f})")
        print(f"  Agency A:          {s.agency_score:.3f} (weakest: {s.agency_weakest})")
        print(f"  Agency collapsed:  {s.agency_collapsed}")
        print(f"  Agency measures:   {s.agency_measurements}")
        print(f"  Proverb stress:    {s.proverb_stress_registered} registered, {s.proverb_stress_tests_run} tests, {s.proverb_stress_flagged} flagged")
        print(f"  Negative space:    {s.negative_space_silences} silences ({s.negative_space_critical} critical), blindness={s.negative_space_blindness:.3f}")
        print(f"  NS cycle:          {s.negative_space_cycle}")
        print(f"  {'-'*48}")
        print(f"  Stewardship:       {s.stewardship_active} active, {s.stewardship_uncovered} uncovered")
        print(f"  Witness chain:     {s.witness_chain_length} records, valid={s.witness_chain_valid}")
        print(f"  Democracy:         {s.democracy_open_proposals} open proposals, {s.democracy_voices} voices")
        print(f"  Evolution:         {s.evolution_active_amendments} active, {s.evolution_ratified} ratified")
        print(f"  Justice:           {s.justice_open_harms} open harms, repair rate={s.justice_repair_rate:.1%}")
        print(f"  Self-awareness:    {s.self_awareness_capabilities} caps, {s.self_awareness_limitations} lims, {s.self_awareness_calibration}")
        print(f"  Parables:          {s.parables_deliveries} deliveries, relevance={s.parables_avg_relevance:.3f}")
        print(f"  Institutional:     {s.institutional_institutions} institutions, {s.institutional_evaluations} evals")
        print(f"  {'-'*48}")
        print(f"  Ninth Operator:    {s.ninth_words_received} received, {s.ninth_words_witnessed} witnessed, {s.ninth_loop_completions} loops")
        print(f"  Ninth sheltered:   {s.ninth_words_sheltered}")
        print(f"  Heartbeat pending: {s.shelter_heartbeat_pending}")
        print(f"  Contests pending:  {s.contests_pending}")
        print(f"  Erasure active:    {s.erasure_active_donors} donors, {s.erasure_erased_donors} erased")
        print(f"  EWMA alert:        {s.early_warning_ewma_alert}")
        print(f"  CUSUM alert:       {s.early_warning_cusum_alert}")
        print(f"  Canon duplicates:  {s.canonicalizer_duplicates}")
        print(f"  Emergency level:   {s.emergency_level}")
        print(f"  {'-'*48}")
        print(f"  FIELD voices:      {s.field_voices_registered}")
        print(f"  FIELD shadows:     {s.field_shadows_canonical} canonical")
        print(f"  FIELD temporal:    {s.field_temporal_records} records")
        print(f"  FIELD donors:      {s.field_donors_registered}")
        print(f"  FIELD audits:      {s.field_audit_count}")
        print(f"  Steward patterns:  {s.steward_observer_patterns}")
        print(f"  {'-'*48}")
        print(f"  Ratification:      {s.ratification_total} total ({s.ratification_ratified} ratified, {s.ratification_provisional} provisional, {s.ratification_committed} committed)")
        print(f"  Awaiting sign-off: {s.ratification_awaiting_signoff}")
        print(f"  {'-'*48}")
        print(f"  SENSE mode:        {s.sense_mode} (competence: {s.sense_competence})")
        print(f"  SENSE need gap:    {s.sense_need_gap}")
        print(f"  SENSE crisis:      {s.sense_crisis_flag}")
        print(f"  LAB active:        {s.lab_active} (type: {s.lab_primary_type}, rigor: {s.lab_rigor})")
        print(f"  LAB forge needed:  {s.lab_forge_needed}")
        print(f"  Metadata events:   {s.metadata_total_events}")
        print(f"  Metadata discovers:{s.metadata_discoveries}")
        print(f"  Pillar dominant:   {s.pillar_dominant} (multi: {s.pillar_multi})")
        print(f"  Pillar wisdom:     {s.pillar_wisdom_potential:.3f}")
        print(f"  Privacy ε remain:  {s.privacy_budget_remaining:.2f}")
        print(f"  Privacy locked:    {s.privacy_budget_locked}")
        print(f"  Amendments refuse: {s.amendments_refusals}")
        print(f"  Baseline drift:    {s.amendments_drift_detected}")
        print(f"  {'='*48}\n")

    def decay_state(self):
        """Get decay engine state counts."""
        return self._decay.state_counts()

    def decay_invoke(self, pattern_id):
        """Manually invoke a pattern — restores full weight."""
        return self._decay.invoke(pattern_id)

    def decay_contest(self, pattern_id):
        """Contest a pattern — resets and enters review."""
        return self._decay.contest(pattern_id)

    def decay_resolve(self, pattern_id):
        """Resolve a contested pattern."""
        return self._decay.resolve_contestation(pattern_id)

    def decay_list_deep_hum(self):
        """List all patterns in the Deep Hum archive."""
        return [r.to_dict() for r in self._decay.list_deep_hum()]

    def latency_profile(self, complexity_str):
        """Get the latency profile for a complexity level."""
        from WEAVER.latency import ComplexityLevel
        try:
            level = ComplexityLevel(complexity_str)
        except ValueError:
            return None
        return self._latency.get_profile(level)

    def latency_state(self):
        """Get latency tracker state."""
        return self._latency.state()

    def lock_test(self, proverb):
        """Run the Lock Test on a proverb candidate."""
        return self._lock_test.test(proverb)

    def lock_test_with_paraphrase(self, original, paraphrase):
        """Run enhanced Lock Test with paraphrase comparison."""
        return self._lock_test.test_with_paraphrase(original, paraphrase)

    def lock_test_stats(self):
        """Get Lock Test statistics."""
        return {
            "tests_run": self._lock_test.tests_run,
            "locked": self._lock_test.locked_count,
            "lock_rate": round(self._lock_test.lock_rate, 4),
        }

    def voice_audit(self, text, context=""):
        """Audit text against the 6 Axi voice rules."""
        return audit_voice(text, context)

    def oracle_audit(self):
        """Run a full Oracle self-audit cycle."""
        drift_state = self._drift.state()
        latency_state = self._latency.state()
        return self._oracle.audit(
            drift_rate=drift_state.dD_dt,
            drift_level=drift_state.level.value,
            voice_score=1.0,  # Updated by last render
            breath_paused=self._breath.is_paused,
            violations_count=latency_state.violations,
            lock_rate=self._lock_test.lock_rate,
            latency_dignity_rate=latency_state.dignity_preservation_rate,
        )

    def oracle_witness(self, element_id, element_type="unknown"):
        """Register an element in the Witness Scale."""
        return self._oracle.witness.process(element_id, element_type)

    def oracle_steward_sees(self, element_id, session_id=""):
        """Mark an element as seen by the steward (W-3)."""
        return self._oracle.witness.steward_sees(element_id, session_id)

    def oracle_check_relay(self, correction_trace, response_fidelity, steward_recognition):
        """Run proprioception check on the relay."""
        return self._oracle.check_relay(correction_trace, response_fidelity, steward_recognition)

    def oracle_witness_distribution(self):
        """Get Witness Scale distribution."""
        return self._oracle.witness.distribution()

    def oracle_unwatched(self):
        """List all unwatched elements (W-0 or W-1)."""
        return [(r.element_id, r.level.name) for r in self._oracle.witness.unwatched()]

    def oracle_report(self):
        """Get the last Oracle report."""
        return self._oracle.last_report

    def prevention_state(self):
        """Get prevention system state."""
        return self._prevention.state()

    def prevention_signal(self):
        """Get the last prevention signal."""
        return self._prevention.last_signal

    def prevention_is_alarm(self):
        """Is the prevention system in ALARM state?"""
        return self._prevention.is_alarm()

    def mycelium_scan(self):
        """Scan mycelium for cross-donor patterns."""
        return self._mycelium.scan()

    def mycelium_state(self):
        """Get mycelium network state."""
        return self._mycelium.state()

    def mycelium_is_rhizome(self):
        """Is there a critical structural pattern?"""
        return self._mycelium.is_rhizome()

    def gap004_process(self, text, individual_scores=None, failed_components=None):
        """Run full GAP#004 conflict engine on text."""
        return self._conflict_engine.process(text, individual_scores, failed_components)

    def gap004_steward_sees(self, ticket):
        """Mark a GAP#004 conflict as seen by steward (W-3)."""
        return self._conflict_engine.steward_sees(ticket)

    def gap004_steward_holds(self, ticket):
        """Mark a GAP#004 conflict as held by steward (W-4)."""
        return self._conflict_engine.steward_holds(ticket)

    def gap004_open_tickets(self):
        """List all open GAP#004 conflict tickets."""
        return self._conflict_engine.open_tickets

    def gap004_unwitnessed(self):
        """List conflicts steward hasn't seen yet."""
        return self._conflict_engine.unwitnessed_tickets

    def last_measurement(self):
        """Get last graduated dignity measurement (GAP#014/015)."""
        return self._last_measurement

    # ── Agency Amplifier (Seed #12) ──────────────────────────

    def agency_measure(self, exchange_id, V, F, C, U, notes=""):
        """Manually measure agency for an exchange."""
        score = self._agency.measure(exchange_id, V=V, F=F, C=C, U=U, notes=notes)
        self._last_agency = score
        return score

    def agency_report(self):
        """Get agency report across all measurements."""
        return self._agency.report()

    def agency_last(self):
        """Get last agency score."""
        return self._last_agency

    # ── Proverb Stress Test (Seed #11) ───────────────────────

    def proverb_stress_register(self, proverb_id, text, domain):
        """Register a proverb for stress testing."""
        self._proverb_stress.register_proverb(proverb_id, text, domain)

    def proverb_stress_test(self, proverb_id, anomaly_id, held, notes=""):
        """Apply a proverb to an anomaly and record whether it held."""
        return self._proverb_stress.test(proverb_id, anomaly_id, held, notes)

    def proverb_stress_report(self, proverb_id):
        """Get stress report for a single proverb."""
        return self._proverb_stress.report(proverb_id)

    def proverb_stress_report_all(self):
        """Get stress reports for all registered proverbs."""
        return self._proverb_stress.report_all()

    def proverb_stress_flagged(self):
        """Get proverbs that need steward attention."""
        return self._proverb_stress.flagged()

    # ── Negative Space Index (Seed #9) ───────────────────────

    def negative_space_register_domain(self, domain):
        """Register a domain for negative space tracking."""
        self._negative_space.register_domain(domain)

    def negative_space_register_pattern(self, pattern_type, expected_by):
        """Register an expected pattern type."""
        self._negative_space.register_expected_pattern(pattern_type, expected_by)

    def negative_space_register_voice(self, voice_id):
        """Register a voice (participant) for silence detection."""
        self._negative_space.register_voice(voice_id)

    def negative_space_register_question(self, question, expected_by):
        """Register a question the system should eventually ask."""
        self._negative_space.register_question(question, expected_by)

    def negative_space_report(self):
        """Get the current negative space report."""
        return self._negative_space.report()

    def negative_space_observe(self, identifier):
        """Manually observe something (domain, pattern, voice)."""
        self._negative_space.observe(identifier)

    # ── Seed #1: Distributed Stewardship ─────────────────

    def stewardship_delegate(self, steward_id, role, scope=""):
        """Delegate a steward role."""
        return self._stewardship.delegate(steward_id, role, scope=scope)

    def stewardship_rotate(self, delegation_id, new_steward_id):
        """Rotate a role to a new steward."""
        return self._stewardship.rotate(delegation_id, new_steward_id)

    def stewardship_check(self):
        """Check for power concentration."""
        return self._stewardship.check_concentration()

    def stewardship_report(self):
        """Get stewardship health report."""
        return self._stewardship.report()

    # ── Seed #2: Immutable Witness Network ───────────────

    def witness(self, event_type, event_summary, actor_id="organism"):
        """Record an event on the witness chain."""
        return self._witness_net.witness(event_type, event_summary, actor_id)

    def witness_verify(self):
        """Verify the witness chain integrity."""
        return self._witness_net.verify_chain()

    def witness_report(self):
        """Get witness network health report."""
        return self._witness_net.report()

    # ── Seed #3: Deliberative Democracy ──────────────────

    def democracy_register_voice(self, voice_id, participation_score=0.0):
        """Register a voice for deliberation."""
        return self._democracy.register_voice(voice_id, participation_score)

    def democracy_propose(self, proposer_id, title, description):
        """Submit a proposal."""
        return self._democracy.propose(proposer_id, title, description)

    def democracy_deliberate(self, proposal_id, voice_id, vote, statement, concerns=None):
        """Add a voice's deliberation."""
        return self._democracy.deliberate(proposal_id, voice_id, vote, statement, concerns)

    def democracy_resolve(self, proposal_id, resolution):
        """Resolve a proposal."""
        return self._democracy.resolve(proposal_id, resolution)

    def democracy_speaking_order(self):
        """Get weakest-voice-first speaking order."""
        return self._democracy.speaking_order()

    def democracy_report(self):
        """Get deliberation health report."""
        return self._democracy.report()

    # ── Seed #4: Constitutional Evolution ────────────────

    def evolution_propose(self, proposer, target_covenant, tier, title, description):
        """Propose a constitutional amendment."""
        return self._evolution.propose(proposer, target_covenant, tier, title, description)

    def evolution_cool(self, amendment_id):
        """Enter cooling period."""
        return self._evolution.enter_cooling(amendment_id)

    def evolution_ratify(self, amendment_id, ratifier):
        """Ratify an amendment."""
        return self._evolution.ratify(amendment_id, ratifier)

    def evolution_report(self):
        """Get constitutional evolution report."""
        return self._evolution.report()

    # ── Seed #5: Restorative Justice ─────────────────────

    def justice_record_harm(self, exchange_id, severity, failed_components, description):
        """Record a dignity violation."""
        return self._justice.record_harm(exchange_id, severity, failed_components, description)

    def justice_acknowledge(self, harm_id):
        """Acknowledge a harm."""
        return self._justice.acknowledge(harm_id)

    def justice_propose_repair(self, harm_id, action, responsible):
        """Propose a repair action."""
        return self._justice.propose_repair(harm_id, action, responsible)

    def justice_complete_repair(self, repair_id, outcome):
        """Complete a repair."""
        return self._justice.complete_repair(repair_id, outcome)

    def justice_report(self):
        """Get restorative justice report."""
        return self._justice.report()

    # ── Seed #6: System Self-Awareness ───────────────────

    def self_awareness_register_capability(self, cap_id, domain, description, level):
        """Register a system capability."""
        return self._self_awareness.register_capability(cap_id, domain, description, level)

    def self_awareness_register_limitation(self, lim_id, domain, description, severity=0.5):
        """Register a system limitation."""
        return self._self_awareness.register_limitation(lim_id, domain, description, severity=severity)

    def self_awareness_calibrate(self, predicted, actual, domain):
        """Record a calibration measurement."""
        self._self_awareness.record_calibration(predicted, actual, domain)

    def self_awareness_report(self):
        """Get self-awareness report."""
        return self._self_awareness.report()

    # ── Seed #7: Personalized Parables ───────────────────

    def parables_register_donor(self, donor_id, domains=None, style="direct"):
        """Register a donor for personalized wisdom delivery."""
        return self._parables.register_donor(donor_id, domains=domains, preferred_style=style)

    def parables_deliver(self, proverb_id, proverb_text, donor_id, theme=""):
        """Deliver a personalized proverb."""
        return self._parables.deliver(proverb_id, proverb_text, donor_id, donor_theme=theme)

    def parables_report(self):
        """Get parables delivery report."""
        return self._parables.report()

    # ── Seed #8: Institutional Dignity Score ─────────────

    def institutional_register(self, institution_id, name, sector=""):
        """Register an institution for dignity evaluation."""
        return self._institutional.register(institution_id, name, sector=sector)

    def institutional_record(self, institution_id, D):
        """Record an individual dignity score for an institution."""
        return self._institutional.record_exchange(institution_id, D)

    def institutional_evaluate(self, institution_id):
        """Evaluate an institution's dignity score."""
        return self._institutional.evaluate(institution_id)

    def institutional_report(self):
        """Get institutional dignity report."""
        return self._institutional.report()

    # ── Ninth Operator (Word Loop) ───────────────────────

    def ninth_receive(self, text, domain="donor-exchange"):
        """Receive a word into the Ninth Operator loop."""
        return self._ninth.receive_word(text, domain)

    def ninth_witness(self, word_id):
        """Witness a word (dignity check within the loop)."""
        return self._ninth.witness(word_id)

    def ninth_return(self, word_id):
        """Return a witnessed word to the donor."""
        return self._ninth.return_word(word_id)

    def ninth_report(self):
        """Get Ninth Operator report."""
        return {
            "words_received": self._ninth.words_received,
            "words_witnessed": self._ninth.words_witnessed,
            "words_sheltered": self._ninth.words_sheltered,
            "loop_completions": self._ninth.loop_completions,
        }

    # ── Gap Solutions (GAP#022-026) ──────────────────────

    def overprotection_check(self, measurement, exchange_history=None):
        """Check if a block is overprotective (GAP#022)."""
        return self._overprotection.check(measurement, exchange_history or [])

    def steward_shadow_propose(self, override_type, scope, justification, steward_id="steward"):
        """Propose a steward override (GAP#023)."""
        return self._steward_shadow.propose(override_type, scope, justification, steward_id)

    def steward_shadow_ratify(self, proposal_id, second_steward=None):
        """Ratify a steward override after delay expires."""
        return self._steward_shadow.ratify_override(proposal_id, second_steward)

    def steward_shadow_pending(self):
        """List pending steward override proposals."""
        return self._steward_shadow.list_pending()

    def shelter_heartbeat_register(self, exchange_id, sheltered_at=""):
        """Register a sheltered exchange for heartbeat monitoring."""
        if not sheltered_at:
            sheltered_at = self._now()
        return self._shelter_heartbeat.register(exchange_id, sheltered_at)

    def shelter_heartbeat_pulse(self):
        """Pulse all registered shelter heartbeats."""
        return self._shelter_heartbeat.pulse()

    def contest_file(self, exchange_id, reason):
        """File a contestability claim (GAP#026)."""
        return self._contestability.contest(exchange_id, reason)

    def contest_add_context(self, contest_id, context):
        """Add context to a pending contest."""
        return self._contestability.add_context(contest_id, context)

    def contest_resolve(self, contest_id, outcome, steward_note):
        """Resolve a contest."""
        return self._contestability.resolve(contest_id, outcome, steward_note)

    def contest_pending(self):
        """List pending contests."""
        return self._contestability.list_pending()

    # ── Cryptographic Erasure ────────────────────────────

    def erasure_seal(self, donor_id, data):
        """Seal donor data with cryptographic erasure envelope. Data must be bytes."""
        return self._erasure.seal(donor_id, data)

    def erasure_unseal(self, donor_id, blob):
        """Unseal (read) donor data from a sealed blob."""
        return self._erasure.unseal(donor_id, blob)

    def erasure_erase(self, donor_id):
        """Erase donor data by destroying the key (GDPR Art. 17)."""
        return self._erasure.erase(donor_id)

    def erasure_report(self):
        """Get erasure status report."""
        return {
            "active_donors": self._erasure.active_donor_count(),
            "erased_donors": self._erasure.erased_donor_count(),
        }

    # ── Early Warning (EWMA + CUSUM) ────────────────────

    def early_warning_state(self):
        """Get early warning detector states."""
        return {
            "ewma": self._ewma.state,
            "cusum": self._cusum.state,
        }

    def early_warning_reset(self):
        """Reset early warning detectors."""
        self._ewma.reset()
        self._cusum.reset()

    # ── Canonicalize + Signing + Emergency ───────────────

    def canonicalize_scan(self):
        """Scan codebase for duplicate IDs."""
        return self._canonicalizer.scan()

    def sign_artifact(self, artifact_id, data):
        """Sign an artifact with Ed25519."""
        return self._signer.sign(artifact_id, data)

    def emergency_escalate(self, level, trigger, description, initiated_by="system"):
        """Escalate emergency governance level."""
        return self._emergency.escalate(level, trigger, description, initiated_by)

    def emergency_resolve(self, record_id, resolution, resolved_by="steward"):
        """Resolve an emergency escalation."""
        return self._emergency.resolve(record_id, resolution, resolved_by)

    def emergency_state(self):
        """Get emergency governance state."""
        return {
            "level": self._emergency.current_level.value,
            "open_escalations": len(self._emergency.open_escalations),
        }

    # ── FIELD Layer ──────────────────────────────────────

    def field_register_voice(self, voice_id, voice_name=""):
        """Register a voice in the FIELD alcove."""
        return self._field_alcove.register_voice(voice_id, voice_name)

    def field_record_shadow(self, voice_id, description, domain, session_id):
        """Record a shadow observation for a voice."""
        return self._field_alcove.record_shadow(voice_id, description, domain, session_id)

    def field_voice_report(self, voice_id):
        """Get a voice's shadow genome report."""
        genome = self._field_alcove.get_genome(voice_id)
        if genome is None:
            return None
        return genome.to_dict()

    def field_compare_genomes(self):
        """Compare all voice genomes for cross-voice patterns."""
        return self._field_alcove.compare_genomes()

    def field_temporal_index(self, fingerprint, domain, description, voices=None):
        """Index a temporal shadow observation."""
        return self._field_clearing.index_temporal_shadow(fingerprint, domain, description, voices or [])

    def field_temporal_divergence(self, absent_element, voices, session_id, certainty=3):
        """Detect a divergence shadow."""
        return self._field_clearing.detect_divergence_shadow(absent_element, voices, session_id, certainty)

    def field_temporal_convergence(self, finding, voices, session_id, certainty=3):
        """Detect convergent emergence."""
        return self._field_clearing.detect_convergent_emergence(finding, voices, session_id, certainty)

    def field_register_donor(self, donor_id):
        """Register a donor in the FIELD donor registry."""
        return self._donor_registry.get_or_create(donor_id)

    def field_donor_profile(self, donor_id):
        """Get a donor's profile."""
        return self._donor_registry.get_profile(donor_id)

    def field_schedule_audit(self):
        """Schedule a FIELD self-audit if due."""
        if self._field_audit_scheduler.should_audit():
            return self._field_audit_scheduler.schedule_audit()
        return None

    def field_audit_history(self):
        """Get FIELD audit history."""
        return self._field_audit_scheduler.get_audit_history()

    def steward_observer_record(self, record):
        """Record a steward ratification for observation."""
        return self._steward_observer.record_ratification(record)

    def steward_observer_report(self):
        """Get steward observation summary."""
        return self._steward_observer.get_summary()

    # ── Full System Report ───────────────────────────────

    def full_report(self):
        """Generate a comprehensive system health report across all modules."""
        return {
            "organism": "alive" if not self._breath.is_paused else "paused",
            "breath_cycle": self._breath.cycle,
            "exchanges_processed": self._exchange_counter,
            "dignity_drift": self._drift.state().level.value,
            "oracle": self._oracle.last_report.overall_health if self._oracle.last_report else "unaudited",
            "prevention": self._prevention.current_level.name,
            "mycelium": self._mycelium.current_alert.name,
            "ninth_operator": self.ninth_report(),
            "early_warning": {
                "ewma_breached": self._ewma.state.breached,
                "cusum_alarm": self._cusum.state.alarm,
            },
            "emergency": self._emergency.current_level.value,
            "justice": self._justice.report(),
            "democracy": self._democracy.report(),
            "evolution": self._evolution.report(),
            "stewardship": self._stewardship.report(),
            "witness_chain": self._witness_net.report(),
            "self_awareness": self._self_awareness.report(),
            "erasure": self.erasure_report(),
            "field": {
                "voices": len(self._field_alcove.genomes),
                "donors": len(self._donor_registry.profiles),
                "audits": len(self._field_audit_scheduler.audits),
                "steward_patterns": len(self._steward_observer.patterns),
            },
            "ratification": self._ratification.summary(),
            # ── Full Integration v2.0 ──
            "sense": {
                "mode": self._last_sense.mode.value if self._last_sense else "unknown",
                "competence": self._last_sense.competence.value if self._last_sense else "unknown",
                "need_gap": self._last_sense.need_gap.value if self._last_sense else "unknown",
                "crisis_flag": self._last_sense.crisis_flag if self._last_sense else False,
            },
            "lab": {
                "active": self._last_lab.active if self._last_lab else False,
                "primary_type": self._last_lab.primary_type.value if self._last_lab and self._last_lab.primary_type else "none",
                "rigor": self._last_lab.rigor_level.value if self._last_lab else "anecdote",
                "forge_needed": self._last_lab.forge_needed if self._last_lab else False,
            },
            "metadata": {
                "total_events": self._metadata.total_events,
                "discoveries": self._metadata.total_discoveries,
                "domains_active": self._metadata.domains_active,
            },
            "pillars": {
                "dominant": self._last_pillar_profile.get("dominant_pillar") if self._last_pillar_profile else None,
                "multi": self._last_pillar_profile.get("multi_pillar", False) if self._last_pillar_profile else False,
                "wisdom_potential": self._last_pillar_profile.get("wisdom_potential", 0.0) if self._last_pillar_profile else 0.0,
            },
            "privacy_budget": self._privacy_budget.state().__dict__ if hasattr(self._privacy_budget.state(), '__dict__') else {},
            "amendments": {
                "refusals": len(self._refusal_map.records),
            },
        }

    # ── SENSE + LAB (Nervous System) ────────────────────

    def last_sense(self):
        """Get last SENSE reading."""
        return self._last_sense

    def last_lab(self):
        """Get last LAB reading."""
        return self._last_lab

    def last_pillar_profile(self):
        """Get last unified pillar detection profile."""
        return self._last_pillar_profile

    # ── Metadata Layer (The Brain) ──────────────────────

    def metadata_query_recent(self, n=10):
        """Query recent metadata events."""
        return self._metadata.query_recent(n)

    def metadata_discover(self):
        """Run metadata discovery — find non-obvious connections."""
        return self._metadata.discover()

    def metadata_detect_echoes(self, scan_last_n=30):
        """Detect echo patterns in metadata."""
        return self._metadata.detect_echoes(scan_last_n)

    def metadata_state(self):
        """Get metadata gathering state."""
        return self._metadata.state()

    # ── Privacy Budget ──────────────────────────────────

    def privacy_budget_state(self):
        """Get global privacy budget state."""
        return self._privacy_budget.state()

    def privacy_budget_lock(self, reason="manual"):
        """Lock the privacy budget."""
        return self._privacy_budget.lock(reason)

    def privacy_budget_unlock(self, steward_approval="steward"):
        """Unlock the privacy budget."""
        return self._privacy_budget.unlock(steward_approval)
