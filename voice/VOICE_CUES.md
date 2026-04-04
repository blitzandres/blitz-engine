# Voice Cues — 8-Cue Low-Interference Selection

> This document covers the curated 8-cue set used by the Voice App.
> The full 13-cue audio catalog (including VOT shortening, formant dispersion, spectral tilt H1-H2, etc.) is in [`docs/CUE_CATALOG.md`](../docs/CUE_CATALOG.md).
> This file explains *why* these 8 were chosen and how they interact.

---

## Why 8 Cues, Not All 13

The full audio cue catalog has strong individual cues (VOT shortening at AUC 0.89, jitter+shimmer as strongest combined audio cue). But the goal of the Voice App is different from the full engine:

1. **Real-time extractability** — VOT shortening, formant dispersion, and spectral tilt (H1-H2) require heavier compute or multi-second context. They work in Review Mode but not Live Mode.
2. **Minimal interference** — using all 13 cues without family grouping causes double-counting (pitch + jitter + spectral tilt all respond to the same autonomic arousal pathway). The 8-cue set is chosen to cover different acoustic families with minimal overlap.
3. **Interpretability** — 8 independent signals are easier to explain and audit than 13 correlated ones.

The 8-cue set is also the minimum viable set for the 3-of-8 convergence gate to be statistically meaningful.

---

## The 8 Cues

### 1. Pitch Mean (F0 average)
**What it measures:** Average fundamental frequency in Hz over the analysis window.
**Stress pathway:** Vocal cord tension from anxiety causes F0 rise. Even 10-20 Hz increase is significant when compared to personal baseline.
**Library:** `librosa.yin()` or `pyin()` — real-time capable
**Mode:** Live + Review
**Acoustic family:** Pitch

---

### 2. Jitter (pitch cycle instability)
**What it measures:** Cycle-to-cycle variation in F0 (percent). Micro-wobble in pitch.
**Stress pathway:** Cognitive load makes laryngeal muscle control less stable. Captured at sub-perceptual level.
**Library:** `Parselmouth` (Praat Python binding)
**Mode:** Live + Review
**Acoustic family:** Pitch

> Note: Jitter and Pitch Mean are in the same family (both pitch-based) but measure different things — height vs stability. They have moderate interference (r ~0.3-0.4) and are treated as a grouped pair in fusion weighting. See [Interference Analysis](#interference-analysis) below.

---

### 3. Shimmer (amplitude cycle instability)
**What it measures:** Cycle-to-cycle variation in loudness/amplitude (percent).
**Stress pathway:** Respiratory and laryngeal muscle changes under stress cause volume micro-fluctuations independent of pitch changes.
**Library:** `Parselmouth`
**Mode:** Live + Review
**Acoustic family:** Amplitude

> Shimmer and Jitter together are the "voice tremor" composite — the strongest single audio indicator in the full catalog. In the 8-cue set they are kept separate so each can contribute independently to the convergence gate.

---

### 4. Pauses (silence duration + frequency)
**What it measures:** Length and frequency of low-energy segments (silences) in speech.
**Stress pathway:** Lying requires higher cognitive load (constructing, monitoring, maintaining). Extra thinking time shows up as longer or more frequent pauses. Strong timing-based cue.
**Library:** `librosa` energy envelope + silence splitting, or `WhisperX` word gaps
**Mode:** Live + Review
**Acoustic family:** Timing

---

### 5. Speech Rate (syllables/words per second)
**What it measures:** Overall speaking speed across the analysis window.
**Stress pathway:** Cognitive load typically slows speech. Some subjects speed up when delivering rehearsed lies. Either direction away from personal baseline is informative.
**Library:** `WhisperX` or `CrisperWhisper` word timestamps
**Mode:** Live + Review
**Acoustic family:** Timing

> Pauses and Speech Rate are in the same Timing family but measure different things — micro-gaps vs macro-speed. They have low-medium interference (r ~0.4) and are weighted as a grouped pair.

---

### 6. Spectral Centroid (voice brightness)
**What it measures:** Center of gravity of the frequency spectrum — how bright or harsh the voice sounds (Hz).
**Stress pathway:** Vocal tract tension shifts energy toward higher frequencies. Higher spectral centroid = more stressed, brighter, harsher tone.
**Library:** `librosa.feature.spectral_centroid()`
**Mode:** Live + Review
**Acoustic family:** Spectral/Tone Quality

---

### 7. Breathiness (high-frequency air noise ratio)
**What it measures:** Proportion of airy/aspirated sound in the voice (HNR proxy using high-frequency band energy).
**Stress pathway:** Anxiety affects vocal fold closure and airflow, producing a slightly breathier or more aspirated quality. Correlates with emotional arousal.
**Library:** `Parselmouth` HNR, or `librosa` high-band energy ratio
**Mode:** Live + Review
**Acoustic family:** Spectral/Tone Quality

> Breathiness and Spectral Centroid share the Spectral family (medium interference). They are grouped in fusion weighting.

---

### 8. Zero-Crossing Rate (waveform noisiness)
**What it measures:** How often the audio waveform crosses zero — a measure of high-frequency noise content.
**Stress pathway:** A tenser or more strained voice produces a noisier, less smooth waveform. Captures overall "roughness" without overlapping with pitch or volume cues directly.
**Library:** `librosa.feature.zero_crossing_rate()`
**Mode:** Live + Review
**Acoustic family:** Waveform/Noise

---

## Cue Family Summary

| Family | Cues | Interference within family |
|---|---|---|
| Pitch | Pitch Mean, Jitter | Medium (r ~0.3-0.4) |
| Amplitude | Shimmer | — (solo) |
| Timing | Pauses, Speech Rate | Low-medium (r ~0.4) |
| Spectral | Spectral Centroid, Breathiness | Medium (r ~0.4-0.5) |
| Waveform | Zero-Crossing Rate | Low with others |

Cross-family interference is low. Timing cues (Pauses, Speech Rate) have near-zero correlation with Pitch cues, which is the key reason this set was chosen.

---

## Interference Analysis

Interference (or overlap) happens when two cues measure the same underlying biological response — making them redundant rather than independent signals.

**Why it matters for the convergence gate:** If cues are heavily correlated, getting 3-of-8 to fire simultaneously is easy even from a single stress event, producing false positives. Independent cues mean the 3-of-8 gate actually requires 3 *different types* of stress leakage.

### Interference Table

| Cue | High interference with | Low interference with | Level |
|---|---|---|---|
| Pitch Mean | Jitter, Spectral Centroid | Pauses, Speech Rate | Medium |
| Jitter | Pitch Mean, Spectral Centroid | Shimmer, Pauses, Breathiness | Medium-High |
| Shimmer | (none significant) | Pitch Mean, Pauses, Zero-Crossing | Low-Medium |
| Pauses | Speech Rate | All pitch + spectral cues | Low |
| Speech Rate | Pauses | Pitch, Shimmer, Breathiness | Low |
| Spectral Centroid | Jitter, Breathiness | Pauses, Speech Rate, Zero-Crossing | Medium |
| Breathiness | Spectral Centroid, Jitter | Pauses, Speech Rate | Medium |
| Zero-Crossing Rate | Breathiness, Spectral Centroid | Pauses, Speech Rate, Pitch Mean | Low-Medium |

### Effective Dimensionality

With family grouping, this 8-cue set has ~5.5 effective independent dimensions (estimated from expected correlation structure). Without grouping, naively treating all 8 as independent would over-count. The Bayesian fusion layer applies family-level downweighting using:

```
effective_dim = trace(Σ) / λ_max(Σ)
```

(Same formula as the full engine — see [`planning/BLITZ_ENGINE_SPEC.md`](../planning/BLITZ_ENGINE_SPEC.md) Section 4.)

---

## Convergence Gate Design

Alert triggers when **≥ 3 of 8 cues** cross their z-score threshold simultaneously (within a 2-second window).

**Rule:** At least one Timing cue (Pauses or Speech Rate) AND at least one Pitch cue (Pitch Mean or Jitter) must be included in the triggered set. This prevents false alarms from pure vocal quality variation (e.g., someone with a naturally high-pitched excited voice).

**Weighting priority for fusion:**
1. Pauses + Speech Rate — most independent, highest weight
2. Shimmer + Zero-Crossing Rate — least correlated with other families
3. Pitch Mean + Jitter — moderate weight, grouped
4. Spectral Centroid + Breathiness — moderate weight, grouped

---

## Live Mode Cue Subset

For Live Mode (real-time streaming with <500ms latency target), heavier cues are deferred:

| Cue | Live Mode | Review Mode | Why deferred in Live |
|---|---|---|---|
| Pitch Mean | Yes | Yes | Fast with librosa |
| Jitter | Partial (300ms buffer) | Yes | Parselmouth needs 0.3s minimum |
| Shimmer | Partial (300ms buffer) | Yes | Same as jitter |
| Pauses | Yes | Yes | Energy-based, instant |
| Speech Rate | Lagged (2s window) | Yes | Needs speech segment |
| Spectral Centroid | Yes | Yes | Single frame operation |
| Breathiness | Yes | Yes | Band energy ratio, fast |
| Zero-Crossing Rate | Yes | Yes | Single frame operation |

In Live Mode, Jitter and Shimmer use a 300ms rolling buffer (slightly lagged but real-time compatible). The convergence gate in Live Mode requires **≥ 3 of the available cues** at any given moment (not all 8 may be ready simultaneously).
