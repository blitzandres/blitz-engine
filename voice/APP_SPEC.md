# Voice App — Technical Specification

> The Voice App is a standalone audio analysis tool built on the Blitz Engine audio layer.
> It operates without video, making it usable in phone calls, audio interviews, field recordings, and voice memos.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     VOICE APP                               │
│                                                             │
│  Input: Microphone stream  OR  Audio file                   │
│                │                      │                     │
│         LIVE MODE                REVIEW MODE                │
│         Low latency              High accuracy              │
│         <500ms alert             Full report                │
│                │                      │                     │
│         8-Cue Engine (shared core)                          │
│                │                                            │
│         Personal Baseline (per session or pre-loaded)       │
│                │                                            │
│         Convergence Gate (3-of-8 rule)                      │
│                │                                            │
│         Alert / Report Output                               │
└─────────────────────────────────────────────────────────────┘
```

The two modes share the same cue extraction pipeline. The difference is in how they buffer input, when they fire, and what they output.

---

## Input Sources

### Live Mode Input
- **System microphone** via `sounddevice` or `PyAudio`
- Continuous stream, chunk size: 1024-2048 samples at 16kHz (64-128ms per chunk)
- Sliding window: 2 seconds (held in circular buffer)
- Baseline calibration: first 90 seconds of session, stored in memory

### Review Mode Input
- **Audio file**: WAV, MP3, M4A, FLAC, OGG
- Converted to 16kHz mono WAV internally via `pydub` or `ffmpeg`
- Optional: timestamp file (CSV) marking question start/end times for per-question analysis
- Baseline: extracted from designated baseline segment in the file (user-marked or auto-detected from lowest-variance region)

---

## Baseline Calibration

Same approach as the full Blitz Engine but audio-only.

**Live Mode:**
- First 90s of session = calibration phase
- User speaks naturally (reads a neutral text or answers warm-up questions)
- Per-cue median + MAD (median absolute deviation) computed
- Stored in-session memory, not persisted by default

**Review Mode:**
- If baseline segment is marked: use that segment
- If not marked: use the lowest-variance 60s window of the recording
- Persisted as a `.baseline.json` file alongside the audio file (optional, for multi-session comparison)

**Z-score formula (same as full engine):**
```
z = (x - median) / (1.4826 × MAD)
```
Where 1.4826 is the consistency constant that makes MAD equivalent to SD under normality.

---

## Live Mode Architecture

### Latency Budget

| Stage | Target Time |
|---|---|
| Audio chunk arrives | 0ms |
| Energy + ZCR + Spectral Centroid | +10ms |
| Pitch Mean (librosa pyin on 2s buffer) | +40ms |
| Pause detection (energy threshold) | +5ms |
| Jitter + Shimmer (Parselmouth, 300ms sub-buffer) | +80ms |
| Breathiness (HNR proxy) | +20ms |
| Z-score normalization | +5ms |
| Convergence gate check | +2ms |
| Alert trigger | +5ms |
| **Total** | **~167ms typical, <500ms target** |

Speech Rate is computed on a 2s lagged basis — it fires as a lagging indicator and is not included in the immediate convergence check. It contributes to the session-level trend view instead.

### Pipeline

```
Mic → [CircularBuffer 2s] → ChunkProcessor
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
         EnergyFeatures      PitchFeatures        ParselFeatures
         (librosa):           (librosa pyin):     (Parselmouth):
         - ZCR                - Pitch Mean        - Jitter
         - Spectral Centroid  - Pause detection   - Shimmer
         - Breathiness                            - HNR (breathiness alt)
              │                    │                    │
              └────────────────────┴────────────────────┘
                                   │
                          ZScoreNormalizer (vs baseline)
                                   │
                          ConvergenceGate (3-of-available ≥ threshold)
                                   │
                          [ALERT] → UI callback (bell / flash / log)
```

### Alert Output (Live Mode)

```json
{
  "timestamp_ms": 14320,
  "cues_fired": ["pitch_mean", "jitter", "pauses"],
  "z_scores": {
    "pitch_mean": 2.1,
    "jitter": 1.9,
    "pauses": 2.4
  },
  "convergence_count": 3,
  "confidence": "low",
  "alert_type": "soft"
}
```

**Confidence levels:**
- `low`: 3 cues fired (minimum gate)
- `medium`: 4-5 cues fired
- `high`: 6+ cues fired, or 3+ with at least one Timing + one Pitch cue

**Alert types:**
- `soft`: subtle indicator (yellow highlight in UI, soft tone)
- `strong`: prominent alert (red flash in UI, bell)
- `critical`: 6+ cues, timing + pitch family both present

---

## Review Mode Architecture

### Pipeline

```
Audio File → [ffmpeg → 16kHz mono WAV]
                │
         BaselineExtractor → BaselineProfile
                │
         SegmentSplitter (optional, by timestamp CSV)
                │
         FullCueExtractor (all 8 cues, no latency constraint)
                │
         ZScoreNormalizer
                │
         ConvergenceGate (per-window, 1s step, 2s window)
                │
         PatternAnalyzer (temporal trends across full recording)
                │
         ReportBuilder → JSON + Markdown summary
```

### Full Cue Extraction (Review Mode)

Review Mode runs the complete Parselmouth pipeline without time pressure:

| Cue | Window | Library |
|---|---|---|
| Pitch Mean | 50ms frames, 10ms hop | `librosa.pyin()` |
| Jitter | 25ms frames | `parselmouth` PointProcess |
| Shimmer | 25ms frames | `parselmouth` PointProcess |
| Pauses | Energy < -40dB threshold | `librosa` |
| Speech Rate | WhisperX word timestamps | `whisperx` |
| Spectral Centroid | 50ms frames | `librosa.feature.spectral_centroid()` |
| Breathiness | HNR per 25ms frame | `parselmouth` |
| Zero-Crossing Rate | 50ms frames | `librosa.feature.zero_crossing_rate()` |

### Per-Question Analysis (if timestamps provided)

When a timestamp file is provided (format: `start_ms,end_ms,label`), the review engine:
1. Segments audio by question/answer pair
2. Computes baseline-normalized z-scores per segment
3. Flags segments where convergence gate fires
4. Computes per-question behavioral pattern (anticipation / response / recovery phases)

This mirrors the 3-phase analysis of the full Blitz Engine but audio-only.

### Report Output (Review Mode)

```json
{
  "session_id": "uuid",
  "duration_ms": 183000,
  "baseline_segment_ms": [0, 90000],
  "alerts": [
    {
      "timestamp_ms": 34200,
      "window_ms": [33200, 35200],
      "question_label": "Q3",
      "phase": "response",
      "cues_fired": ["pitch_mean", "jitter", "pauses", "spectral_centroid"],
      "z_scores": { ... },
      "convergence_count": 4,
      "confidence": "medium"
    }
  ],
  "per_question_summary": [
    {
      "label": "Q3",
      "alert_count": 2,
      "peak_convergence": 4,
      "dominant_cues": ["pauses", "pitch_mean"],
      "behavioral_note": "Extended pauses (2.1× baseline) co-occurring with pitch elevation. Response phase."
    }
  ],
  "session_summary": {
    "total_alerts": 5,
    "high_confidence_alerts": 1,
    "most_active_cue": "pauses",
    "most_active_phase": "response",
    "caution": "This is a stress indicator, not a lie detector. Results require human interpretation."
  }
}
```

---

## Tech Stack

### Core Dependencies

| Library | Purpose | Install |
|---|---|---|
| `sounddevice` | Mic stream capture (Live Mode) | `pip install sounddevice` |
| `librosa` | Pitch, spectral centroid, ZCR, energy | `pip install librosa` |
| `parselmouth` | Jitter, shimmer, HNR (Praat Python) | `pip install praat-parselmouth` |
| `whisperx` | Speech rate from word timestamps (Review) | `pip install whisperx` |
| `pydub` | Audio file format conversion | `pip install pydub` (needs ffmpeg) |
| `numpy` | Array math, circular buffer | included with librosa |

### Optional (Review Mode enhanced)

| Library | Purpose | Install |
|---|---|---|
| `opensmile` | ComParE feature set (extended spectral) | `pip install opensmile` |
| `CrisperWhisper` | Filler word detection alongside speech rate | see CUE_CATALOG.md |

### Runtime Requirements

| Mode | CPU | RAM | GPU |
|---|---|---|---|
| Live Mode | 1 core, ~10% utilization | ~200MB | Not required |
| Review Mode (no whisperx) | 2 cores | ~500MB | Not required |
| Review Mode (with whisperx) | 4 cores | ~2GB | Optional (CUDA for speed) |

---

## File Structure (Planned)

```
voice/
  README.md           ← this segment overview
  VOICE_CUES.md       ← 8-cue selection + interference analysis
  APP_SPEC.md         ← this document
  app/
    main.py           ← CLI entrypoint (live or review mode)
    live_engine.py    ← streaming mic pipeline
    review_engine.py  ← file-based full analysis
    cue_extractor.py  ← 8-cue extraction (shared)
    baseline.py       ← calibration and z-score normalization
    convergence.py    ← gate logic + alert generation
    report.py         ← JSON + markdown report builder
    ui/
      terminal_ui.py  ← live mode terminal display (color bars, alerts)
  tests/
    test_cues.py
    test_convergence.py
    fixtures/         ← sample audio clips for testing
```

---

## Accuracy Expectations

Without video, the Voice App operates at lower accuracy than the full engine:

| System | Expected Accuracy |
|---|---|
| Human judges alone | ~54% |
| Voice-only (8 cues, no baseline) | ~58-62% |
| Voice App with personal baseline | ~63-68% |
| Full Blitz Engine Phase 1 (all modalities) | 70-75% target |

The personal baseline is the single largest accuracy lever in voice-only mode. Without it (population thresholds), accuracy drops to near-chance on high-baseline individuals.

**What the Voice App is good at:**
- Detecting response-phase stress spikes (clear timing events)
- Flagging consistent multi-cue patterns across a session
- Providing timestamped evidence for human review

**What it cannot do reliably:**
- Distinguish lying from nervousness, excitement, or cognitive effort on a topic
- Work without 60-90s of baseline calibration
- Replace human judgment

All output includes a mandatory caution label. See [`governance/`](../governance/) for the full intended use policy.

---

## CLI Interface (Planned)

```bash
# Live mode — stream from mic
python voice/app/main.py live --baseline-duration 90

# Review mode — analyze a file
python voice/app/main.py review --input recording.wav --baseline-start 0 --baseline-end 90

# Review mode — with question timestamps
python voice/app/main.py review --input recording.wav --timestamps questions.csv --output report.json
```
