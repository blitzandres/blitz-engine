# Blitz Engine — Technical Specification
> v1.0 — March 31, 2026 | Research-driven, zero-commercial-cost, open source

---

## What is the Blitz Engine?

The **Blitz Engine** is a modular, open-source behavioral deception detection core. It is not a Chrome extension. It is not a web app. It is the **brain that powers all of those things**.

The engine accepts video input, extracts 66 behavioral cues across 5 modality families, runs Bayesian multimodal fusion with personal baseline calibration, and returns a structured deception signal with uncertainty bounds and cue-level attribution.

Any video software — a Chrome extension, a desktop app, a REST API, a Python library — can plug into the Blitz Engine and get deception analysis. Build once. Deploy anywhere.

---

## The Name

**Blitz** — German for "lightning." Fast signal extraction. No hesitation. The engine fires.

**Blitz Engine** — the core. Everything else is an adapter.

---

## Core Design Principle

> Treat deception as **weak-evidence accumulation under uncertainty**, not direct classification.

No single cue is a lie detector. The engine accumulates evidence across 66 weak signals and computes a posterior probability. The output is always a **score with uncertainty**, never a binary verdict.

---

## Architecture — 5 Layers

```
┌────────────────────────────────────────────────────────────┐
│  LAYER 1: INGESTION                                         │
│  Raw media adapters: browser stream, file, API upload       │
│  Outputs: normalized video clip + audio track               │
├────────────────────────────────────────────────────────────┤
│  LAYER 2: FEATURE EXTRACTION (Modality Plugins)            │
│  Per-modality cue extractors → timestamped CueEvent objects │
│  Visual | Audio | Linguistic | Physiological | CBCA/RM      │
├────────────────────────────────────────────────────────────┤
│  LAYER 3: CALIBRATION                                       │
│  Personal baseline model: trait + state stress + residual   │
│  Robust Z normalization (median/MAD)                        │
│  Session drift correction                                   │
├────────────────────────────────────────────────────────────┤
│  LAYER 4: FUSION                                            │
│  Cue-level experts → cross-modal attention → Bayesian LLR  │
│  Temporal phase scoring (pre / during / post answer)        │
│  Convergence gate: 2+ independent families required         │
├────────────────────────────────────────────────────────────┤
│  LAYER 5: OUTPUT                                            │
│  risk_score | uncertainty | channel_contributions           │
│  quality_flags | cue_attribution | audit_log               │
│  compliance flag: not_for_sole_decision                     │
└────────────────────────────────────────────────────────────┘
```

### The Canonical Object: CueEvent

The engine's internal currency is not raw video. It is the **CueEvent** — a timestamped, normalized behavioral signal.

```
CueEvent {
  cue_id:        string          # e.g. "audio.vot_shortening"
  modality:      enum            # visual | audio | linguistic | physiological | cbca
  timestamp_ms:  int             # when the cue fired
  phase:         enum            # anticipation | response | recovery
  raw_value:     float           # raw extracted measurement
  z_score:       float           # deviation from personal baseline (robust Z)
  llr:           float           # log-likelihood ratio contribution
  quality:       float (0-1)     # extraction confidence
  question_id:   string          # which question this fired on
}
```

This is the abstraction that makes the engine platform-agnostic. Any modality plugin that produces CueEvents plugs into the engine. Any output adapter that consumes the fusion result can be built independently.

---

## Layer 1: Ingestion

### Supported Input Modes

| Mode | Use Case | Notes |
|---|---|---|
| **Continuous clip** (15-30s @ 15-30fps) | Primary: Chrome extension | Minimum for rPPG |
| **File upload** (MP4/WebM) | Batch analysis, desktop app | Full quality |
| **Stream chunk** (adaptive) | Real-time future | Approximate only |

### Quality Pre-Screening (Required)

Before any analysis begins, the engine must reject or warn on:
- Resolution < 480p
- Frame rate < 15fps
- Side profile (face angle > 45°)
- Poor lighting (mean luminance < threshold)
- Severe H.264 compression artifacts

**Expected rPPG accuracy degradation under compression: 2-5x vs lab conditions (MAE 5-10 BPM, not 2 BPM as papers claim)**

---

## Layer 2: Feature Extraction — The 66 Cues

### Modality Plugin Architecture

Each modality is a **standalone plugin** with:
- Standard input: normalized video + audio
- Standard output: `List[CueEvent]`
- No dependencies on other plugins
- Self-contained quality assessment

### Visual Plugin (20 cues)
| Cue | Library | Effect Size |
|---|---|---|
| Blink rate deviation | MediaPipe FaceMesh + EAR | Only vs baseline |
| Micro-expressions | OpenGraphAU (41 AUs) | d ~0.3 |
| Lip compression | OpenGraphAU (AU20/AU23) | d ~0.4 |
| Nose wrinkle | OpenGraphAU (AU9) | Moderate |
| Asymmetric smile | OpenGraphAU (AU6/AU12) | d ~0.5 |
| Eye gaze direction | InsightFace gaze module | Context-dependent |
| Pupil dilation spike | MediaPipe iris tracking (720p+) | 65-75% |
| Jaw tension | OpenGraphAU (AU28) | Moderate |
| Eyebrow raise | OpenGraphAU (AU1/2/4) | Weak alone |
| Eye blocking | MediaPipe + blink duration | Moderate |
| Head movement | InsightFace 3D head pose | d ~0.3 |
| Self-touching | MMPose hand-to-face | d ~0.5 |
| Speech-gesture mismatch | MMPose + Whisper | d ~0.4 |
| Reduced hand gestures | MMPose wrist delta | d ~0.3 |
| Postural shifts | MMPose CoM shift | Moderate |
| Gaze fixation pattern | OpenFace 2.0 IVDT | 70-80% with ML |
| Emblematic slip | MediaPipe Pose bilateral | 85% precision (rare) |
| Gaze aversion duration | OpenFace 2.0 gaze angle | d 0.6-0.8 |
| Self-adaptor duration | MediaPipe Holistic | d ~0.5-0.7 |
| Blink rebound pattern | MediaPipe EAR temporal | Pattern > static rate |

### Audio Plugin (13 cues)
| Cue | Library | Effect Size |
|---|---|---|
| Pitch (F0) increase | librosa pyin() | d ~0.3 |
| Voice tremor (jitter+shimmer) | Parselmouth | Strongest audio cue |
| HNR drop | Parselmouth | d ~0.3 |
| Speech rate change | CrisperWhisper timestamps | d ~0.3 |
| Filler words | CrisperWhisper verbatim | d ~0.4 |
| Pause duration mid-sentence | CrisperWhisper word gaps | d ~0.4 |
| Volume drop on key words | librosa rms() per word | Moderate |
| VOT shortening | Parselmouth (Praat) | AUC 0.89 — strongest new |
| Articulation vs speaking rate | pyAudioAnalysis + Praat | d ~0.3-0.5 |
| Spectral tilt (H1-H2) | openSMILE eGeMAPS | ~65-72% combined |
| Contact Quotient via CPPS | openSMILE + VoiceLab | Moderate, needs baseline |
| Formant dispersion (F1-F4) | Parselmouth FormantPath | AUC ~0.75 |
| Energy-per-syllable irregularity | librosa rms + syllable | ~63% alone |

### Linguistic Plugin (18 cues)
| Cue | Library | Effect Size |
|---|---|---|
| Response delay (pre-answer) | Whisper timestamps | d ~0.4 |
| Distancing language | spaCy POS (i_rate) | d ~0.3 |
| Qualifier overload | spaCy Matcher + hedge lexicon | d ~0.4 |
| Sensory detail poverty | spaCy + sensory lexicon (RM) | d ~0.5 |
| Tense inconsistencies | spaCy morphology | Moderate |
| Pronoun avoidance | spaCy POS distribution | d ~0.3 |
| Abnormal answer length | Word count | Context-dependent |
| Negative emotion density | VADER + NRCLex | d ~0.3 |
| Narrative coherence drop | TextDescriptives | Moderate |
| Verifiable entity poverty | spaCy NER | d ~0.4 |
| Spontaneous corrections rate | Regex + disfluency detection | 72-74% standalone |
| Cognitive operations density | Custom lexicon + spaCy dep | 69.4% (inverted signal) |
| Lexical diversity (MTLD) | lexicalrichness + taaled | ~60-65% |
| Syntactic tree depth | spaCy / stanza dep parser | ~62-68% |
| Direct quote ratio | spaCy + regex | ~63-68% |
| Narrative proportion imbalance | HeidelTime temporal tagger | Weak alone |
| Statement contradiction score | facebook/bart-large-mnli | ~80% NLI benchmark |
| Complication events rate (CBCA) | Adversative markers + spaCy | g ~0.5 |

### Physiological Plugin (5 cues)
| Cue | Library | Effect Size |
|---|---|---|
| Heart rate spike | vitallens-python (CPU) | Moderate |
| HRV drop | vitallens-python | d ~0.3 |
| Skin color / blood flow | vitallens-python | Moderate |
| Multi-ROI rPPG divergence | pyVHR per-ROI CHROM/POS | +15-20% vs single-ROI |
| Contactless EDA proxy | LBP texture on forehead/cheek | r=0.77 correlation |

### CBCA/RM Plugin (10 cues)
| Cue | Framework | Effect Size |
|---|---|---|
| Unusual peripheral details | CBCA + sentence-transformers | g = 0.64 |
| Admitted perceptual uncertainty | CBCA (opposite to qualifiers) | g ~0.4 |
| Cognitive operations contrast | Combines cues 48+65 | Resolves false positives |
| Logical structure | CBCA criterion | g ~0.3 |
| Contextual embedding | CBCA criterion | g ~0.4 |
| Interactions, conversations | CBCA criterion | g ~0.3 |
| Reproduction of conversation | CBCA criterion | g ~0.3 |
| Unexpected complications | CBCA criterion | g ~0.5 |
| Superfluous details | CBCA criterion | g ~0.4 |
| Spontaneous correction | CBCA criterion | g ~0.3 |

---

## Layer 3: Personal Baseline Calibration

**This is the most important layer for accuracy.** It's also the most underimplemented in existing systems.

### The Problem Codex Research Confirmed

Bogaard et al. (2024) found no strong evidence that simple deviation-from-baseline is reliably a lie marker on its own. But person-specific variability is enormous, and population thresholds are brittle (DePaulo 2003).

The solution is a **3-component hierarchical model**:

```
Observed cue = TRAIT level (this person's stable baseline)
             + STATE reactivity (stress from hard questions, not lying)
             + DECEPTION residual (what we actually want to detect)
```

### Baseline Protocol (Research-Updated)

**Previous spec said 30-60s. Codex research says this is not enough.**

| Duration | What you can reliably estimate |
|---|---|
| 30-60s | Coarse pitch center, rough speech rate |
| 90-180s | Stable trait estimates for most cues |
| 180s+ | Stable rPPG BVP waveform, reliable blink statistics |

**New requirement: 90-180s multi-prompt baseline with at least 2 neutral topics.**

### Baseline Topics (Calibration Script)

The baseline must include topics that are:
1. **Neutral** — no emotional loading
2. **Verbal** — person must speak to establish speech features
3. **Slightly varied** — not all identical to capture natural variation

Example prompts:
- "Tell me about your commute this morning"
- "Describe your favorite meal"
- "What did you do last weekend?"

### Normalization: Robust Z (not standard Z)

**Standard Z is fragile to outliers. Use Robust Z:**

```
z_robust = (x - median(baseline)) / (1.4826 × MAD(baseline))
```

Where MAD = Median Absolute Deviation. The 1.4826 factor makes it consistent with standard deviation under normality.

**Also apply Empirical-Bayes shrinkage when baseline is short:**
```
z_shrunk = λ × z_robust + (1 - λ) × 0  # shrink toward population mean
λ = min(1.0, n_baseline_obs / n_target)
```

### Session Drift Correction

Behavior changes over time even within a session. Apply a **rolling baseline refresh** every 5 minutes using trailing-window updates, excluding segments where deception signals are already flagged.

---

## Layer 4: Fusion — Hybrid Architecture

### Why Hybrid (not pure early or pure late)

Per Codex research (DOLOS/PECL, cross-domain benchmark 2405.06995):
- **Early fusion** (concatenate all features): strong in-domain, brittle to missing modalities
- **Late fusion** (score separately, then combine): robust to missing data, misses cross-modal interactions
- **Hybrid**: best of both — modality experts + cross-modal attention + Bayesian late decision

### Fusion Pipeline

```
Step 1: Cue-level experts
Each plugin outputs CueEvents with pre-computed LLR contributions.

Step 2: Within-modality aggregation
Temporal CueEvents → modality summary vector per answer window.
Handle correlated cues (pitch + jitter) by grouping and downweighting:
  effective_dim = trace(Σ) / λ_max(Σ)  (effective dimensionality)

Step 3: Cross-modal attention (optional, if modalities available)
Light attention layer across modality summary vectors.
Handles synergy: e.g., pitch rise + gaze aversion co-firing.

Step 4: Bayesian log-odds accumulation (PROVEN FORMULA)
logit(P(lie|x)) = logit(P_0) + Σ_i [w_i × LLR_i]

Where:
  P_0 = prior deception probability (default: 0.3 — not 0.5, avoid overconfidence)
  LLR_i ≈ d_i × z_i - (d_i²/2)  [under equal-variance Gaussian assumption]
  w_i = reliability weight × quality_score × temporal_phase_multiplier

Step 5: Convergence gate (REQUIRED)
Raise flag only when:
  (a) Posterior probability > calibrated threshold (default: 0.65)
  AND
  (b) At least 2 INDEPENDENT modality families are active
     (prevents single-modality bias — e.g., pitch alone is not enough)
```

### Temporal Phase Multipliers

```
Phase              Window          LLR Multiplier
─────────────────────────────────────────────────
Anticipation      -2s to 0s        1.2×   (anticipatory stress = meaningful)
Response core      0s to end        1.5×   (active deception = strongest)
Recovery           0s to +4s        1.0×   (relief/regret = informative but weaker)
```

### Cue Reliability Weights (Evidence-Based)

| Tier | Effect Size | Default Weight | Examples |
|---|---|---|---|
| Tier 1 — Strong | d > 0.6 or AUC > 0.85 | 1.5× | VOT shortening (AUC 0.89), voice tremor, emblematic slip |
| Tier 2 — Moderate | d 0.4-0.6 | 1.0× | Spontaneous corrections, CBCA peripheral details, gaze fixation |
| Tier 3 — Weak | d 0.2-0.4 | 0.6× | Most individual cues |
| Tier 4 — Anchors | d < 0.2 | 0.3× | Only valuable in convergence context |

---

## Layer 5: Output

### Response Schema

```json
{
  "session_id": "...",
  "question_id": "...",
  "timestamp_ms": 14250,

  "risk_score": 0.72,
  "uncertainty": 0.15,
  "confidence_interval": [0.57, 0.87],

  "channel_contributions": {
    "visual": 0.68,
    "audio": 0.81,
    "linguistic": 0.55,
    "physiological": 0.74,
    "cbca": 0.61
  },

  "top_cues": [
    {
      "cue_id": "audio.vot_shortening",
      "fired_at_ms": 12100,
      "phase": "response",
      "z_score": 2.8,
      "llr": 0.43,
      "on_word": "never"
    }
  ],

  "quality_flags": {
    "video_quality": "acceptable",
    "baseline_duration_s": 120,
    "rppg_reliability": "degraded_compression",
    "missing_modalities": []
  },

  "narrative": "At 14.2s, subject showed Voice Onset Time shortening and jaw tension while saying 'never'. Cues fired 0.3s before speech onset. Multi-ROI rPPG divergence detected simultaneously. Three independent modality families active.",

  "compliance": {
    "not_for_sole_decision": true,
    "use_case": "research",
    "consent_declared": true,
    "jurisdiction": "CA-US"
  }
}
```

---

## Personal Baseline Calibration: The Math

### Separating Trait Anxiety from Deception

The problem: person A is naturally high-pitch with rapid speech. Person B is calm by default. A population threshold will flag A constantly and miss B completely.

**Solution: Within-person deviation scoring**

For each cue `c` and answer `a`:

```
1. Compute baseline distribution: μ_c, σ_c (from 90-180s baseline)
2. Compute stress reactivity: σ_stress (from responses to control questions)
3. Normalize: z_c = (x_c,a - μ_c) / σ_c
4. Gate on question context: only flag if z_c > threshold AND question is high-stakes
5. Topic-specificity bonus: if cue fires on topic-specific word (not all words), multiply LLR by 1.3
```

### The Three Baselines

| Type | How to capture | Used for |
|---|---|---|
| Trait baseline | 90-180s neutral speech at session start | Centering all measurements |
| Stress baseline | 2-3 mildly uncomfortable but truthful questions | Separating anxiety from lying |
| Topic baseline | Truthful answers to similar-domain questions | Detecting topic-specific activation |

---

## Gender Handling (Research-Corrected)

**Previous approach was wrong: do NOT use gender-stratified lie thresholds.**

Codex research (Hall et al. 2025, DOLOS results): sex/gender differences in deception cues are small-to-moderate and not reliable enough for separate scoring models.

**Correct approach:**
1. Use **speaker-normalized prosody** — express pitch in semitones relative to speaker's own baseline (already handles F0 sex differences automatically)
2. Use **person-relative delta** — all cues expressed as deviation from personal baseline
3. **Fairness audit** — test system accuracy separately for male/female/other subgroups and flag performance gaps
4. Do NOT apply different cue weights based on gender

---

## Temporal Analysis — Proven Framework

Based on blink/cognitive-load suppression research (Acta Psych 2008) and DOLOS duration protocol:

### The 3-Phase Window System

```
Pre-response anticipation window: -2s to speech onset
  → Captures: preparatory stress, cognitive load before answering
  → Cues: response delay, anticipatory pitch rise, gaze shift

Response core windows: sliding 1-2s from speech onset to end
  → Captures: active deception signals
  → Cues: VOT, filler words, pause patterns, micro-expressions

Post-response recovery window: 0s to +4s after speech end
  → Captures: relief, regret, suppression rebound
  → Cues: blink rebound spike, pitch return, rPPG recovery
```

### Handling Multi-Second Cues

For cues with inherent temporal structure (blink rebound, rPPG divergence, tense transitions):

```
Model as state machine, not point event:
State 1: Normal → State 2: Suppression → State 3: Rebound

Score the TRANSITION PATTERN not just the presence of any one state.
Blink rebound is more diagnostic than either suppression or spike alone.
```

---

## Convergence Scoring — The Math

### Log-Odds Accumulation Formula

From Bayesian deception detection theory:

```
logit(P(lie|cues)) = logit(P_0) + Σ_i [w_i × (d_i × z_i - d_i²/2)]
```

Where:
- `P_0 = 0.30` (prior: 30% base rate of deceptive responses in interrogative settings)
- `d_i` = effect size for cue i (from literature)
- `z_i` = robust Z-score vs personal baseline
- `w_i` = reliability weight × quality × phase multiplier

**What does this mean practically?**

With average `d = 0.25` and independent cues, total effect size grows as:
```
d_total ≈ 0.25 × √k   (k = number of independent cues)
```

To reach a meaningful signal (d = 1.5 → ~85% separation):
```
k ≥ (1.5 / 0.25)² = 36 independent cues
```

This is why 66 cues are needed — and why convergence (not just count) matters.

### Handling Correlated Cues

Pitch rise and jitter increase are correlated (both reflect laryngeal stress). Double-counting them inflates the signal.

**Correction:**
1. Group known correlated cues into families
2. Compute family-level effective dimensionality: `eff_dim = trace(Σ) / λ_max(Σ)`
3. Downweight within-family contributions proportionally

Predefined correlation groups:
```
Laryngeal stress: pitch, jitter, shimmer, HNR, VOT, formant dispersion
Autonomic arousal: rPPG, EDA proxy, multi-ROI divergence
Cognitive load: speech rate, pauses, fillers, syntactic simplification
Social distance: pronouns, distancing language, gaze aversion
```

### The Two-Gate Rule

**Gate 1:** Posterior probability > 0.65 (configurable)
**Gate 2:** At least 2 independent modality families active

Both gates must be passed. A system that fires on a single modality (even with high confidence) is unreliable.

---

## What Separates Blitz Engine from Everything Else

Based on Codex research of DARE, DOLOS winners, SVC 2025:

### What existing systems DON'T do

1. **Personal baseline calibration** — most systems use population thresholds
2. **Question-locked temporal analysis** — most analyze averages over whole clips
3. **Convergence gating across modality families** — most just sum cue scores
4. **Uncertainty quantification** — most output a single number with no confidence bounds
5. **Correlated cue correction** — most double-count within-family cues
6. **Domain shift handling** — SVC 2025 top accuracy is only ~62% in hard cross-domain settings

### What Blitz Engine will do differently

| Feature | Existing systems | Blitz Engine |
|---|---|---|
| Baseline | Population threshold | 90-180s personal calibration |
| Temporal | Average over clip | 3-phase window per question |
| Fusion | Sum scores | Bayesian log-odds + convergence gate |
| Gender | Fixed weights or gender-stratified | Person-relative delta, fairness-audited |
| Correlated cues | Double-counted | Family grouping + effective dimensionality |
| Output | Single number | Score + uncertainty + cue attribution + compliance |
| Architecture | Monolithic | Modular plugins + canonical CueEvent schema |

---

## Open Source GitHub Repo Structure

### Repository: `blitz-engine`

```
blitz-engine/
│
├── core/                          # The engine itself — no app-specific code
│   ├── schemas/                   # CueEvent, Session, BlitzOutput schemas
│   ├── calibration/               # Personal baseline + robust Z + drift correction
│   ├── fusion/                    # Bayesian log-odds, temporal phases, convergence gate
│   ├── scoring/                   # Cue weights, reliability tiers, correlation groups
│   └── quality/                   # Video quality pre-screening
│
├── modalities/                    # Modality plugins (each standalone)
│   ├── visual/                    # MediaPipe, OpenGraphAU, InsightFace, MMPose
│   ├── audio/                     # librosa, Parselmouth, openSMILE, CrisperWhisper
│   ├── linguistic/                # spaCy, VADER, NRCLex, TextDescriptives, MTLD
│   ├── physiological/             # vitallens-python, pyVHR, rPPG multi-ROI
│   └── cbca_rm/                   # CBCA criteria, Reality Monitoring framework
│
├── apps/                          # Application adapters (consume core engine)
│   ├── chrome-extension/          # Phase 2: Chrome extension widget
│   ├── web-api/                   # FastAPI REST wrapper around engine
│   ├── cli/                       # Command-line: blitz analyze video.mp4
│   └── desktop/                   # Future: Electron or Tauri desktop app
│
├── evaluation/                    # Benchmarking + fairness
│   ├── benchmarks/                # Standardized test protocols
│   ├── datasets/                  # Dataset loaders (DOLOS, Real-Life Trial, etc.)
│   ├── fairness/                  # Subgroup accuracy auditing
│   └── baselines/                 # Comparison vs human judges (54% baseline)
│
├── governance/                    # Ethics and legal
│   ├── MODEL_CARD.md              # Intended use, limitations, accuracy claims
│   ├── INTENDED_USE.md            # What it's for, what it's NOT for
│   ├── PROHIBITED_USES.md         # Hiring, law enforcement, healthcare, EU high-risk
│   └── ETHICS.md                  # Full ethical framework + EU AI Act considerations
│
└── docs/                          # Documentation
    ├── QUICKSTART.md
    ├── architecture.md
    ├── cue_catalog.md             # All 66 cues, effect sizes, implementation status
    ├── calibration_guide.md
    └── contributing.md
```

### Public API (Python SDK)

```python
from blitz_engine import BlitzEngine, BlitzSession

# Initialize engine with modality config
engine = BlitzEngine(
    modalities=["visual", "audio", "linguistic"],  # plug in what you need
    prior=0.30,
    convergence_threshold=0.65
)

# Start session with baseline calibration
session = engine.new_session(
    baseline_video="baseline.mp4",   # 90-180s neutral footage
    consent=True,
    use_case="research",
    jurisdiction="CA-US"
)

# Analyze a response
result = session.analyze(
    video_clip="response1.mp4",
    question="Where were you on Tuesday night?"
)

print(result.risk_score)           # 0.72
print(result.uncertainty)          # 0.15
print(result.top_cues)             # List of CueEvent
print(result.narrative)            # AI narration
print(result.channel_contributions) # Per-modality breakdown
```

### REST API

```
POST /session/new
  body: { baseline_video_b64, consent, use_case, jurisdiction }
  returns: { session_id, baseline_quality, cues_extracted }

POST /session/{id}/analyze
  body: { video_clip_b64, question }
  returns: BlitzOutput (risk_score, uncertainty, top_cues, narrative)

GET /session/{id}/report
  returns: Full session analysis with all questions
```

---

## Legal & Ethics Framework

### Open Source License

**Apache 2.0** for the engine code. This:
- Allows academic and personal use freely
- Requires attribution
- Does NOT allow trademark use of "Blitz Engine"
- Allows commercial use with restrictions noted in INTENDED_USE.md

### Prohibited Uses (from Codex research — EU AI Act 2024/1689)

The following are **explicitly prohibited** by law in the EU and strongly discouraged globally:
- Employment screening or hiring decisions
- Insurance risk assessment
- Law enforcement or immigration adjudication
- Healthcare triage or mental health assessment
- Educational discipline or student assessment
- Any decision made **without human review**

The API will enforce `not_for_sole_decision: true` — this flag cannot be disabled.

### Required Disclosure

Every session must include:
- `consent: true` — caller declares consent was obtained
- `use_case` — must be one of: research | education | journalism | personal | other
- `jurisdiction` — for legal compliance logging

### Ethical Disclosure to Users

```
BLITZ ENGINE ETHICAL DISCLOSURE

This system analyzes behavioral patterns associated with deception.
It does NOT read minds or detect lies with certainty.
Accuracy target: 70-75% vs 54% human baseline.
False positive rate: approximately 25-30%.
This output is a probability, not a verdict.
Do not use to make decisions about people without additional evidence.
```

---

## Accuracy Expectations (Research-Corrected)

| System | Accuracy | Notes |
|---|---|---|
| Human judges (Bond & DePaulo 2006) | 54% | 24,483 judges, 206 studies |
| SVC 2025 competition winner | ~62% | Hard cross-domain setting |
| DOLOS PECL system | ~68% | In-domain benchmark |
| **Blitz Engine target (Phase 1)** | **70-75%** | With personal calibration |
| **Blitz Engine target (Phase 2)** | **75-80%** | With online drift correction |
| Phase 3 with thermal camera | ~83-87% | Validated lab studies only |

The published 85-99% numbers are lab overfitting. Datasets are tiny (121-320 clips). Cross-domain accuracy drops to 60-65%. We will not claim those numbers.

---

## Build Phases (Updated)

### Phase 0 — Foundation (current)
- Complete blueprint research ✅
- Write Blitz Engine spec ✅
- Set up GitHub repo
- Finalize cue catalog with effect sizes
- Write governance docs

### Phase 1 — Core Engine
- Build Layer 1 (ingestion + quality screening)
- Build Layer 2 (all 5 modality plugins)
- Build Layer 3 (personal baseline calibration)
- Build Layer 4 (Bayesian fusion + convergence gate)
- Build Layer 5 (output schema)
- Build CLI adapter (`blitz analyze video.mp4`)

### Phase 2 — Applications
- Build FastAPI REST wrapper
- Build Python SDK (pip installable)
- Build Chrome Extension (connects to local API)
- VHS signal bar UI

### Phase 3 — Validation
- Benchmark on Real-Life Trial dataset
- Fairness audit (subgroup accuracy)
- Publish results vs human baseline
- Publish model card

### Phase 4 — Hardware Extension
- Thermal camera adapter (3 additional cues)
- Validated accuracy ceiling: ~83-87%

---

## Key Decisions (Codex Research-Updated)

| Decision | Choice | Evidence |
|---|---|---|
| Fusion architecture | Hybrid (experts + attention + Bayesian LLR) | DOLOS/PECL, cross-domain benchmark |
| Baseline duration | 90-180s (not 30-60s) | Bogaard et al. 2024 + practical signal stability |
| Normalization | Robust Z (median/MAD) | Outlier resistance |
| Gender handling | Person-relative delta, NOT gender-stratified | Hall et al. 2025, DOLOS results |
| Prior probability | 0.30 (not 0.50) | Conservative, avoids overconfidence |
| Convergence gate | 2+ independent modality families | Prevents single-modality false alarms |
| Correlated cue handling | Family grouping + effective dimensionality | Prevents double-counting |
| Open source license | Apache 2.0 | Allows academic + personal use |
| API design | Forces consent + use_case + jurisdiction | EU AI Act compliance |
| Prohibited uses | Hiring, law enforcement, healthcare, education | EU AI Act 2024/1689 |

---

*Blitz Engine Spec v1.0 — Research by Codex (o3/gpt-5.3-codex)*
*Literature: DePaulo 2003, Bond & DePaulo 2006, Bogaard et al. 2024, DOLOS 2023, SVC 2025, EU AI Act 2024/1689*
*Status: Planning complete. Ready to initialize GitHub repo and begin Phase 1.*
