# Lie Detector — Accuracy Plan
> Low error rate strategy, March 2026

---

## Honest Accuracy Ceiling (Updated)

| System | Accuracy | Notes |
|---|---|---|
| Human unaided | 54% | Bond & DePaulo 2006, 24,483 judges |
| SVC 2025 winner (cross-domain) | 62.44% | Best real-world published result |
| Cross-domain benchmark best | ~60-69% | Depends on domain split |
| **Our realistic target** | **68-72%** | With quality gating + baseline calibration + abstain option |
| With thermal (Phase 3) | ~83-87% | Controlled conditions only |

**Key insight:** Low-70s is achievable only with:
- Good A/V quality (720p+, stable face, clean audio)
- An abstain option (don't force a binary verdict on bad footage)
- Robust baseline normalization per session
- Quality-aware cue weighting

Without those three, forced binary scoring drifts to 55-65%.

---

## Cue Reliability Under H.264 Compression

Ranked by how well each modality survives YouTube/news video compression:

```
1. Linguistic / semantic  — compression-immune (text only)
2. Coarse prosody         — mostly survives (pitch, pauses, fillers)
3. Head/body gross motion — survives at any resolution
4. Coarse facial AUs      — degrades moderately (AU20/23/24 ok, microexpressions degrade)
5. Fine AUs / micro-exp   — degrades 2-4x (needs high bitrate)
6. rPPG heart rate        — first to fail under compression + motion (treat as bonus only)
```

**Action:** Fine AUs and rPPG need explicit quality gates. If video quality score < 0.6, suppress rPPG entirely and halve fine AU weights.

---

## LLM Scoring Validity

Research finding (2025): fine-tuned BERT outperforms zero/few-shot LLM prompting for deception text classification. LLMs near chance in zero-shot on raw text.

**But our approach is different** — we send structured numerical features (z-scores, timing, magnitude), not raw text. This is closer to a rubric-following task than classification. Claude's value is:
- Context-aware weighting (knows the question + which word triggered the cue)
- Contradiction handling
- Abstain logic
- Cross-cue pattern recognition

The rubric-driven JSON prompt below addresses the zero-shot weakness. Self-consistency (3 passes, take median) addresses variance.

---

## Architecture: What Happens Before Claude

### Step 1: Quality Gates

Per cue, compute `quality_gate_status`:

| Condition | Status | Effect |
|---|---|---|
| Face too small / occluded | suppress | multiply by 0 |
| Head pose > 25° | downweight | multiply by 0.5 |
| fps < 24 | downweight rPPG/blink | multiply by 0.3 |
| Video bitrate < 500kbps | downweight fine AUs + rPPG | multiply by 0.2 |
| Audio SNR < 15dB | downweight vocal cues | multiply by 0.5 |
| ASR word confidence < 0.7 | downweight linguistic | multiply by 0.6 |

Compute `overall_quality_score = weighted average of all gate outcomes (0-1)`. If < 0.45, output abstain without calling Claude.

### Step 2: Baseline Normalization

Collect 30-90s neutral baseline at session start (subject talking normally, no stress topic).

Per cue, compute robust z-score:
```
z = (x - median_baseline) / (1.4826 * MAD_baseline + ε)
clip to [-4, 4]
```

Use MAD (median absolute deviation) not std — less sensitive to outlier frames.

If baseline segment is unstable (high variance), reduce confidence for that session globally.

Add slow EWMA drift correction for long sessions (lighting/pose drift over time).

### Step 3: Temporal Features

Don't just send point values. Send per-cue:
- `raw_value`
- `baseline_robust_z`
- `magnitude_norm` (clamped 0-1)
- `direction` (+1/-1/0)
- `duration_ms` of the event
- `timing.phase` — which window relative to the answer:

| Phase | Window | Diagnostic Weight |
|---|---|---|
| pre | t0 - 1.0s to t0 | 1.05 — anticipatory stress |
| onset | t0 to t0 + 2s | 1.20 — highest signal |
| mid | t0 + 2s to t0 + 6s | 1.00 — standard |
| late | t0 + 6s onwards | 0.75 — cognitive load/fatigue confound |
| post | end to end + 1.5s | 0.90 — release/rebound |

- `anchor_word` — the specific word the cue fired on (most valuable if it fired mid-answer on a key claim)

---

## Cue Catalog — Default Weights

| cue_id | modality | base_weight | direction | quality_sensitive | rationale |
|---|---|---|---|---|---|
| `au1_inner_brow_raise` | facial | 0.30 | +1 | yes | Concern/cognitive load, weak alone |
| `au2_outer_brow_raise` | facial | 0.25 | 0 | yes | Conversational emphasis, low specificity |
| `au4_brow_lower` | facial | 0.45 | +1 | yes | Tension/effort marker, moderate |
| `au5_upper_lid_raise` | facial | 0.35 | +1 | yes | Arousal/surprise, needs timing context |
| `au6_cheek_raise` | facial | 0.35 | -1 | yes | Duchenne affect, counter-evidence when congruent |
| `au7_lid_tightener` | facial | 0.45 | +1 | yes | Eye-area tension, co-occurs with stress |
| `au9_nose_wrinkler` | facial | 0.25 | 0 | yes | Disgust, highly context-dependent |
| `au10_upper_lip_raiser` | facial | 0.25 | 0 | yes | Mixed affective interpretation |
| `au12_lip_corner_puller` | facial | 0.25 | 0 | yes | Smile alone not reliable |
| `au14_dimpler` | facial | 0.20 | 0 | yes | Weak standalone |
| `au15_lip_corner_depressor` | facial | 0.30 | +1 | yes | Negative affect, supports stress pattern |
| `au17_chin_raiser` | facial | 0.25 | 0 | yes | Common in neutral speech, low specificity |
| `au20_lip_stretcher` | facial | 0.45 | +1 | yes | Mouth tension marker |
| `au23_lip_tightener` | facial | 0.50 | +1 | yes | Suppression/tension, useful when sustained |
| `au24_lip_pressor` | facial | 0.55 | +1 | yes | Classic suppression, strong with timing |
| `au25_lips_part` | facial | 0.20 | 0 | yes | Common articulation, low specificity |
| `au26_jaw_drop` | facial | 0.20 | 0 | yes | Mostly articulation unless unusually timed |
| `au28_jaw_tension` | facial | 0.50 | +1 | yes | Self-regulatory/suppression (use landmark fallback) |
| `blink_rate` | facial | 0.35 | +1 | yes | Arousal-related, direction varies by person |
| `gaze_aversion` | facial | 0.30 | +1 | yes | Weak alone, stronger with other modalities |
| `smile_asymmetry` | facial | 0.40 | +1 | yes | Incongruence under challenge |
| `head_yaw_variability` | head_pose | 0.30 | +1 | yes | Discomfort/restlessness, nonspecific |
| `head_pitch_variability` | head_pose | 0.30 | +1 | yes | Movement variability, weak alone |
| `head_roll_variability` | head_pose | 0.25 | +1 | yes | Lowest specificity of head axes |
| `self_touch_rate` | head_pose | 0.35 | +1 | yes | Self-soothing, detection errors common |
| `f0_mean_shift` | vocal | 0.60 | +1 | yes | Pitch shift is robust arousal indicator |
| `f0_variability` | vocal | 0.55 | +1 | yes | Prosodic instability = cognitive/emotional load |
| `jitter_local` | vocal | 0.50 | +1 | yes | Voice perturbation with tension/stress |
| `shimmer_local` | vocal | 0.50 | +1 | yes | Amplitude perturbation under load |
| `hnr_drop` | vocal | 0.55 | +1 | yes | Reduced harmonicity = stress/strain |
| `speech_rate_change` | vocal | 0.60 | +1 | yes | Rate shifts anchored to baseline |
| `pause_rate` | vocal | 0.65 | +1 | yes | Processing-load marker, strong |
| `pause_duration_mean` | vocal | 0.70 | +1 | yes | Duration more informative than count |
| `filled_pause_rate` | vocal | 0.65 | +1 | yes | Fillers = planning pressure/uncertainty |
| `answer_latency_ms` | linguistic | 0.90 | +1 | yes | **Highest-value single cue** |
| `repair_rate` | linguistic | 0.80 | +1 | yes | Self-corrections = elevated monitoring load |
| `hedge_rate` | linguistic | 0.75 | +1 | yes | Hedges = reduced commitment |
| `negation_rate` | linguistic | 0.65 | +1 | yes | Negation style, context-sensitive |
| `rppg_hr_shift` | physio | 0.30 | +1 | yes | Only reliable in high-quality stable video |
| `rppg_hrv_rmssd_shift` | physio | 0.25 | +1 | yes | Fragile under compression/motion — bonus only |

**Highest-weight cues:** answer_latency_ms (0.90) > repair_rate (0.80) > hedge_rate (0.75) > pause_duration_mean (0.70) > pause_rate + filled_pause_rate (0.65)

Linguistic timing cues are the most reliable under compressed video. Lean on them.

---

## Scoring Formula (Pre-Claude)

For each cue observation in a QA event:

```
gate_mult = 1.0 if pass | 0.5 if downweight | 0.0 if suppress

signed_evidence = direction × magnitude_norm × base_weight
                  × phase_weight × cue_quality × detector_confidence × gate_mult

# inactive cues count as 0.25 weight (absence also has signal)
if not is_active: signed_evidence × 0.25
```

Aggregation:
```
net_evidence = Σ signed_evidence

# contradiction penalty
pos = Σ max(0, e) for each e
neg = Σ max(0, -e) for each e
contradiction_penalty = min(pos, neg) × 0.35
net_evidence -= sign(net_evidence) × contradiction_penalty

# synergy bonus (independent modalities)
active_modality_count = modalities with |contribution| > 0.25
synergy_bonus = 0 if <2 | 0.20 if 2 | 0.45 if 3 | 0.60 if ≥4
synergy_bonus × directional_alignment_ratio (top 5 cues)
net_evidence += sign(net_evidence) × synergy_bonus

risk_score = round(100 × sigmoid(1.25 × net_evidence))
```

Confidence:
```
confidence = 0.20
           + 0.30 × overall_quality
           + 0.20 × (1 - contradiction_ratio)
           + 0.15 × (active_modality_count / 5)
           + 0.15 × clamp(|net_evidence| / 2.5, 0, 1)
```

Abstain if:
- overall_quality < 0.45
- confidence < 0.55
- active modalities < 2
- contradiction_penalty > 0.60

Labels:
- 0–40 → truth_leaning
- 40–60 → mixed
- 60–100 → deception_leaning
- abstain → abstain (shown as "Insufficient data")

---

## Claude Prompt Strategy

**System prompt key rules:**
1. Rubric-driven JSON output only (no free-form text)
2. Quality-aware: suppress/downweight per gate_status in payload
3. Contradiction-aware: high-quality contradicting cues lower confidence
4. Abstain conditions: low quality, low confidence, <2 modalities, high contradiction
5. Synergy bonus: 2+ independent modalities in tight timing window
6. Self-consistency: run 3 passes at low temperature, take median — if spread > 10 points, lower confidence

**Output schema from Claude:**
```json
{
  "session_id": "string",
  "results": [{
    "qa_id": "string",
    "risk_score_0_100": 0,
    "label": "truth_leaning|mixed|deception_leaning|abstain",
    "confidence_0_1": 0.0,
    "quality_summary": {
      "overall_quality": 0.0,
      "active_modalities": ["vocal", "linguistic"],
      "suppressed_cue_count": 0
    },
    "evidence_summary": {
      "net_evidence": 0.0,
      "synergy_bonus": 0.0,
      "contradiction_penalty": 0.0
    },
    "top_supporting_cues": [
      {"cue_id": "answer_latency_ms", "signed_evidence": 0.72, "phase": "pre", "anchor_word": ""}
    ],
    "top_contradicting_cues": [],
    "abstain_reason": null
  }]
}
```

---

## JSON Payload Schema (Feature Payload to Claude)

Top-level structure:
```
InterviewCuePayload
├── schema_version: "1.0.0"
├── session: {session_id, source, language, started_at_iso}
├── global_quality: {video: {codec, fps, bitrate_kbps, compression_artifact, face_visibility, motion_level}, audio: {snr_db}, asr: {avg_word_confidence}, overall_quality}
├── cue_catalog: {[cue_id]: {modality, base_weight, expected_direction, quality_sensitive}}
├── baseline: {segment_start_ms, segment_end_ms, stats: {[cue_id]: {median, mad, n, stability}}}
└── qa_events: [{
      qa_id, question_text, answer_text,
      t_question_end_ms, t_answer_start_ms, t_answer_end_ms,
      word_timestamps: [{word, start_ms, end_ms, confidence}],
      cue_observations: [{
        cue_id, raw_value, detector_confidence, cue_quality,
        baseline_robust_z, magnitude_norm, direction, duration_ms, is_active,
        timing: {onset_ms, offset_ms, relative_to_answer_start_ms, phase, anchor_word},
        quality_gate_status: pass|downweight|suppress,
        quality_gate_reason
      }]
    }]
```

---

## What Raises Accuracy Most (Priority Order)

1. **Answer latency** — biggest single cue (weight 0.90). Measure from question_end to first word of answer. Sub-100ms and you may have a rehearsed answer.
2. **Linguistic timing cues** — pause rate, pause duration, fillers, repairs, hedges. Compression-immune. Start here.
3. **Robust baseline normalization** (median/MAD per session) — prevents false positives from individual style differences
4. **Quality gates** — suppressing bad rPPG/fine AU data prevents noise from dragging down accuracy
5. **Abstain option** — refusing to score bad footage raises accuracy on what you do score
6. **Multi-modality agreement** — 3+ modalities firing together is far stronger than any single cue
7. **Timing windows** — knowing the cue fired at the onset phase (t0 to t0+2s) vs late is a major signal
8. **Self-consistency** — 3 Claude passes and take median reduces output variance

## What Kills Accuracy (Avoid)

- Forcing a binary verdict on compressed/bad video (use abstain)
- Equal-weighting all cues (linguistic/timing >> rPPG/fine AUs)
- Ignoring individual differences (always normalize to baseline)
- Over-counting correlated facial cues (cap same-family contribution)
- Rehearsed liars (low latency + few fillers → can score as truth — this is a known limitation)
- Class imbalance in evaluation (ensure balanced truth/lie test set)

---

*Accuracy plan complete — ready to build when you say go*
