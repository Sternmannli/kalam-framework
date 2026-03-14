# Contributing to KALAM Framework

We welcome contributions. Here are specific ways you can help right now.

## Open tasks (ordered by impact)

### 1. Run EXP-001 on AI systems we don't have access to

**Impact: HIGH** — This is the single most valuable contribution.

We're testing whether structured interaction frameworks reduce output noise across AI systems. We have 188 runs remaining.

**What you need:**
- Access to any of: Claude, ChatGPT, Grok, DeepSeek, Gemini, Copilot, Manus, Kimi, Euria, Perplexity (or any other system)
- 10 minutes per run

**How to do it:**
1. Read the [experiment protocol](experiments/EXP-001-PROTOCOL.md)
2. Pick a system and a question from the grid
3. Run the question twice: once normally (Condition A), once with the [Universal Prompt](protocols/UNIVERSAL_PROMPT.md) (Condition B)
4. Record: system name, question, word count A, word count B, and both full responses
5. Submit as a pull request adding your data to `experiments/data/`

**Data format:** See `experiments/schema.py` for the exact schema.

### 2. Validate drift detection on your own data

**Impact: MEDIUM** — Helps calibrate our early warning thresholds.

If you have time-series data from any monitoring system (not just AI), you can test our drift detector against it:

```python
from tools.drift_detector import DriftDetector

d = DriftDetector()
for score in your_time_series:
    d.record(score, exchange_id="your-id")
alert = d.check()
print(alert.level, alert.rate)
```

Report: does it detect real declines? Does it fire false positives? What thresholds work for your domain?

### 3. Test detectors on diverse text

**Impact: MEDIUM** — Our detectors are tested on English text. We need:

- Non-English text (does absurdity detection work across languages?)
- Domain-specific text (medical, legal, poetic)
- Edge cases that break the detectors

```python
from detectors.absurdity import detect
result = detect("your text here")
```

### 4. Review and improve the gate function

**Impact: HIGH (theoretical)** — The gate function D = A × L × M is the core of the framework. We need:

- Mathematical critique: is non-compensatory multiplication the right operator?
- Alternative formulations (geometric mean? weighted?)
- Edge case analysis: what happens at boundary values?

### 5. Port tools to other languages

**Impact: MEDIUM** — All tools are Python. Ports to JavaScript, Rust, or Go would broaden adoption.

Priority: `drift_detector.py` and `agency_score.py` (stdlib only, straightforward to port).

## How to submit

1. Fork the repository
2. Create a branch: `contrib/your-name/what-you-did`
3. Make your changes
4. Run existing examples to make sure nothing breaks
5. Submit a pull request with:
   - What you did
   - What you found
   - Your confidence level (C1–C5):
     - C1: Anecdotal (single observation)
     - C2: Repeated (seen multiple times)
     - C3: Systematic (controlled conditions)
     - C4: Validated (independent replication)
     - C5: Robust (survives adversarial testing)

## Code style

- Python 3.8+
- Type hints encouraged
- Docstrings required for public functions
- Prefer stdlib over external dependencies
- Each tool should be independently runnable (`python tool.py` should produce output)

## What we don't accept

- Changes that break existing experiment data compatibility
- Dependencies on proprietary services or APIs
- Code without documentation or examples
- Findings presented without confidence levels

## Questions?

Open an issue or email info@kalam.ch.
