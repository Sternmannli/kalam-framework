# KALAM Framework

A research toolkit for measuring how structured interaction frameworks affect AI system behaviour.

## What this is

KALAM provides tools, experiment protocols, and detectors for studying whether dignity-first design constraints produce measurable improvements in human-AI interaction. We measure output efficiency, noise reduction, and behavioural shifts across multiple AI systems.

**Early finding (EXP-001, Q3 pilot):** Structured interaction frameworks reduced output noise by 30.1% on average across 9 commercial AI systems. Effects varied dramatically by system — from 0% (Grok) to 49.5% (ChatGPT). [See experiment protocol →](experiments/EXP-001-PROTOCOL.md)

## Core concepts

- **The Gate Function** — a non-compensatory function D = A × L × M (Agency × Legibility × Moral Standing); any zero collapses D to zero and halts the system
- **The Confidence Scale** — five levels of evidential confidence (C1–C5)
- **The Three Markers** — Shadow Detection, Pronoun Adoption, Silence Quality
- **Drift Detection** — EWMA/CUSUM-based early warning for metric decline
- **Agency Scoring** — multidimensional agency measurement (Visibility × Affordability × Controllability × Understandability)

## Structure

```
kalam-framework/
├── detectors/           # NLP-based pattern detectors
│   ├── absurdity.py     # Absurdity detection (Camus, schema-violation theory)
│   ├── humour.py        # Humour detection (Benign Violation Theory)
│   └── love.py          # Love detection (Sternberg's Triangular Theory)
├── experiments/
│   ├── EXP-001-PROTOCOL.md  # Main experiment: framework efficiency
│   └── schema.py            # A/B experiment data schema
├── protocols/
│   └── UNIVERSAL_PROMPT.md  # The structured interaction prompt
├── tools/
│   ├── agency_score.py      # Multidimensional agency measurement
│   ├── drift_detector.py    # Early warning for metric decline
│   ├── pacing.py            # Module synchronization and stress management
│   ├── signing.py           # Ed25519 multi-signature for JSON manifests
│   ├── confidence.py        # Confidence scoring from frequency/diversity
│   ├── temporal_index.py    # Dual-track temporal reasoning
│   ├── similarity.py        # Structural similarity measurement
│   └── change_detector.py   # Change detection across versions
├── GLOSSARY.md
├── ROUTING.md
└── CONTRIBUTING.md          # How to contribute
```

## Quick start

```bash
git clone https://github.com/Sternmannli/kalam-framework.git
cd kalam-framework

# Run the experiment schema demo
python experiments/schema.py

# Run the absurdity detector
python detectors/absurdity.py

# Use the drift detector
python -c "
from tools.drift_detector import DriftDetector, DriftLevel
d = DriftDetector()
for s in [1.0, 0.95, 0.85, 0.7, 0.5, 0.3]:
    d.record(s, f'EX-{s}')
alert = d.check()
print(f'Level: {alert.level.value}, Rate: {alert.rate}')
"

# Use agency scoring
python -c "
from tools.agency_score import AgencyAmplifier
amp = AgencyAmplifier()
amp.measure('EX-001', V=0.9, F=0.3, C=0.8, U=0.7)
amp.measure('EX-002', V=0.8, F=0.2, C=0.9, U=0.6)
print(amp.report())
"
```

## Dependencies

**Core tools** (stdlib only — no install needed):
- `tools/agency_score.py`
- `tools/drift_detector.py`
- `tools/pacing.py`
- `tools/confidence.py`
- `experiments/schema.py`

**Detectors** (require ML libraries):
```bash
pip install sentence-transformers transformers torch scikit-learn numpy
```

**Signing tool:**
```bash
pip install pynacl
```

## Current experiment status

**EXP-001: Framework Efficiency** — Measures whether structured interaction frameworks reduce noise and improve efficiency across AI systems.

- **Design:** 10 systems × 10 questions × 2 conditions (with/without framework) = 200 runs
- **Completed:** 12/200 runs (Q3: "What is fear?")
- **Preliminary result:** Mean noise reduction +30.1% (meets 30% hypothesis threshold)
- **Systems tested:** Claude, ChatGPT, Grok, DeepSeek, Gemini, Copilot, Manus, Kimi, Euria, Perplexity

We need help collecting the remaining 188 runs. [See how to contribute →](CONTRIBUTING.md)

## Status

Active research. All findings carry a confidence level (C1–C5). Current findings sit at C2–C3. The experiment protocol, tools, and detectors are stable and tested.

## Authors

M. Farag and collaborators · 2024–2026

## Contact

info@kalam.ch

## License

Research use. See individual files for citations and theoretical grounding.
