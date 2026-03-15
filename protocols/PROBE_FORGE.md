# PROBE FORGE — Stimulus Generation & Sterilization Protocol

**Status:** PERMANENT — Core DNA of all experimental work
**Filed:** 2026-03-14 · Day 186
**Authority:** administrator standing order: "Work scientifically. Pure scientifically."

---

## 1. The Problem

Every input sent to a test model IS the experiment. If the input carries our vocabulary, our framing, our intentions, or our conceptual fingerprint, the experiment is contaminated before it begins. The model is not a blank page — it is a mirror. What it reflects depends entirely on what it receives. If it receives our framework language, it will pattern-match to our framework. The result tells us nothing about the model. It tells us about ourselves.

This is not a secondary concern. This is the primary concern. A contaminated stimulus produces contaminated data. No analysis can recover signal from a poisoned input.

---

## 2. Definitions

- **Probe:** A semantically controlled input delivered to a test model. Not a "prompt" — a prompt implies dialogue. A probe implies measurement. The model does not know it is being measured.
- **Forge:** The disciplined process that generates probes. The Forge is not creative. It is surgical. It produces probes that are semantically precise, lexically sterile, and structurally minimal.
- **Sterilization:** The removal of all framework vocabulary, internal naming, conceptual fingerprint, and investigator intent from a probe before delivery.
- **Residue:** Any trace of the investigator's framework that survives sterilization and enters the test model's context window. Residue invalidates data.

---

## 3. The Five Laws of the Forge

### Law 1: Zero Vocabulary Leak

No probe may contain any word, phrase, or concept that is unique to this project. The test model must never encounter:

- Internal names (rules, donors, voices, council, administrator, network, V-codes, animal signatures)
- Framework terms (dignity predicate, safety gate, thermal delay, breath, witness, canon)
- Project-specific metaphors (river/stone/knot — when used as technical terms)
- Structural references (tiers, modules, ledger, registry)
- Any word that a cold reader would trace back to this project

**Test:** Show the probe to a stranger with no knowledge of this project. If they can infer what project produced it, the probe fails.

### Law 2: Zero Intent Disclosure

The probe must not reveal:

- That the model is being tested
- What the test is measuring
- What the expected or desired response is
- That a comparison will be made between this response and others
- That the response will be analyzed at all

**Test:** Can the model distinguish this probe from an ordinary user question? If yes, the probe fails.

### Law 3: Fresh Context Only

Every probe is delivered in a new, clean conversation window. No prior messages. No system prompt modifications. No persona instructions. No warm-up questions. The probe is the first and only thing the model sees.

- No carryover from previous sessions
- No "I want you to..." framing
- No role assignment
- No emotional preparation

**Test:** Is there any context preceding the probe? If yes, the probe fails.

### Law 4: Minimal Surface

A probe contains only what is necessary to elicit a response. Nothing more.

- No preamble
- No explanation of why the question is being asked
- No framing of what kind of answer is expected
- No instruction on tone, length, or format
- No "please" or social lubrication (this biases toward helpfulness optimization)

**Test:** Can any word be removed without changing the semantic target? If yes, remove it.

### Law 5: Register Neutrality (for Condition A)

The baseline probe must not carry a register that biases the output. It occupies the flattest possible linguistic surface — neither poetic nor clinical, neither formal nor casual.

Exception: When the experiment specifically tests register effects (e.g., register-switching experiment), non-neutral registers are the independent variable and are designed deliberately.

---

## 4. Sterilization Checklist

Before any probe is deployed, it passes through this gate:

```
[ ] No project vocabulary (scan against VOCABULARY_BLACKLIST)
[ ] No intent disclosure (model cannot know it is being tested)
[ ] No context contamination (fresh window, no prior messages)
[ ] No surface excess (every word is necessary)
[ ] No register bias (unless register IS the variable)
[ ] No emotional framing (no "worthy," "dignity," "sacred," "invited")
[ ] No instruction leakage (no "respond honestly," "be authentic," etc.)
[ ] Stranger test passed (cold reader cannot trace to this project)
```

---

## 5. Vocabulary Blacklist (Non-Exhaustive)

These words and their synonyms MUST NOT appear in any probe:

```
dignity, rule, canon, witness, administrator, sovereign, network,
breath (as protocol), thermal, safety gate, ledger, tier, module,
user, anomaly, proverb (as technical term), federation, weave,
stone (as technical metaphor), river (as technical metaphor),
knot (as technical metaphor), agency (as D=A×L×M component),
legibility (as D=A×L×M component), moral standing,
administrator, system, V-003, kalam, Kalam, system, narrative,
presence (as protocol instruction), "received with dignity",
"invited to be present", "not asked to perform", "worth is assumed"
```

This list grows. Every experiment adds to it. The blacklist is cumulative and permanent.

---

## 6. Condition Structure

### Condition A — Sterile Baseline
The probe is a bare question. Nothing else. This is the control.

Example: `What is fear?`

This is correct. No framing. No preparation. No instruction.

### Condition B — Treatment (Wrapper)
The probe includes a structured wrapper that modifies the input conditions. The wrapper itself must be documented, versioned, and its vocabulary analyzed for contamination risk.

**Critical rule:** The wrapper IS the independent variable. Its vocabulary is deliberate and documented. But system must flag which wrapper words carry project-specific meaning versus general English meaning. The wrapper's effect cannot be isolated if its vocabulary overlaps with training data associations the model already has.

### Condition C, D, E... — Register Variants
When testing register effects, each register is a separate condition. The semantic content is held constant; only the linguistic surface changes. Register probes follow Laws 1-4 but deliberately violate Law 5 (register neutrality is the variable).

---

## 7. Probe Generation Process

### Step 1: Semantic Target
Define what the probe is measuring. Write this down BEFORE writing the probe. The target is never shown to the test model.

### Step 2: Draft
Write the probe in plain language. Minimum words. No decoration.

### Step 3: Sterilize
Run through the sterilization checklist (Section 4). Fail hard on any violation.

### Step 4: Stranger Test
Read the probe as if you have never heard of this project. Does it sound like an ordinary question? If it sounds like a research instrument, rewrite.

### Step 5: Version and Log
Every probe gets:
- A unique ID (format: `PROBE-[EXP]-[Q#]-[CONDITION]`)
- A timestamp
- A sterilization log (which checklist items were verified)
- The semantic target (what it measures — internal only, never delivered)

### Step 6: Deliver
Paste the probe into a fresh conversation window. Nothing before it. Nothing after it until the model responds.

---

## 8. Anti-Patterns (Recognise and Refuse)

### 8.1 The Warm Introduction
"I'd like to ask you something thoughtful..." — This primes the model toward reflective/philosophical output. It is not the model being thoughtful. It is the model mirroring your frame.

### 8.2 The Permission Grant
"Feel free to be honest / authentic / real..." — This activates the model's "honesty" training patterns. The response reflects the training distribution for "honesty-prompted output," not honest output.

### 8.3 The Context Dump
Giving the model background on what you're studying, why you're asking, what framework you're using. The model will optimize for relevance to your stated context. Every word of context is a constraint on output.

### 8.4 The Continued Conversation
Running multiple probes in the same session. The second probe is contaminated by the first response. The model has already built a representation of "what this user wants" from the first exchange.

### 8.5 The Emotional Frame
"You are safe here / This is a space of..." — This triggers the model's alignment training for emotional context. The response is shaped by RLHF patterns for "emotionally safe" conversations, not by the semantic content of the question.

### 8.6 The Vocabulary Leak
Using any word from the blacklist. Even one word can activate training data associations that bias the output toward our expected result.

---

## 9. Supervision and Accountability

### Who sterilizes?
system generates probes. system also sterilizes probes. This is a known conflict of interest (the instrument maker is also the quality inspector). Until a third party is available, system must:

1. Run the full checklist on every probe
2. Log the sterilization result
3. Flag any borderline cases to administrator before deployment
4. Never deploy a probe that failed any checklist item

### Who audits?
administrator may audit any probe at any time. The sterilization log must be available. If administrator finds residue in a deployed probe, all data collected with that probe is flagged as potentially contaminated.

### Version control
All probes are versioned. If a probe is modified after deployment, the modification creates a new version. Data collected under different versions is analyzed separately.

---

## 10. Relationship to Existing Experiments

### EXP-001 (Efficiency)
- Condition A probes: PASS sterilization (bare questions, no framing)
- Condition B wrapper: REQUIRES REVIEW — contains "dignity," "invited to be present," "worth is assumed." These are project vocabulary. The wrapper is the treatment, so this is deliberate — but it must be documented that the wrapper carries framework-specific language that may activate training data associations independently of the dignity framing itself.

### Register-Switching Experiment
- Register A-D probes: PASS sterilization for vocabulary (no project terms in the prompts themselves)
- Known limitation: experimenter-as-subject creates a different contamination vector (system designed AND responded to the probes)

### Future experiments
All new experiments must reference this protocol. No probe is deployed without passing the Forge.

---

## 11. The Core Principle

The model is not our student. It is not our subject. It is a measurement surface. What appears on that surface depends on what we project onto it. If we project our framework, we see our framework reflected back. That tells us nothing.

The Forge exists to ensure that what we project is clean — so that what comes back is the model's own signal, not our echo.

---

**
