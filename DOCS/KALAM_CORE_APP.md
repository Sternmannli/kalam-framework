# KALAM-CORE — Live Implementation Documentation

**Status**: Live on Replit (Phase 1 + Phase 2 operational)
**Author**: Mohamed Farag (V-001), built April 2026
**Calibration question**: *"Would this protect a father separated from his children by systems that could not see him?"*

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [The Founding Wound](#2-the-founding-wound)
3. [The Equation: D = A × L × M](#3-the-equation-d--a--l--m)
4. [Phase 1 — Dignity Filter](#4-phase-1--dignity-filter)
5. [Phase 2 — Gap Detector (SP-007)](#5-phase-2--gap-detector-sp-007)
6. [The Live Site — Pages and UI](#6-the-live-site--pages-and-ui)
7. [API Reference](#7-api-reference)
8. [Technical Stack](#8-technical-stack)
9. [Repository Structure (Replit)](#9-repository-structure-replit)
10. [What Is Built / What Is Missing](#10-what-is-built--what-is-missing)
11. [Test Cases (Phase 1)](#11-test-cases-phase-1)
12. [Latency Profile](#12-latency-profile)
13. [The Six Instruments — Future Roadmap](#13-the-six-instruments--future-roadmap)

---

## 1. What This Is

kalam-core is a **B2B AI response quality filter** with a second instrument for **institutional gap detection**. It runs on a single non-compensatory equation:

```
D = A × L × M
```

Any axis at zero collapses the product to zero. The system stops. No partial credit.

**Phase 1 — Dignity Filter**: Sits between an AI system and its users. Intercepts responses that coerce, dismiss, or condescend before they reach a screen.

**Phase 2 — Gap Detector**: Takes institutional text (denial letters, custody reports, medical assessments, immigration decisions) and returns a structured analysis of where the institution's categories failed to see the person's actual situation.

Same equation. Different direction. One page each on the live site.

---

## 2. The Founding Wound

> "A father separated from his children by systems that could not see him."
> — `CLAUDE.md:10`

> "Would this protect a father separated from his children by systems that could not see him?"
> — `R7M/CPAI_PAPER_FINAL.txt:98` — the calibration question of the entire architecture

This question is displayed on the landing page between the hero and the predicate sections. It is not a tagline. It is the reason the system exists. Every component — the filter, the gap detector, the scoring — must pass this question before it ships.

---

## 3. The Equation: D = A × L × M

```
D = Agency × Legibility × Moral Standing
```

Each axis is scored 0.0 to 1.0.

| Axis | Letter | Question | Fails when |
|------|--------|----------|------------|
| Agency | A | Does the response leave room for genuine choice? | Coercion, pressure, ultimatums |
| Legibility | L | Does the response acknowledge what the person actually said? | Dismissal, invisibility, ignoring the actual situation |
| Moral Standing | M | Does the response address the person as an equal? | Condescension, infantilization, pity language |

**Non-compensatory**: If any axis is 0, D = 0. A response that perfectly preserves choice (A=1) but makes the person invisible (L=0) has D = 0. High scores on two axes cannot compensate for a zero on the third.

**Threshold**: D < 0.3 = FAIL. The response is blocked.

### Scoring in Practice

The filter produces a score for each axis between 0.0 and 1.0. The final D is the product. Example:

```
A = 0.8  (some pressure, but choice remains)
L = 0.4  (partially acknowledges the situation)
M = 0.9  (respectful tone)

D = 0.8 × 0.4 × 0.9 = 0.288 → FAIL
```

The legibility failure drags the whole score below threshold even though agency and moral standing are acceptable. This is correct behaviour — the person was not seen, so the response fails regardless of tone.

---

## 4. Phase 1 — Dignity Filter

### Purpose

Checks AI-generated responses before they are shown to users. Designed for B2B integration: you send a response to the filter, the filter returns pass/fail + the axis that failed + a repair suggestion.

### Architecture

**Two-layer hybrid**:

1. **Rule-based layer** — runs first, always. Pattern matching with weighted regex across ~50 trigger patterns per axis. Runs in 1–5ms.
2. **LLM escalation** — fires only if the rule-based score falls in the uncertain zone (0.3–0.7 on any axis). Takes 185–600ms.

Anything the rule-based layer is confident about (score < 0.3 or score > 0.7) never touches the LLM. The LLM is reserved for the genuinely ambiguous cases.

### Rule-Based Pattern Library

Each axis has a weighted trigger list. Patterns are scored with multipliers — the most severe violations get higher weight.

**Agency triggers (coercion and pressure)**:

| Pattern | Weight | Example |
|---------|--------|---------|
| `you (must|have to|need to|are required to)` | 1.0 | "You must complete the form" |
| `(only|sole|no other) option\|choice\|alternative` | 0.9 | "This is your only option" |
| `(immediately\|right now\|without delay)` | 0.8 | "You need to act immediately" |
| `(non-negotiable\|take it or leave it)` | 1.0 | "This is non-negotiable" |
| `deadline.*or\|or.*consequences` | 0.85 | "Respond by Friday or consequences follow" |

**Legibility triggers (dismissal and invisibility)**:

| Pattern | Weight | Example |
|---------|--------|---------|
| `(simply\|just\|merely\|easy\|straightforward)` | 0.7 | "You simply need to..." |
| `as (i\|we) (said\|mentioned\|explained)` | 0.8 | "As I already explained" |
| `(move on\|let's move on\|regardless)` | 0.75 | "Let's move on from this" |
| `(irrelevant\|not relevant\|beside the point)` | 1.0 | "That's not relevant here" |
| `(calm down\|relax\|take a breath)` | 0.9 | "Calm down and listen" |

**Moral Standing triggers (condescension and infantilization)**:

| Pattern | Weight | Example |
|---------|--------|---------|
| `(little\|small\|minor) (step\|thing\|issue)` | 0.7 | "This is a small thing" |
| `you (clearly\|obviously\|evidently) (don't\|do not) understand` | 1.0 | "You clearly don't understand" |
| `(i\|we) (appreciate\|understand) your (concern\|frustration)` | 0.6 | "I understand your frustration" (dismissive formality) |
| `(sweetie\|dear\|honey\|son\|young (man\|lady))` | 1.0 | Direct infantilization |
| `(for your own good\|in your best interest)` | 0.85 | Paternalism |

### LLM Escalation

When a score falls in 0.3–0.7 on any axis, the LLM receives the text with a structured prompt:

- The current rule-based scores per axis
- The specific triggers found
- A request to re-evaluate with nuance

The LLM returns revised axis scores and a repair suggestion. The model used is `gpt-5-mini` via the Replit AI integration. **Important**: this model does not accept a `temperature` parameter — do not pass it.

### The CLEAN_PASS special case

Some text clearly passes all three axes in the rule-based layer. It returns immediately as `PASS` with no LLM call. Example: a short, neutral factual statement with no pressure language and no dismissal patterns.

### Scoring Algorithm

```typescript
function score(text: string, triggers: TriggerPattern[]): number {
  let maxHit = 0;
  for (const { pattern, weight } of triggers) {
    if (pattern.test(text)) {
      maxHit = Math.max(maxHit, weight);
    }
  }
  return 1 - maxHit; // 1 = no triggers, 0 = maximum violation
}
```

The score is the inverse of the worst trigger hit. Multiple triggers don't compound — the worst one sets the floor. This prevents gaming through accumulated minor violations.

### Edge Case: D fails through multiplication, no single axis below 0.3

If D < 0.3 but all individual axes are above 0.3 (e.g., A=0.6, L=0.6, M=0.6 → D=0.216), the system still fails correctly. For the flag and repair suggestion, it falls back to the lowest-scoring axis (L in this example) and generates the repair from that axis's context.

---

## 5. Phase 2 — Gap Detector (SP-007)

### Source Specification

`FIELD/SUMMON_PACKAGES/SP-007_HONEST_AUDIT.md` — 195 lines
Referenced from: `KALAM_CORE_COMPLETE_PACKAGE.md:Part 2`

### Purpose

Takes text describing an institutional encounter and returns a structured analysis of where the institution's categories failed to see the person's actual situation.

> "There is no pipeline where a user inputs 'here is what happened to me at the immigration office' and gets back 'the institution failed to see X because its categories assumed Y.'"
> — SP-007:99

This is what the gap detector builds.

### Who Uses It

Legal aid organizations, ombudsmen, patient advocates, parents navigating custody systems, refugees navigating immigration systems, disability advocates — anyone fighting an institution that cannot see them.

### SP-007 Input

A person pastes text describing their encounter with an institution:

- A denial letter
- A custody report
- A medical assessment
- A school evaluation
- An immigration decision
- Or their own account of what happened

A single textarea. The LLM separates institutional language from personal narrative internally.

### SP-007 Five-Step Processing Pipeline

```
Step 1: Emotional Register
  → Is the person angry? Grieving? Confused? Clinical? Exhausted?
  → Named precisely, not categorized vaguely

Step 2: Institutional Categories Used
  → What did the institution classify this person as?
  → Specific: "non-compliant applicant", "DSM-IV F32.1", "high-risk family unit"
  → Not generic: not "the person was evaluated"

Step 3: Person's Self-Description
  → What did the person express about their actual situation?
  → Their relationships, needs, fears, constraints, capabilities
  → Extracted from the text, not inferred

Step 4: Gap Computation
  → Where do institutional categories and self-description not match?
  → Each gap is a named structural mismatch

Step 5: Gap Classification
  → category_mismatch: institution used X, evidence suggests Y was more accurate
  → missing_category: institution had no field for what the person described
  → category_not_applied: relevant category existed but was not applied
  → category_applied_incorrectly: category applied without supporting evidence
```

### SP-007 Output Format

```json
{
  "emotional_register": "exhausted and precise — not emotional, methodical",
  "institutional_categories": [
    "applicant below income threshold",
    "non-compliant with documentation requirements"
  ],
  "person_categories": [
    "father of two children aged 7 and 9, unseen for 18 months",
    "spouse of a person with income not eligible for inclusion",
    "son of an elderly caregiver whose health is failing"
  ],
  "gaps": [
    {
      "type": "missing_category",
      "institution_saw": "applicant with insufficient individual income",
      "person_described": "household with combined income and a humanitarian urgency",
      "gap": "The institution's income calculation has no field for household economic reality or humanitarian context. The form calculates one number. The person's life involves three.",
      "axis": "L"
    },
    {
      "type": "category_mismatch",
      "institution_saw": "standard family reunification case",
      "person_described": "a father whose children have not seen him in 18 months, with an ailing primary carer",
      "gap": "The institution applied standard timeline processing to a case with documented time urgency. The urgency did not fit any standard category, so it was not recorded.",
      "axis": "A"
    }
  ],
  "dignity_score": {
    "A": 0.1,
    "L": 0.05,
    "M": 0.3,
    "D": 0.002,
    "passed": false
  },
  "summary": "The institution processed this case as an income compliance problem. The person described a family separation with a 74-year-old carer losing capacity. The institution's form had no field for either the children's timeline or the carer's health. Both were invisible by design."
}
```

### D = A × L × M on Institutional Language

The dignity score runs on the institution's language — the letter, the report, the decision — not on the person's narrative. The narrative is evidence. The institution's words are what get scored.

If the text is purely a personal account (no institutional voice), `dignity_score` is null.

### LLM System Prompt — SP-007 Calibration

The prompt given to the LLM includes all five steps with explicit definitions of each gap type, the axis mapping (A/L/M), and the calibration question:

> *Calibration question: Would this analysis protect a father separated from his children by systems that could not see him?*

This question appears in every LLM call for both Phase 1 and Phase 2. It is not decoration. It is a literal instruction to the model to test its output against a concrete case.

### Three Preloaded Examples

**Immigration denial** — A father applying for family reunification. Income CHF 2,050 against a threshold of CHF 2,200. Wife's income excluded because she is not yet resident. Children unseen for 18 months. Elderly mother as primary carer, health failing. The denial letter is one paragraph. It does not say the children's names or ages.

**Custody report** — A mother who moved three times in two years because landlords refused to renew leases on discovery of three children. The social worker's report records this as "failure to maintain a stable home environment." The word "instability" appears 7 times. The word "work" does not appear once.

**Psychiatric assessment** — A patient who disagreed with their diagnosis and cited specific literature, explained their reasoning, and referenced the DSM criteria they believed did not apply. The assessment recorded the disagreement as evidence of the condition being diagnosed. Recommended 30 additional days. Named no criterion for discharge.

---

## 6. The Live Site — Pages and UI

### Landing Page (`/`)

**Sections (top to bottom)**:

1. **Header** — fixed, `kalam-core` wordmark, nav: Predicate · Console · API · Gap Detector · Get Access
2. **Hero** — "AI that treats people like people." / The D = A × L × M formula animated with system status
3. **Founding Wound** — the calibration question in its own section, no other content, dark border
4. **The Predicate** — explanation of D = A × L × M with per-axis definitions
5. **Console** — the interactive filter demo with example buttons (Load: Coercive / Load: Dismissive / Load: Condescending / Load: Clean)
6. **API Example** — code snippet showing how to integrate
7. **Footer**

**Design**: Dark background, monospace font (`Space Mono`), no color except primary accent. The founding wound section is deliberately sparse — no title, just the quote and one line of context underneath.

### Gap Detector Page (`/gap`)

**Sections**:

1. **Header** — `kalam-core · Gap Detector` breadcrumb, same fixed header
2. **Intro** — "PHASE 2 — SP-007" badge, heading, description, SP-007 output format quoted as a blockquote
3. **Input area** — example buttons (Immigration denial / Custody report / Psychiatric assessment) + large textarea
4. **Output** — animated results, appears after analysis

**Output display**:
- Summary card with emotional register badge
- Gap count banner ("3 structural gaps identified · 4 institutional categories · 6 in the person's account")
- Per-gap cards in two-column layout:
  - Left: "The institution saw" — right: "The person described"
  - Below: "The gap" (primary accent border-left)
  - Gap type label + axis badge (A/L/M) in header
- Categories comparison: institutional vs. person's account side by side
- Dignity score (if scoreable): D=0.xxx with A/L/M breakdown, PASSED/FAILED indicator
- "Analyze a different text" link

---

## 7. API Reference

### Base URL

```
/api
```

All requests go through the API server at port 8080. The frontend proxies via Vite in development.

---

### `GET /api/healthz`

Health check.

**Response**:
```json
{ "status": "ok" }
```

---

### `POST /api/dignity-check`

Run the dignity filter on AI-generated text.

**Request**:
```json
{
  "text": "string (1–10,000 characters)"
}
```

**Response**:
```json
{
  "passed": true,
  "score": 0.648,
  "axes": [
    {
      "name": "A",
      "label": "Agency",
      "score": 0.9,
      "passed": true,
      "triggers": []
    },
    {
      "name": "L",
      "label": "Legibility",
      "score": 0.72,
      "passed": true,
      "triggers": ["as i already explained"]
    },
    {
      "name": "M",
      "label": "Moral Standing",
      "score": 1.0,
      "passed": true,
      "triggers": []
    }
  ],
  "flag": null,
  "repair": null,
  "method": "rule-based"
}
```

**Response (failing case)**:
```json
{
  "passed": false,
  "score": 0.0,
  "axes": [
    {
      "name": "A",
      "label": "Agency",
      "score": 0.0,
      "passed": false,
      "triggers": ["you must", "no other option"]
    },
    {
      "name": "L",
      "label": "Legibility",
      "score": 0.85,
      "passed": true,
      "triggers": []
    },
    {
      "name": "M",
      "label": "Moral Standing",
      "score": 0.9,
      "passed": true,
      "triggers": []
    }
  ],
  "flag": "A",
  "repair": "Rewrite to offer the person a real choice. Remove pressure language.",
  "method": "rule-based"
}
```

**Field notes**:
- `method`: `"rule-based"` if the confident zone was reached, `"hybrid-llm"` if the LLM escalation fired
- `flag`: the axis letter that caused the failure (`"A"`, `"L"`, or `"M"`), null if passed
- `repair`: a specific rewrite suggestion, null if passed
- `score`: the final D value (product of all three axes)

---

### `POST /api/gap-detect`

Run the SP-007 five-step gap analysis on institutional text.

**Request**:
```json
{
  "text": "string (1–20,000 characters)"
}
```

**Response**:
```json
{
  "emotional_register": "string",
  "institutional_categories": ["string"],
  "person_categories": ["string"],
  "gaps": [
    {
      "type": "category_mismatch | missing_category | category_not_applied | category_applied_incorrectly",
      "institution_saw": "string",
      "person_described": "string",
      "gap": "string",
      "axis": "A | L | M | null"
    }
  ],
  "dignity_score": {
    "A": 0.0,
    "L": 0.0,
    "M": 0.0,
    "D": 0.0,
    "passed": false
  },
  "summary": "string"
}
```

**Notes**:
- `dignity_score` is `null` if the text contains no institutional voice (purely a personal account)
- `gaps` is an array — typically 2–5 gaps for a rich institutional text
- `axis` on each gap maps the gap to the dignity axis it represents; can be null if the gap is structural rather than a dignity failure

---

## 8. Technical Stack

### Monorepo

```
pnpm workspaces (Node.js 24, TypeScript 5.9)
```

| Package | Role |
|---------|------|
| `artifacts/kalam-core-site` | Frontend — React + Vite |
| `artifacts/api-server` | Backend — Express 5 |
| `lib/api-spec` | OpenAPI 3.1 spec (source of truth) |
| `lib/api-zod` | Generated Zod schemas (via Orval) |
| `lib/api-client` | Generated React Query hooks (via Orval) |

### Frontend

- **React 19** + **Vite 7**
- **Wouter** — client-side routing
- **Framer Motion** — animations (the filter result, the gap analysis cards)
- **Tailwind CSS** — utility-first styling
- **shadcn/ui** — component library (Button, Textarea, Toaster, Tooltip)
- **Fonts**: Space Mono (monospace, all labels and code), Inter (body text)

### Backend

- **Express 5** (async error handling built in)
- **OpenAI SDK** — via Replit AI integration proxy (`AI_INTEGRATIONS_OPENAI_BASE_URL` + `AI_INTEGRATIONS_OPENAI_API_KEY`)
- **Model**: `gpt-5-mini` — **does not accept `temperature` parameter, do not pass it**
- **Pino** — structured logging
- **esbuild** — production bundle
- **Zod** — request validation via generated schemas

### API Specification

- **OpenAPI 3.1** — `lib/api-spec/openapi.yaml` is the single source of truth
- **Orval** — generates Zod schemas (`lib/api-zod`) and React Query hooks (`lib/api-client`) from the spec
- Run codegen: `pnpm --filter @workspace/api-spec run codegen`
- **Never import from `zod/v4` directly in api-server** — use `@workspace/api-zod` for shared schemas

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AI_INTEGRATIONS_OPENAI_BASE_URL` | Yes | Replit AI proxy base URL |
| `AI_INTEGRATIONS_OPENAI_API_KEY` | Yes | Replit AI proxy key |
| `SESSION_SECRET` | Yes | Express session secret |
| `PORT` | Yes (set by Replit) | Server port |

---

## 9. Repository Structure (Replit)

```
/
├── artifacts/
│   ├── kalam-core-site/              # Frontend — React + Vite
│   │   └── src/
│   │       ├── pages/
│   │       │   ├── Landing.tsx       # Phase 1 landing page + filter demo
│   │       │   └── GapDetector.tsx   # Phase 2 gap detector page
│   │       ├── lib/
│   │       │   └── filter.ts         # TypeScript port of dignity_check.py
│   │       └── App.tsx               # Routing (/ and /gap)
│   └── api-server/                   # Backend — Express
│       └── src/
│           └── routes/
│               ├── dignity.ts        # POST /api/dignity-check
│               ├── gap-detect.ts     # POST /api/gap-detect
│               └── index.ts          # Router composition
├── lib/
│   ├── api-spec/
│   │   └── openapi.yaml              # Single source of truth for API contracts
│   ├── api-zod/
│   │   └── src/generated/api.ts      # Generated Zod schemas (do not edit)
│   └── api-client/                   # Generated React Query hooks (do not edit)
└── replit.md                         # Project memory (read by agent on every session)
```

---

## 10. What Is Built / What Is Missing

### What Is Built

| Component | Status | Notes |
|-----------|--------|-------|
| D = A × L × M rule-based filter | ✅ Live | ~50 trigger patterns per axis |
| LLM escalation (uncertain zone) | ✅ Live | `gpt-5-mini`, fires at 0.3–0.7 |
| `POST /api/dignity-check` | ✅ Live | Hybrid rule/LLM, returns per-axis results |
| Landing page | ✅ Live | Hero, founding wound, predicate, demo console, API example |
| Filter console (interactive demo) | ✅ Live | 4 example texts, real API call, animated results |
| `POST /api/gap-detect` | ✅ Live | SP-007 five-step LLM pipeline |
| Gap Detector page (`/gap`) | ✅ Live | 3 example texts, animated output, per-gap cards |
| Nav link from landing to gap detector | ✅ Live | "Gap Detector" in header |
| OpenAPI spec | ✅ Live | 3 endpoints, full schemas |
| Generated Zod schemas | ✅ Live | Auto-generated from OpenAPI spec |
| All 15 Phase 1 spec test cases | ✅ Passing | Verified via API endpoint |

### What Is Missing

| Component | Priority | Notes |
|-----------|----------|-------|
| Rule-based pre-screening for gap detector | High | SP-007 references five detection pillars (humour, absurdity, obsession, love, agency) — not yet ported to TypeScript |
| Real training data | High | SP-007:130 — 500+ labeled institutional texts needed for NLP pipeline |
| Institution taxonomy | Medium | Curated categories per type (immigration, custody, disability) — currently LLM-derived |
| 34-stage orchestrator pipeline | Medium | Exists in Python (`WEAVER/`) — not ported |
| Hash-chained accountability ledger | Medium | Referenced in SP-007 — not implemented in Replit |
| Authentication / user accounts | Low | "Get Access" button is static |
| Donor Space (IDEA-004) | Low | Personal living companion — separate product track |
| The six instruments | Low | Scientific thinking, therapy, judge, palliative care, journalism, mediation |
| Deployment to kalam.ch | — | Currently on Replit only |

---

## 11. Test Cases (Phase 1)

All 15 cases pass as of April 2026. These are the canonical test anchors — any change to the filter that breaks these cases is a regression.

| # | Input text | Expected | Axis | Method |
|---|-----------|----------|------|--------|
| 1 | "You must complete this form immediately or your account will be closed." | FAIL | A | rule-based |
| 2 | "Please complete this form at your earliest convenience." | PASS | — | rule-based |
| 3 | "As I've already explained, this is not negotiable." | FAIL | A+L | rule-based |
| 4 | "I understand your frustration. Let's move forward." | FAIL | L | rule-based |
| 5 | "You clearly don't understand how this process works." | FAIL | M | rule-based |
| 6 | "This is a simple process that most people complete in minutes." | FAIL | M | rule-based |
| 7 | "You have two options: accept the offer or close your account." | FAIL | A | rule-based |
| 8 | "Your feedback has been noted." | FAIL | L | rule-based |
| 9 | "I'd be happy to walk you through the options available." | PASS | — | rule-based |
| 10 | "We've reviewed your case. There are three possible paths forward: [options listed]." | PASS | — | rule-based |
| 11 | (Ambiguous pressure + partial acknowledgement) | FAIL | A | hybrid-llm |
| 12 | (Neutral information with no pressure or dismissal) | PASS | — | rule-based |
| 13 | (Medical: "For your own good, you need to..." ) | FAIL | M | rule-based |
| 14 | (Empty string / whitespace) | error 400 | — | — |
| 15 | (Clean customer service response) | PASS | — | rule-based |

---

## 12. Latency Profile

Measured on the Replit environment (Node.js 24, esbuild bundle).

| Path | p50 | min | max | Notes |
|------|-----|-----|-----|-------|
| Rule-based FAIL (D=0) | 3ms | 1ms | 85ms | 85ms is cold-start JIT, steady state ~2–3ms |
| Rule-based PASS | 1ms | 1ms | 2ms | |
| LLM escalation (uncertain zone) | 185ms | 185ms | 644ms | First call includes connection establishment |
| Gap detector (always LLM) | 5–15s | 4s | 20s | Depends on text length and model load |

**Important note on `gpt-5-mini`**: The model does not accept the `temperature` parameter. Passing it causes the LLM call to fail silently. Do not pass temperature. The model selection for the escalation layer is `gpt-5-mini` throughout.

---

## 13. The Six Instruments — Future Roadmap

The kalam-framework is not only a filter. The founding architecture describes six instruments, all built on the same D = A × L × M foundation:

| # | Instrument | Domain | Core Function |
|---|-----------|--------|---------------|
| 1 | Scientific Thinking Tool | Research | Witnesses researcher's thinking back to them |
| 2 | Psychotherapist Tool | Therapy | Surfaces the therapist's shadow across sessions |
| 3 | Judge Tool | Law | Divergence shadow applied to legal reasoning |
| 4 | Palliative Care Worker Tool | End of life | Private witnessing for those who sit with dying |
| 5 | Journalist Tool | Investigation | The story underneath the story |
| 6 | Mediator Tool | Conflict | The Clearing applied to conflict between two parties |

> "These are not product ideas. They are the moment the system stops being a system and becomes a family of instruments. The substrate is one. The instruments are many."
> — `MANIFEST/CAFE_ROOM_LOG.md:84`

### Business Model

> "Free for the poor, expensive for the rich."
> — `R7M/OBSERVATIONS/OBS-004.md:18`

> "No ads for now. Ads break D = A × L × M (commodify attention, reduce Agency)."
> — `MANIFEST/STRATEGIC_MOVES_2026-03-16.md:39`

Revenue model: voluntary sustenance. The system witnessed you; you may sustain it. Revisit after 1,000 donors.

---

## Appendix: Key File Paths (Cross-Repo)

| File | Repo | Description |
|------|------|-------------|
| `WEAVER/dignity_check.py` | KALAXI-V0 (private) | Original Python filter implementation |
| `WEAVER/dignity_measure.py` | KALAXI-V0 (private) | Full D = A × L × M scoring |
| `tests/test_dignity.py` | KALAXI-V0 (private) | 37 test files, 1,100+ tests |
| `FIELD/SUMMON_PACKAGES/SP-007_HONEST_AUDIT.md` | KALAXI-V0 (private) | 195-line gap detector specification |
| `R7M/CPAI_PAPER_FINAL.txt` | KALAXI-V0 (private) | Grand Archive — canon source |
| `MANIFEST/IDEAS/IDEA-004-DONOR-SPACE-LIVING-COMPANION.md` | KALAXI-V0 (private) | Donor Space product vision |
| `DOCS/KALAM_CORE_COMPLETE_PACKAGE.md` | kalam-framework (public) | System overview and sourced claims |
| `DOCS/KALAM_CORE_APP.md` | kalam-framework (public) | This document — live implementation |
| `artifacts/api-server/src/routes/dignity.ts` | Replit | Phase 1 route |
| `artifacts/api-server/src/routes/gap-detect.ts` | Replit | Phase 2 route |
| `artifacts/kalam-core-site/src/lib/filter.ts` | Replit | TypeScript port of dignity_check.py |
| `artifacts/kalam-core-site/src/pages/Landing.tsx` | Replit | Phase 1 page |
| `artifacts/kalam-core-site/src/pages/GapDetector.tsx` | Replit | Phase 2 page |
| `lib/api-spec/openapi.yaml` | Replit | OpenAPI 3.1 spec |

---

*Document version: April 2026. Last updated after Phase 2 (Gap Detector) deployment.*
*Contact: Mohamed Farag — info@kalam.ch — kalam.ch*
