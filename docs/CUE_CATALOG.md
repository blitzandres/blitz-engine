# Video Lie Detector — Project Blueprint
> v2.1 — Cue catalog and research reference, March 2026
> **ARCHITECTURE SUPERSEDED** → See `BLITZ_ENGINE_SPEC.md` for architecture and `../planning/PROJECT_MAP.md` for repo structure, current status, and implementation order.

---

## Project Rules (v2.1 — Non-Negotiable)

```
1. PLANNING ONLY — No code is written until the user explicitly says to start coding.
2. CONTINUOUS RESEARCH — Always mine papers, signals, and libraries before any build decision.
3. 100% FREE TOOLS — Project is non-commercial. No subscription costs allowed.
   Only acceptable cost = AI API tokens (Claude) for analysis.
   This means:
   → InsightFace pretrained models: NOW USABLE (non-commercial research = OK)
   → openSMILE: NOW USABLE (non-commercial license = OK)
   → All research-only datasets (DOLOS, CASME2, MU3D, etc.): fully usable
   → Railway $5/month Hobby: NOT acceptable — need free hosting alternative
   → LIWC-22: still blocked (proprietary paid)
4. PLATFORM FLEXIBILITY — Chrome Extension is first target.
   If Chrome extension hits blockers → pivot to desktop app or web app.
   Architecture must stay modular so backend is reusable across platforms.
5. RESEARCH PAPERS FIRST — Before adding any cue or tool, check the literature.
   Look for: CBCA, Reality Monitoring, SCAN, MASQ, IEEE FG, ACM MM, ICASSP papers.
```

---

## Free Hosting Alternatives (replaces Railway $5/month)

```
LOCAL FIRST (recommended for personal use):
→ Run Flask/FastAPI backend on localhost
→ Chrome extension calls localhost:PORT
→ Zero hosting cost, full RAM available, no compression loss

REMOTE FREE OPTIONS (if needed):
→ Hugging Face Spaces (CPU free tier — 16GB RAM, 2 vCPU — may work)
→ Google Colab + ngrok (free, not persistent — dev/test only)
→ Render free tier (512MB RAM — too small for full stack)
→ Oracle Cloud Always Free (4 ARM CPUs, 24GB RAM — best free remote option)

DECISION: Start with local. Add remote later if needed.
```

---

## The Vision

A discreet Chrome Extension widget that sits on top of any video, detects behavioral stress cues in real time, and uses Claude AI to narrate findings and deliver a final verdict. Feels like classified government equipment. Looks like a VHS signal monitor.

---

## The Signal Visual

VHS / oscilloscope style bars using block characters:

```
CALM     →  ████████████████  (green, flat)
RISING   →  ████████████░░░░  (yellow)
STRESSED →  ████████░░░░░░░░  (orange)
DECEPTION → ████░░░░░░░░░░░░  (red, jagged)
```

- Each cue gets its own signal line
- Color shifts green → yellow → orange → red
- Widget view: 1 overall bar
- Dropdown: top 5 active cues visible
- Final version: all cues in expanded view

---

## The 40 Cues (Expanded from 20)

### Face — Visual (Camera)
| # | Cue | Signal | Library |
|---|---|---|---|
| 1 | Blink rate deviation | Stress (deviation from personal baseline) | MediaPipe FaceMesh + EAR |
| 2 | Micro-expressions | Involuntary emotion flashes < 0.2 sec | OpenGraphAU |
| 3 | Lip compression | Withholding information | OpenGraphAU (AU20/AU23) |
| 4 | Nose wrinkle | Disgust or discomfort | OpenGraphAU (AU9) |
| 5 | Asymmetric smile | Fake vs genuine (Duchenne) | OpenGraphAU (AU6/AU12 asymmetry) |
| 6 | Eye gaze direction | Looking away during specific questions | InsightFace gaze module |
| 7 | Pupil dilation | Stress / cognitive effort | Custom (iris size tracking, needs 720p+) |
| 8 | Jaw tension | Clenching under stress | OpenGraphAU (AU28) + landmark distance |
| 9 | Eyebrow raise | Surprise or overemphasis | OpenGraphAU (AU1/AU2/AU4) |
| 10 | Swallowing | Anxiety response | Custom (throat tracking — harder, may skip Phase 1) |
| 11 | Lip licking / mouth drying | Stress dries mouth — autonomic response | Custom (lip landmark tracking) |
| 12 | Nostril flare | Arousal / stress | Custom (nostril width from landmarks) |
| 13 | Eye blocking | Closing eyes while talking — blocking info | MediaPipe + blink duration classifier |

### Head & Body — Visual (Camera)
| # | Cue | Signal | Library |
|---|---|---|---|
| 14 | Head movement increase | Restlessness, discomfort | MMPose / InsightFace 3D head pose |
| 15 | Self-touching face/neck | Self-soothing under stress | MMPose (hand-to-face region) |
| 16 | Shoulder tension | Defensive posture | MMPose keypoints |
| 17 | Speech-gesture mismatch | Words vs hands misalignment | MMPose + Whisper combined |
| 18 | Reduced hand gestures | Liars gesture LESS, not more | MMPose wrist movement delta |
| 19 | Postural shifts | Discomfort, wanting to exit | MMPose center-of-mass shift |
| 20 | Object touching/manipulation | Pacifying — reaching for cup, pen, phone | MMPose hand tracking |

### Voice / Audio (Raw Audio Signal)
| # | Cue | Signal | Library |
|---|---|---|---|
| 21 | Pitch (F0) increase | Stress, cognitive load | librosa `pyin()` |
| 22 | Voice tremor / micro-shakiness | Autonomic stress — strongest audio cue | Parselmouth (jitter + shimmer) |
| 23 | HNR drop | Voice becomes breathy/aperiodic under stress | Parselmouth |
| 24 | Speech rate change | Slowing = constructing; speeding = rehearsed | CrisperWhisper word timestamps |
| 25 | Filler words (um, uh, like) | Cognitive overload | CrisperWhisper (verbatim transcription) |
| 26 | Pause duration mid-sentence | Story construction (not just response delay) | CrisperWhisper / WhisperX word gaps |
| 27 | Volume drop on specific words | Confidence decrease on key claim | librosa `rms()` per word window |

### Linguistic / NLP (From Whisper Transcript — via Claude + pre-extraction)
| # | Cue | Signal | Library |
|---|---|---|---|
| 28 | Response delay (pre-answer pause) | Constructing a story | Whisper timestamps |
| 29 | Distancing language | "that person" instead of "I" — disowning narrative | spaCy POS (i_rate) |
| 30 | Qualifier overload | "I think", "maybe", "sort of", "as far as I know" | Custom hedge lexicon + spaCy Matcher |
| 31 | Sensory detail poverty | Truthful stories have smell, texture, temperature | Custom sensory lexicon + spaCy (Reality Monitoring) |
| 32 | Tense inconsistencies | Slipping present when constructing, not recalling | spaCy morphology |
| 33 | Pronoun avoidance | Dropping "I" during personal claims | spaCy POS (pronoun distribution) |
| 34 | Abnormal answer length | Too short or over-elaborated vs question type | Pure Python word count |
| 35 | Negative emotion word density | Anxiety/guilt leaks into word choice | VADER + NRCLex |
| 36 | Narrative coherence drop | Abrupt semantic jumps between sentences | TextDescriptives (coherence score) |
| 37 | Verifiable entity poverty | Truth-tellers include more named people/places/times | spaCy NER (Verifiability Approach) |

### Physiological (rPPG — No Hardware)
| # | Cue | Signal | Library |
|---|---|---|---|
| 38 | Heart rate spike | Stress at specific moment | vitallens-python (POS/CHROM methods) |
| 39 | Heart rate variability (HRV) | Low HRV = sustained high stress | vitallens-python |
| 40 | Skin color / blood flow change | Peripheral vascular response | vitallens-python |

### Thermal (Phase 3 — Hardware Required)
| # | Cue | Signal | Library |
|---|---|---|---|
| 41 | Periorbital heating | Eye area heat under deception — 87.2% validated | Thermal IR camera (FLIR) |
| 42 | Forehead temperature rise | Corrugator + supraorbital blood flow — 76.3% validated | Thermal IR camera |
| 43 | Nose tip temperature shift | The Pinocchio Effect — validated, direction disputed | Thermal IR camera |

---

## New Cues — Research Update v2.1 (26 additional, total now 66)

### Audio / Vocal (6 new)
| # | Cue | Signal | Library | Reliability |
|---|---|---|---|---|
| 41 | Voice Onset Time (VOT) shortening | Fine motor laryngeal control degrades under cognitive load | `parselmouth` (Praat Python) | AUC **0.89** — strongest new audio cue |
| 42 | Articulation rate vs speaking rate divergence | Liars pause more BUT speak faster when talking | `pyAudioAnalysis`, Praat | d ~0.3–0.5, combine with F0 |
| 43 | Spectral tilt flattening (H1–H2) | Pressed/tense phonation under deception stress | `openSMILE` eGeMAPS feature set | ~65–72% combined |
| 44 | Contact Quotient (CQ) via CPPS proxy | Laryngeal tension — gender-specific patterns | `openSMILE`, `VoiceLab` (Python) | Moderate, needs baseline |
| 45 | Formant dispersion (F1–F4 spacing) | Jaw tension + tongue retraction changes vocal tract shape | `parselmouth` `To FormantPath` | AUC ~0.75 as single feature |
| 46 | Energy-per-syllable (EPS) irregularity | Over/under-stress on specific words under cognitive load | `librosa.feature.rms` + syllable segmentation | ~63% alone, strong combined |

### Linguistic / NLP (8 new)
| # | Cue | Signal | Library | Reliability |
|---|---|---|---|---|
| 47 | Spontaneous corrections rate | Truth-tellers self-correct from real memory; liars have fixed script | Regex + disfluency detection | **72–74% standalone** |
| 48 | Cognitive operations density (Reality Monitoring) | Liars insert MORE reasoning/inference to fill fabricated gaps — *inverted signal* | Custom lexicon + `spaCy` dep parse | 69.4% vs 59.4% human judges |
| 49 | Lexical diversity (MTLD score) | Liars repeat concepts; truth-tellers use wider vocabulary | `lexicalrichness`, `taaled` (pip) | ~60–65%, combine with syntax |
| 50 | Syntactic tree depth / rhetorical complexity | Liars use simpler sentences under cognitive load | `spaCy` / `stanza` dep parser | ~62–68% |
| 51 | Embedded attribution / direct quote ratio | Truth-tellers quote exact speech; liars use indirect reported speech | `spaCy` + regex for quote patterns | ~63–68%, low false positive |
| 52 | Narrative proportion imbalance (setup/core/aftermath) | Liars over-elaborate setup/aftermath, thin core event | `HeidelTime` / `SUTime` temporal tagger | Moderate, weak signal alone |
| 53 | Statement-internal contradiction score | Liars contradict themselves across a long statement | `facebook/bart-large-mnli` or `cross-encoder/nli-deberta-v3-large` | ~80%+ NLI benchmark, deception-specific TBD |
| 54 | Complication events rate (CBCA) | Truth-tellers describe obstacles that arose ("I forgot my keys") — liars tell clean scripts | Adversative discourse markers + `spaCy` | g ~0.5 (medium-large) |

### Visual / Body (7 new)
| # | Cue | Signal | Library | Reliability |
|---|---|---|---|---|
| 55 | Response-specific pupil dilation spike | Cognitive load spike within 0.5–2s of deceptive answer | `MediaPipe FaceMesh` (iris radius tracking) | 65–75% alone; higher combined |
| 56 | Gaze fixation pattern (count + duration) | Fabrication = more frequent, shorter fixations vs recall = fewer, longer | `OpenFace 2.0` gaze vector, IVDT filter | **70–80% with ML** |
| 57 | Emblematic slip — partial shoulder shrug | Suppressed "I don't know" shrug fires involuntarily during assertion | `MediaPipe Pose` or `OpenPose` bilateral shoulder Y-tracking | ~85% precision when detected (rare, high precision) |
| 58 | Gaze aversion *duration* (sustained, not momentary) | Sustained aversion >2s during answer window (not frequency) | `OpenFace 2.0` gaze angle output | d ~0.6–0.8 high-stakes |
| 59 | Self-adaptor duration (full-body, not just face) | Arms/clothing/hair touching duration increases under high-stakes deception | `MediaPipe Holistic` hand-to-body proximity | d ~0.5–0.7 high-stakes |
| 60 | Blink rebound pattern (suppression → spike) | Blink suppresses during lie, spikes 2–5s after — temporal profile is the signal | `MediaPipe FaceMesh` EAR (Eye Aspect Ratio) | Moderate; pattern > static rate |
| 61 | Transdermal blood flow redistribution (periorbital vs cheek rPPG) | Sympathetic activation: periorbital warms, cheeks cool under stress | CHROM/POS rPPG per facial ROI via `MediaPipe FaceMesh` | 70–85% emotion lab; deception TBD |

### Physiological / rPPG (2 new)
| # | Cue | Signal | Library | Reliability |
|---|---|---|---|---|
| 62 | Multi-ROI rPPG divergence (sympathetic arousal proxy) | Calm = ROIs correlate; stress = ROIs diverge (autonomic branch split) | `pyVHR` per-ROI CHROM/POS | +15–20% vs single-ROI |
| 63 | Contactless EDA proxy (skin texture micro-variation) | Sweating alters facial skin reflectance; visible in RGB video | `LBP` texture analysis on forehead/cheek ROI | Correlation 0.77 with true EDA (lab) |

### CBCA Sub-criteria (3 new)
| # | Cue | Signal | Library | Reliability |
|---|---|---|---|---|
| 64 | Unusual peripheral details | Truth-tellers include irrelevant authentic details ("dog was barking"); liars script only the main event | `sentence-transformers` semantic distance from topic centroid | g = **0.64** (large) |
| 65 | Admitted perceptual uncertainty (self-handicapping) | Truth-tellers admit their own perception limits; liars never weaken their story | `spaCy` (epistemic verbs + self-reference) | g ~0.4; OPPOSITE direction to qualifier overload |
| 66 | Cognitive operations density directional contrast | Cross-validate: qualifiers ↑ (deception) BUT epistemic self-hedging about perception ↑ (truth) — contrast resolves ambiguity | Combines cues 30 + 65 | Resolves false positives in qualifier overload |

---

## New Libraries Unlocked
| Library | Purpose | Install |
|---|---|---|
| `lexicalrichness` | MTLD lexical diversity | `pip install lexicalrichness` |
| `taaled` | MATTR for short texts | `pip install taaled` |
| `VoiceLab` | CPP/CPPS (glottal proxy) | `pip install VoiceLab` |
| `sentence-transformers` | Semantic distance for peripheral details | `pip install sentence-transformers` |
| `HeidelTime` | Temporal expression tagging | `pip install heideltime` |
| `facebook/bart-large-mnli` | Contradiction detection (HuggingFace) | `transformers` pipeline |

---

## Best Free Datasets (Research Update)
| Dataset | Size | Modalities | Access |
|---|---|---|---|
| **Real-Life Trial (Michigan/Umich)** | 121 clips | Video + audio + transcripts | public.websites.umich.edu/~zmohamed/resources.html |
| **DOLOS (ICCV 2023)** | 1,675 clips, 213 subjects | Audio + video | arXiv 2303.12745 — request from authors |
| **MU3D (Miami University)** | 320 clips, 80 subjects | Video + audio | Via ResearchGate request |
| **Deceptive Opinion Spam Corpus v1.4** | 1,600 hotel reviews | Text only | myleott.com/op-spam.html — freely downloadable |
| **MuDD (2025, arXiv 2603.26064)** | Multi-modal + GSR | Video + physiological | arXiv 2603.26064 |

---

## Reliability Ranking — All New Cues (Highest to Lowest)
1. VOT shortening (A41) — AUC 0.89
2. Spontaneous corrections (L47) — 72–74% standalone
3. Gaze fixation pattern (V56) — 70–80% with ML
4. Unusual peripheral details CBCA (L64) — g = 0.64
5. Response-specific pupil spike (V55) — 65–75%
6. Formant dispersion (A45) — AUC ~0.75
7. Cognitive operations density (L48) — inverted, 69.4%
8. Gaze aversion duration (V58) — d 0.6–0.8
9. Contradiction score NLI (L53) — strong NLI, deception TBD
10. Emblematic slip / partial shrug (V57) — rare, 85% precision

---

## Build Phases

```
PHASE 1 — Core Engine (software only)
→ Local file / CLI / API input first
→ Highest-confidence subset of the 66-cue catalog implemented first
→ VHS signal bars
→ Claude API narration + structured scoring
→ Final probability + uncertainty + abstain option
→ Localhost FastAPI / CLI first (zero-cost research target)

PHASE 2 — Chrome Extension
→ Auto detects face in any video (YouTube, Zoom, etc.)
→ Widget appears on manual activation
→ Captures continuous video clips (NOT sparse frames — see architecture)
→ Sends clips to the same local-first engine underneath

PHASE 3 — Hardware Add-ons
→ Thermal IR camera support (3 additional cues)
→ Validated accuracy ceiling: ~87% in controlled conditions
```

---

## Tech Stack — Final (Research-Validated)

```
VISUAL LAYER
Face landmarks + gaze   → InsightFace (code only, own weights) OR MediaPipe (fallback, Apache 2.0)
Body keypoints          → MMPose 133-keypoint whole body (Apache 2.0 ✅)
Facial action units     → OpenGraphAU (41 AUs, Apache 2.0 ✅) — covers micro expressions
Blink detection         → MediaPipe Face Mesh + EAR algorithm (Apache 2.0 ✅)

AUDIO LAYER
Transcription + fillers → CrisperWhisper (CC-BY-NC-4.0 ✅ for non-commercial research)
                          WhisperX (BSD-2 fallback if project scope changes)
Pitch + energy          → librosa (ISC license ✅)
Jitter/shimmer/tremor   → Parselmouth = Praat in Python (GPL v3 — ok for SaaS backend)
Heart rate + HRV        → vitallens-python (MIT ✅, CPU-only classical methods)

LINGUISTIC LAYER
Pronouns + tense + NER  → spaCy (MIT ✅)
Hedge word density      → Custom lexicon + spaCy Matcher
Sensory detail count    → Custom sensory lexicon + spaCy (Reality Monitoring framework)
Emotion word density    → VADER (MIT ✅) + NRCLex (MIT ✅)
Narrative coherence     → TextDescriptives (MIT ✅) — spaCy plugin
Holistic analysis       → Claude API (CBCA, RM scoring, cross-answer consistency, verdict)

INFRASTRUCTURE
Video processing        → OpenCV
Backend hosting         → Localhost first, Oracle Cloud Always Free / HF Spaces optional
Code storage            → GitHub
Extension               → Chrome Extension (Phase 2)
```

---

## Architecture — CRITICAL UPDATE

**The original "frame every 2 seconds" approach is broken for rPPG.**

rPPG requires a continuous temporal sequence of frames at 15–30fps to extract the BVP (blood volume pulse) waveform via frequency analysis. A single frame every 2 seconds has no temporal signal to analyze.

```
CORRECTED ARCHITECTURE:

Chrome Extension captures:
→ Short continuous video clip (15–30 seconds at 15–30fps)
→ NOT sparse frames
→ Send as base64-encoded video chunk to local FastAPI backend
  (or a configured free remote endpoint if needed)

Backend processes:
→ Frame extraction via OpenCV
→ Face/body detection (InsightFace + MMPose + OpenGraphAU)
→ Audio extraction → CrisperWhisper + librosa + Parselmouth
→ rPPG heart rate → vitallens-python on full clip
→ Linguistic pre-extraction → spaCy + VADER + NRCLex
→ Structured JSON payload sent to Claude API

Claude API:
→ Receives: visual cues + audio cues + linguistic features + timestamps + question/answer context
→ Scores each cue 0-10
→ Flags specific words/moments where cues fired
→ Returns structured JSON verdict + narration

Chrome Extension:
→ Updates VHS signal bars
→ Shows AI narration
→ Queues next clip capture
```

### Why clips not frames:
- rPPG needs time-series pulse data (need 10-30s minimum)
- Blink rate needs sequence data (need 15+ fps continuous)
- Parselmouth needs audio waveform (not silent individual images)
- CrisperWhisper needs continuous speech (not 2-second snippets)

---

## Context-Aware Detection

The key differentiator — cues are judged in context, not in isolation:

```
System captures:
→ The question asked
→ The answer given
→ Which cues fired
→ WHEN exactly they fired (before/during/after answer)
→ Which specific word triggered the cue

Claude receives all of this together and judges intention
not just presence of a cue
```

### Timing Matters
```
Cue BEFORE answer  → anticipation stress
Cue DURING answer  → active deception signal
Cue AFTER answer   → regret or relief
Cue on SPECIFIC WORD → strongest signal of all
```

---

## Claude Prompt Strategy (Linguistic Layer)

Pre-extract deterministic signals locally (cheap, fast, explainable).
Send structured features to Claude for judgment.

```
Pre-extracted before Claude call:
→ i_rate: 0.03 (first-person pronoun ratio — low = flag)
→ hedge_rate: 0.08 (hedge word density per 100 tokens)
→ vader_compound: -0.42 (sentiment)
→ fear_score: 0.12, anger_score: 0.07 (NRCLex)
→ entities: [{"text":"John","label":"PERSON"}, ...] (verifiable)
→ word_count: 47
→ past_verb_pct: 0.6, present_verb_pct: 0.4 (tense distribution)
→ coherence_score: 0.43 (TextDescriptives)
→ sensory_words: ["cold","rough"], count: 2

Claude then scores:
→ distancing_language (0-10)
→ qualifier_overload (0-10)
→ sensory_detail_richness (0-10)
→ tense_consistency (0-10)
→ pronoun_avoidance (0-10)
→ verbosity_anomaly (0-10)
→ negative_affect_density (0-10)
→ narrative_coherence (0-10)
→ overall_deception_risk (0-100)
→ flags: {specific phrases that triggered each score}
```

Do NOT ask Claude "is this person lying?" — ask it to score specific signals.

---

## The Output

### Widget (collapsed)
```
┌──────────────────┐
│  ████████░░  73% │
│  STRESS ELEVATED │
└──────────────────┘
```

### Widget (expanded dropdown)
```
BLINK      ████████░░  74%  ELEVATED
MICRO      ██████░░░░  61%  ELEVATED
LIP        █████████░  89%  CRITICAL
GAZE       ███████░░░  68%  ELEVATED
HEART      ████████░░  77%  STRESSED
...top 5 active cues...

AI: "At 3:45 subject showed lip compression
     combined with gaze aversion while saying 'no'.
     Cues fired 0.2s after the word 'no'.
     Pattern matches known deception timing."
```

### Final Verdict
```
TRUTH ░░░░░░░░░░░░░░░░░░░░░░ LIE
      ├──────────────────78%─┤

"Based on 847 data points across 40 cues,
 this subject showed elevated stress indicators at
 78% confidence. Stress was topic-specific
 not general anxiety. Key moments: 2:14 / 5:33 / 9:01"
```

---

## Verdict Tone — All Three Layers

```
Soft   → "Subject showed elevated stress indicators"
Direct → "78% likelihood of deceptive pattern"
Bold   → shown only above user-set threshold
```

---

## Honest Accuracy Expectations (Research-Corrected)

**Previous blueprint numbers were wrong — based on lab-overfitted papers.**

```
Human unaided baseline (Bond & DePaulo 2006, 24,483 judges): 54%
Best published automated system (SVC 2025 competition winner):  60.43%
Our realistic target — multimodal, context-aware, good video:   70-75%
With Phase 3 thermal (validated lab studies, controlled):        ~83-87%

The 85-99% numbers in papers are lab overfitting.
Datasets are tiny (121-320 clips). Models memorize artifacts.
Cross-domain accuracy drops 50% from those numbers.
```

### Why 70-75% is still valuable
- Baseline is 54% (chance = 50%)
- 70-75% is 16-21 points above chance
- More actionable than human judgment alone
- Value is in flagging WHICH cues fired on WHICH question, not binary verdict

### What raises accuracy
- Personal baseline calibration (neutral footage at start)
- Context-aware cue weighting (cues on specific high-stakes words score higher)
- Multi-cue agreement (5+ cues firing together > any single cue)
- High quality video (720p+, 30fps, front-facing, controlled lighting)

---

## Language & Legal Framing

**Use this language. Not the other column.**

| Say this | Not this |
|---|---|
| "Elevated stress indicators" | "Lying" |
| "Behavioral cues associated with deception" | "Deception detected" |
| "Matches patterns observed in deceptive subjects" | "78% chance of lying" |
| "Cognitive load indicator" | "Lie score" |
| "Deceptive pattern probability" | "LIAR" |

**Required before every session:** Ethical disclaimer with user acknowledgment.

**EU AI Act (2024):** Automated deception detection directed at people without consent = high-risk application. Do not deploy for employment screening, insurance, or law enforcement in the EU without legal review.

---

## Library Research — Verified on GitHub (March 2026)

### Visual Libraries
| Library | Stars | License | Commercial OK? | Covers |
|---|---|---|---|---|
| InsightFace | 28,200 | MIT (code) / Non-commercial (models) | ⚠️ code yes, models NO | Eye gaze, head movement, 106 face landmarks |
| MMPose | 7,400 | Apache 2.0 | ✅ | Full body + whole body 133 keypoints |
| OpenGraphAU | 59 | Apache 2.0 | ✅ | 41 facial action units, 2M training images |
| ME-GraphAU | 204 | MIT | ✅ | 12-41 AUs — backup for OpenGraphAU |
| MediaPipe (Google) | 30,000+ | Apache 2.0 | ✅ | Face mesh 468 points, blink, hand tracking |

### Audio Libraries
| Library | Stars | License | Commercial OK? | Covers |
|---|---|---|---|---|
| librosa | 8,200 | ISC (≈MIT) | ✅ | Pitch (pyin), energy (rms), silence splitting |
| Parselmouth | 1,200 | GPL v3 | ✅ for SaaS | Jitter, shimmer, HNR, voice tremor — clinical grade |
| CrisperWhisper | 500 | Apache 2.0 | ✅ | Fillers (um/uh), verbatim, word timestamps |
| WhisperX | 13,000 | BSD-2 | ✅ | Word-level timestamps, pause gaps |
| vitallens-python | 72 | MIT | ✅ | Heart rate, HRV, rPPG — CPU local methods |
| openSMILE | 1,000 | Non-commercial | ✅ NOW OK (non-commercial project) | Best single lib — ComParE feature set, 6,373 features |

### Linguistic Libraries
| Library | Stars | License | Commercial OK? | Covers |
|---|---|---|---|---|
| spaCy | 30,000+ | MIT | ✅ | POS, NER, morphology, Matcher — foundation |
| VADER | 4,500 | MIT | ✅ | Sentiment for conversational text |
| NRCLex | — | MIT | ✅ | 8-emotion breakdown per word |
| TextDescriptives | 500+ | MIT | ✅ | Coherence, readability, POS proportions |
| Empath | 300 | MIT | ✅ | 200 custom categories, seed-word expansion |
| LIWC-22 | — | Proprietary | ❌ paid | Best dictionary — blocked, no open alternative |

### rPPG / Heart Rate
| Library | Stars | License | Commercial OK? | CPU OK? | Notes |
|---|---|---|---|---|---|
| vitallens-python | 72 | MIT | ✅ | ✅ | Best choice — active March 2026 |
| pyVHR (pyvhr-cpu) | 567 | GPL-3.0 | ✅ SaaS | ✅ | Stale (Jan 2023) — fallback |
| rPPG-Toolbox | 983 | Responsible AI | ⚠️ restrictive | Traditional only | Research benchmarking |

---

## Key Constraints Updated

### Architecture
- Chrome extension must send **continuous video clips** (15-30s at 15-30fps), NOT sparse frames
- rPPG is impossible from sparse frames — needs temporal waveform
- Backend must be platform-agnostic — usable from extension, web app, or desktop app

### Hosting
- **Personal/local use**: Run backend on localhost (zero cost, full RAM, no compression loss)
- **Remote free option**: Oracle Cloud Always Free (4 ARM CPUs, 24GB RAM) or HF Spaces CPU
- Railway $5/month is no longer the target — project is non-commercial, keep costs at $0

### InsightFace License
- Code = MIT (free for commercial use)
- Pretrained model weights = NON-COMMERCIAL RESEARCH ONLY
- **Project is non-commercial → InsightFace models are NOW FULLY USABLE**
- Use InsightFace models directly without workarounds

### openSMILE — NOW AVAILABLE
- License = non-commercial only → project qualifies
- ComParE feature set = 6,373 features, clinical-grade audio analysis
- Best single audio feature extraction library available — integrate in audio module

### Blink Rate Caveat
- Direction of change is inconsistent across individuals (some go up, some go down when lying)
- Only reliable as **deviation from personal baseline**
- Need 30-60 seconds neutral baseline footage at start of every session

### Compression Reality
- YouTube / browser video = H.264 compressed
- rPPG accuracy degrades 2-5x under compression vs lab benchmarks
- Expect MAE 5-10 BPM (not 2 BPM like papers claim)
- Must use model trained on compressed video or fine-tune

---

## Datasets For Training

| Dataset | Content | Size | Access | License |
|---|---|---|---|---|
| **DOLOS** (best) | TV gameshow deception, 25 facial + 5 speech features annotated | 1,675 clips, 213 subjects | ROSE Lab NTU: rose1.ntu.edu.sg/dataset/DOLOS/ | Research non-commercial |
| Real-Life Trial | Actual courtroom footage, truth/lie labeled | 121 clips, 56 speakers | Request: U Michigan (zmohamed) | Research only |
| MU3D | Demographic-balanced truth/lie videos | 320 clips, 80 subjects | Miami OH (signed agreement) | Research non-commercial |
| CASME2 | Micro-expressions, 200fps, 5 categories | 247 samples, 26 subjects | Chinese Academy of Sciences (signed) | Research only |
| MAHNOB-HCI | Emotion + physiology (NOT deception-labeled) | 27 subjects | mahnob-db.eu | Research use |

---

## Existing Reference Repo

**Truthsayer** (github.com/everythingishacked/Truthsayer)
- 141 stars, abandoned Aug 2022, no license
- Stack: Python + OpenCV + MediaPipe + FER
- Covers: heart rate (rPPG), blink rate, gaze, lip, hand-face detection
- **Most architecturally similar to what we're building**
- Read the source code as architecture reference — do not use directly

---

## Cost Estimates

```
2 min video           →  ~$0.08 (Claude API)
10 min video          →  ~$0.35
30 min video          →  ~$1.00
1 hour video          →  ~$2.00

Hosting target        →  $0 (localhost / local GPU or CPU)
Optional remote path  →  Free tiers first (Oracle Cloud / HF Spaces)
Main paid cost today  →  API usage, not infrastructure
```

---

## Video Quality Requirements

```
Minimum:  480p, 24fps, front facing, even lighting
Ideal:    720p+, 30fps, studio lighting, single camera

Works well:   News interviews, podcasts, court hearings
Avoid:        Street interviews, shaky cam, side profiles

Pre-check quality scorer required before analysis starts
30-60 sec neutral baseline footage required at start
Pupil dilation only reliable at 720p+ (high resolution needed)
```

---

## Build Order Recommendation

```
STEP 1: Find, don't build
→ Search for each missing component before building
→ Building from scratch = months. Finding + combining = weeks.

STEP 2: Linguistic module first (~300 lines, 6-8 hours)
→ spaCy + VADER + NRCLex + TextDescriptives
→ All MIT, all pip-installable, all testable with text files
→ No video infrastructure needed
→ Highest accuracy gain per hour of work

STEP 3: Audio module
→ librosa + Parselmouth + CrisperWhisper
→ Testable with audio files before video pipeline exists

STEP 4: Visual module
→ MediaPipe blink + OpenGraphAU expressions + MMPose body
→ Start with MediaPipe (easiest), add OpenGraphAU after

STEP 5: rPPG (vitallens-python)
→ Requires proper continuous video clip architecture
→ Build AFTER clip-based capture is working

STEP 6: Integrate + Claude prompt
→ Assemble all pre-extracted features
→ Build the structured Claude scoring prompt
→ Wire VHS signal bar UI

STEP 7: Chrome extension (Phase 2)
→ Wrap Phase 1 backend in extension widget
→ Handle continuous clip capture and send
```

---

## Business Model (TBD)

```
Option A → user brings their own Claude API key
Option B → subscription ($10-20/month covers Railway + profit)
Option C → freemium (5 free analyses/month, paid unlimited)
Decision → not made yet

Foundation/nonprofit path → unlocks InsightFace models + openSMILE + datasets
```

---

## Key Decisions Made

| Decision | Choice |
|---|---|
| AI Brain | Claude API only (no Gemini) |
| Activation | Manual by user |
| Threshold | User adjustable |
| Storage | Behavioral data only, no identity |
| Internet | Required |
| Export | Yes — shareable report |
| Disclaimer | Required before every session |
| Sound | None — bars do the communicating |
| Sensors | Phase 3 only, pure software first |
| Local model | No — kills scalability |
| Video capture | Continuous clips (NOT sparse frames) |
| Hosting | Localhost first, Oracle Cloud Always Free as remote option |
| InsightFace | Full models usable (non-commercial project) |
| Whisper variant | CrisperWhisper (fillers + verbatim) |
| rPPG library | vitallens-python (MIT, CPU, active) |

---

*Blueprint v2.0 — full research update, March 2026*
*Covers: 40 cues, verified libraries (4 domains), honest accuracy numbers,*
*architecture correction, Railway cost update, legal/ethics framing.*
*Terminal signal preview built (signal_preview.py). Backend not started.*
