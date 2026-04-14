# Blitz Engine — Quick Start

> Status: text-first MVP implemented. Video/audio APIs below are still planned.

---

## Installation

```bash
pip install -e .
```

## Requirements

- Python 3.10+
- Video with face at 480p+ minimum, 720p+ recommended
- 90-180 seconds of neutral baseline footage from the same subject
- Front-facing camera, consistent lighting

---

## Basic Usage (Implemented Now)

```python
from blitz_engine import BlitzEngine

# Current MVP supports linguistic cues only.
engine = BlitzEngine(
    modalities=["linguistic"],
    prior=0.30,
    convergence_threshold=0.65
)

# Start a session with baseline text samples
session = engine.new_session(
    baseline_texts=[
        "I drove to work and grabbed coffee before the meeting.",
        "My usual breakfast is eggs, toast, and tea at home.",
        "Last weekend I cleaned the apartment and watched a movie.",
        "I usually walk to the store in the afternoon for groceries.",
        "My morning routine starts with stretching and checking messages.",
    ],
    baseline_duration_s=120,
    consent=True,
    use_case="research",
    jurisdiction="CA-US"
)

# Check baseline quality
print(session.baseline.quality_report())
# {"duration_s": 120.0, "is_sufficient": True, ...}

# Analyze a response text
result = session.analyze_text(
    response_text="Honestly, I really do not know, um, I was basically with someone at that place.",
    question="Where were you on Tuesday night?"
)

print(result.risk_score)
print(result.uncertainty)
print(result.channel_contributions)
print(result.narrative)
print(result.compliance["not_for_sole_decision"])
```

## Planned Next

- audio cue extraction from files
- visual cue extraction from frames
- multi-modal convergence that can actually satisfy the 2-family gate
- local API adapter

## CLI (Implemented Now)

```bash
blitz analyze-text \
  --baseline-file baseline.txt \
  --response-file response.txt \
  --question "Where were you Tuesday night?" \
  --response-latency-ms 900 \
  --output report.json
```

`baseline.txt` should contain one neutral baseline sample per line. The CLI writes a stable JSON report to stdout or to `--output`.

---

## Understanding the Output

### risk_score

`0.0 to 1.0` — posterior probability that the behavioral pattern is consistent with deception.

- `< 0.40` — No meaningful signal
- `0.40 - 0.55` — Weak signal, below convergence threshold
- `0.55 - 0.70` — Moderate, worth attention
- `> 0.70` — Elevated, 2+ modality families active

**A score of 0.72 does not mean someone is 72% likely to be lying. It means observed behavioral patterns are at the 72nd percentile of patterns associated with deception in the literature.**

### uncertainty

Half-width of the 90% confidence interval. A score of `0.72 ± 0.15` means the true posterior is likely between 0.57 and 0.87.

High uncertainty means: more baseline footage needed, or video quality is poor.

### channel_contributions

Per-modality signal strengths. If one modality is missing (rPPG failed due to compression), others still contribute.

### top_cues

The CueEvents that drove the score highest. Each includes:
- `cue_id` — which cue fired
- `fired_at_ms` — when
- `phase` — anticipation / response / recovery
- `z_score` — how many robust standard deviations above personal baseline
- `on_word` — the specific word that triggered it (if applicable)

---

## The Convergence Gate

Blitz Engine will NOT raise a flag unless:
1. Posterior probability > 0.65 (configurable)
2. At least 2 independent modality families are active

A high audio score alone is not enough. Voice tremor + gaze aversion + pronoun avoidance = meaningful signal. Voice tremor alone = noise.

---

## Baseline Guide

The 90-180s baseline is critical. Without it, the engine uses population thresholds — which are brittle and produce false positives for anxious individuals.

**Good baseline prompts:**
- "Tell me about your commute today"
- "Describe your favorite meal"
- "What's your typical morning routine?"

**Avoid:**
- Emotionally loaded topics (even positive ones)
- Yes/no questions (need sustained speech)
- Topics the person might be embarrassed about

**Required: At least 2 different neutral topics in the baseline.**

---

## REST API (planned — Phase 2)

```bash
# Start a session
curl -X POST http://localhost:8000/session/new \
  -H "Content-Type: application/json" \
  -d '{
    "baseline_video_b64": "...",
    "consent": true,
    "use_case": "research",
    "jurisdiction": "CA-US"
  }'

# Analyze a clip
curl -X POST http://localhost:8000/session/{id}/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "video_clip_b64": "...",
    "question": "Where were you on Tuesday?"
  }'
```

---

## CLI (planned — Phase 2)

```bash
# Analyze a full interview video
blitz analyze \
  --baseline baseline_90s.mp4 \
  --video interview.mp4 \
  --questions questions.txt \
  --output report.json
```

---

## Ethics Notice

Every time you use Blitz Engine, remember:

- Accuracy: 70-75%
- False positive rate: ~25-30%
- `not_for_sole_decision` is always `true`
- Consent is required. Always.

See [../governance/ETHICS.md](../governance/ETHICS.md).
