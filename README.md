# Blitz Engine

> The open-source behavioral deception detection core.

Blitz Engine is a modular, research-driven engine that analyzes video to detect behavioral deception signals. It combines 66 cues across visual, audio, linguistic, physiological, and cognitive analysis — fused using a Bayesian log-odds architecture with personal baseline calibration.

**Not a lie detector. A behavioral signal analyzer.**

---

## What makes it different

| Feature | Other systems | Blitz Engine |
|---|---|---|
| Baseline | Population thresholds | 90-180s personal calibration |
| Temporal analysis | Averages over clip | 3-phase window per question |
| Fusion | Sum of scores | Bayesian log-odds + convergence gate |
| Correlated cues | Double-counted | Family grouping + effective dimensionality |
| Gender handling | Fixed or stratified weights | Person-relative delta, fairness-audited |
| Output | Single score | Score + uncertainty + cue attribution + compliance |
| Architecture | Monolithic | Modular plugins + canonical CueEvent schema |

---

## 📚 Planning Phase Documentation

All planning artifacts consolidated in [`planning/`](planning/) folder:

| Document | Purpose |
|---|---|
| **[planning/PROJECT_MAP.md](planning/PROJECT_MAP.md)** | Canonical project map — repo reality, source-of-truth rules, implementation order |
| **[planning/INDEX.md](planning/INDEX.md)** | Start here — overview of all planning documents and quick navigation |
| **[planning/BLITZ_ENGINE_SPEC.md](planning/BLITZ_ENGINE_SPEC.md)** | Complete technical specification (30KB) — all 5 layers, 66 cues, APIs, output schema |
| **[planning/LIE_DETECTOR_BLUEPRINT.md](planning/LIE_DETECTOR_BLUEPRINT.md)** | Project blueprint (31KB) — vision, constraints, tech stack, library verification |
| **[planning/ACCURACY_PLAN.md](planning/ACCURACY_PLAN.md)** | Accuracy strategy (14KB) — quality gates, baseline normalization, scoring formula |
| **[planning/RESEARCH.md](planning/RESEARCH.md)** | Implementation research (14KB) — 6 gaps resolved, 2 blockers, library install methods |
| **[planning/COMPETITIVE_RESEARCH.md](planning/COMPETITIVE_RESEARCH.md)** | Competitive landscape (Apr 2026) — 10 top repos, novel techniques, free datasets, accuracy benchmarks |
| **[planning/signal_preview.py](planning/signal_preview.py)** | VHS signal UI demo — run with `python planning/signal_preview.py` |

`planning/` is the canonical research source tracked in Git. If you keep external mirror copies, sync them from here.

**Total:** ~100 KB planning documentation. Ready for Phase 1 implementation sequencing.

---

## Accuracy (Honest)

| System | Accuracy |
|---|---|
| Human judges (Bond & DePaulo 2006, 24k judges) | 54% |
| SVC 2025 competition winner (cross-domain) | ~62% |
| Blitz Engine Phase 1 target | 70-75% |
| Blitz Engine Phase 2 target (with drift correction) | 75-80% |

The 85-99% numbers in papers are lab overfitting on tiny datasets (121-320 clips). We don't claim those numbers.

---

## How It Works

### 1 · User Session Flow

Consent gate → 90–180s personal baseline → per-response analysis → convergence gate → verdict or explicit abstain.

```mermaid
flowchart TD
    START(["User opens Blitz Engine\n(CLI / Extension / API)"])

    START --> CONSENT["Consent Gate\n─────────────────────\nvalidates: consent flag\nuse_case field\njurisdiction field"]
    CONSENT -->|"missing or blocked use_case"| BLOCKED["403 Access Denied\nno session created"]
    CONSENT -->|approved| BASELINE

    subgraph SETUP ["PHASE 1 — Baseline Calibration  (90–180s)"]
        BASELINE["Record neutral baseline clip\n─────────────────────\nCaptures: FramePacket stream\n+ AudioChunkPacket stream\nduring neutral speech"]
        BASELINE --> BQUALITY{"Quality gate\nface tracked?\nclean audio?"}
        BQUALITY -->|fail| RETRY_B["Retry — bad input\n(return reason to user)"]
        RETRY_B --> BASELINE
        BQUALITY -->|pass| CALIBRATED["BaselineProfile stored\n─────────────────────\nper-cue: median + MAD\n(robust z-score anchors)\nExpires at session end"]
    end

    CALIBRATED --> QUESTION

    subgraph ANALYSIS ["PHASE 2 — Per-Response Analysis  (15–30s per clip)"]
        QUESTION["Question asked / clip played"]
        QUESTION --> CAPTURE["Capture response\nFramePacket + AudioChunkPacket"]
        CAPTURE --> QGATE{"Input quality?\n720p+, stable face\nclean audio, SNR ok"}
        QGATE -->|fail| ABSTAIN["BlitzOutput: ABSTAIN\nreason: input_quality_insufficient"]
        QGATE -->|pass| EXTRACT["Feature Extraction — all local\n5 modality chains in parallel\n→ VisualCueFrame\n→ AudioCueWindow\n→ LinguisticCueWindow\n→ PhysioCueWindow\n→ CBCAPacket"]
        EXTRACT --> NORMALIZE["Baseline Normalization\n─────────────────────\nz_i = (x − median) / (1.4826×MAD)\nper cue, vs personal baseline"]
        NORMALIZE --> FUSE["Bayesian Fusion\nlogit(P) = logit(0.30)\n+ Σ[w_i × (d_i×z_i − d_i²/2)]"]
        FUSE --> GATE{"Convergence Gate\nposterior > 0.65\nAND active_families ≥ 2?"}
        GATE -->|no| ABSTAIN
        GATE -->|yes| SCORE["PosteriorPacket → BlitzOutput\nrisk_score · uncertainty\ncue_attribution ranked"]
    end

    SCORE -->|"CuePacket JSON only\n→ Claude API"| NARRATIVE["NarrativeText returned\nhuman-readable · caveats included"]
    NARRATIVE --> REPORT["BlitzOutput FINAL\nrisk_score · uncertainty\ncue_attribution · narrative\nnot_for_sole_decision: true"]
    ABSTAIN --> LOG
    REPORT --> LOG["AuditLog written\nsession_id · timestamp · use_case"]

    REPORT --> NEXT{"Analyze\nanother response?"}
    NEXT -->|yes| QUESTION
    NEXT -->|no| DONE(["Session complete\nraw media wiped from memory"])
```

---

### 2 · Modality Extraction — Technical Sequence

Each modality chain runs in parallel. Data passes as typed packet objects between library calls, joined into a feature bus before fusion.

```mermaid
flowchart LR
    subgraph VISUAL ["VISUAL  (per frame)"]
        direction TB
        V1["MediaPipe FaceMesh\n→ FaceMeshPacket\nlandmarks_3d[478]\nblink_EAR, tracking_conf"]
        V1 -->|"visual.facemesh.ready"| V2["OpenGraphAU\n→ AUPacket\nau_intensity[41 keys]\nau_presence[41 keys]"]
        V1 -->|"cached frame"| V3["MMPose / rtmlib\n→ Pose133Packet\nkeypoints_133[{x,y,conf}]"]
        V1 -->|"cached frame"| V4["InsightFace\n→ GazeHeadPacket\nhead_pose{yaw,pitch,roll}\ngaze{yaw,pitch,eye_contact_prob}"]
        V2 & V3 & V4 -->|"join by frame_id\nmodality.visual.ready"| VCUE["VisualCueFrame\nblink_rate_hz · au_41\npose_133 · head_pose · gaze\nquality{face_ok, pose_ok}"]
    end

    subgraph AUDIO ["AUDIO  (per 1s window)"]
        direction TB
        A1["librosa\n→ ProsodyPacket\nf0_hz_series, voiced_prob\nrms_series, f0_mean/std"]
        A1 -->|"audio.prosody.ready"| A2["Parselmouth/Praat\n→ VoiceQualityPacket\njitter · shimmer · hnr_db\ntremor_index"]
        A2 -->|"audio.voice_quality.ready"| A3["CrisperWhisper\n→ TranscriptPacket\ntext · words[{w,start_ms,conf}]\nfiller_words[{w,start_ms}]"]
        A3 -->|"audio.asr.ready"| A4["vitallens rPPG\n→ CardioPacket\nhr_bpm · hrv_rmssd_ms\nrr_intervals_ms"]
        A1 & A2 & A3 & A4 -->|"join by time window\nmodality.audio.ready"| ACUE["AudioCueWindow\nprosody · voice_quality\nasr · cardio · quality{snr_db}"]
    end

    subgraph LING ["LINGUISTIC  (per utterance)"]
        direction TB
        L1["spaCy nlp(text)\n→ SpacyPacket\npos/ner/morph/dep counts\ndoc_len_tokens"]
        L1 -->|"ling.spacy.ready"| L2["VADER\n→ VaderPacket\nsentiment{neg,neu,pos,compound}"]
        L2 -->|"ling.vader.ready"| L3["NRCLex\n→ NRCEmotionPacket\nemotions8{anger,fear,trust...}"]
        L3 -->|"ling.nrc.ready"| L4["TextDescriptives\n→ TextDescPacket\nreadability · coherence\ncomplexity{ttr,mean_sent_len}"]
        L4 -->|"ling.textdesc.ready"| L5["SentenceTransformer\n→ SemanticPacket\ncbca_semantic_distance\ncontradiction_distance"]
        L1 & L2 & L3 & L4 & L5 -->|"join by utterance_id\nmodality.linguistic.ready"| LCUE["LinguisticCueWindow\nspacy · sentiment · emotions8\ntextdesc · semantic · transcript_ref"]
    end

    subgraph PHYSIO ["PHYSIO  (per window)"]
        direction TB
        P1["vitallens multi-ROI\n→ PhysioCueWindow\nroi_delta{forehead,cheekL,cheekR,chin}\nroi_divergence_index\nperfusion_asymmetry"]
        P1 -->|"modality.physiological.ready"| PCUE["PhysioCueWindow ✓"]
    end

    subgraph CBCA ["CBCA/RM  (needs ling + visual)"]
        direction TB
        CB1["cbca_rm_score(\n  LinguisticCueWindow,\n  VisualCueFrame[]\n)\n→ CBCAPacket\ncbca_criteria_scores[dict]\nrm_score · statement_quality"]
        CB1 -->|"cbca.ready"| CCUE["CBCAPacket ✓"]
    end

    VCUE & ACUE & LCUE & PCUE & CCUE -->|"all modalities present\n→ Fusion Stage"| FUSE(["→ Fusion"])
```

---

### 3 · Fusion & Output — Technical Sequence

Four staged fusion pipeline: evidence collection → baseline normalization → Bayesian accumulation → convergence gate → BlitzOutput → Claude narrative.

```mermaid
flowchart TD
    IN(["← 5 modality feature buses"])

    IN --> S1["STAGE 1 · Per-Cue Evidence\n─────────────────────────────\nCueEvidencePacket\ncues: list of {\n  cue_id, modality_family\n  x: raw cue value\n  d_i: effect size weight\n  reliability_w: cue reliability\n  llr_raw: log-likelihood ratio\n}\npublish: fusion.evidence.ready"]

    S1 -->|"baseline.ready = true\n(90–180s stats loaded)"| S2

    S2["STAGE 2 · Robust Baseline Normalization\n─────────────────────────────\nNormalizedEvidencePacket\nper cue:\n  z_i = (x − median) / (1.4826 × MAD + ε)\n  median, MAD from baseline window\n─────────────────────────────\nRolling baseline: 90–180s window\nRobust Z — not standard Z\nOutlier resistance via MAD\npublish: fusion.normalized.ready"]

    S2 --> S3["STAGE 3 · Bayesian Log-Odds Accumulation\n─────────────────────────────\nPosteriorPacket\nlog_odds: float\nposterior = sigmoid(log_odds)\ncontributing_cues ranked by |w_i × d_i × z_i|\nactive_families: set of modality names\n─────────────────────────────\nFORMULA:\nlogit(P) = logit(0.30)\n         + Σ [ w_i × (d_i × z_i − d_i²/2) ]\n\nPrior = 0.30 (avoids overconfidence)\nw_i = reliability_w\nd_i = effect size weight\nz_i = baseline-normalized value\npublish: fusion.posterior.updated  (each window)"]

    S3 --> GATE{"STAGE 4 · Convergence Gate\n─────────────────────────────\nDecisionPacket\npassed = (posterior > 0.65)\n       AND (active_families ≥ 2)\n─────────────────────────────\nBlocks single-modality false alarms\nRequires cross-modal agreement"}

    GATE -->|"passed = false\naccumulate next window"| S3

    GATE -->|"passed = true\ndecision.ready"| BUILD

    BUILD["BlitzOutput Builder\n─────────────────────────────\nrisk_score = posterior\nuncertainty = posterior variance\ncue_attribution: list of {\n  cue_id · modality_family\n  weight · direction · evidence\n}\nnarrative = null  ← filled next\nnot_for_sole_decision = true  ← hardcoded\npublish: output.blitz.ready"]

    BUILD -->|"OUTBOUND BOUNDARY\nno raw media crosses this line"| CLAUDE

    CLAUDE["CuePacket → Claude API\n─────────────────────────────\n✅ JSON only\n✅ No raw video / audio\n✅ No full ASR transcript\n─────────────────────────────\n{\n  session_id\n  risk_score, uncertainty\n  top_cues: [{\n    label, modality_family\n    signed_strength, short_evidence\n  }]\n  constraints: {no_raw_media: true}\n}\n─────────────────────────────\nClaude returns → NarrativeText"]

    CLAUDE --> FINAL["BlitzOutput FINAL\n─────────────────────────────\nrisk_score: float\nuncertainty: float\ncue_attribution: list\nnarrative: str\nnot_for_sole_decision: true\nmetadata: {session_id, t_end_ms, model_version}"]

    FINAL --> CLI["CLI / SDK\nterminal + JSON"]
    FINAL --> API2["REST API\nJSON response"]
    FINAL --> EXT["Chrome Extension\nVHS signal widget"]
    FINAL --> AUDIT["AuditLog\nsession · timestamp · use_case · config_hash"]

    GATE -->|"quality gate failed\nbefore reaching posterior > 0.65"| ABS["BlitzOutput: ABSTAIN\nrisk_score: null\nreason: convergence_not_reached\n     OR input_quality_insufficient\nStill writes to AuditLog"]
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: INGESTION — video + audio normalization            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: FEATURE EXTRACTION — 5 modality plugins           │
│  Visual | Audio | Linguistic | Physiological | CBCA/RM       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: PERSONAL CALIBRATION — 90-180s baseline           │
│  Trait + state stress + deception residual                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: BAYESIAN FUSION — hybrid architecture             │
│  Cue experts → cross-modal attention → log-odds → gate      │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: OUTPUT — risk score + uncertainty + attribution    │
└─────────────────────────────────────────────────────────────┘
```

Full specification: [planning/BLITZ_ENGINE_SPEC.md](planning/BLITZ_ENGINE_SPEC.md)

---

## The 66 Cues

| Domain | Count | Key signals |
|---|---|---|
| Visual / facial | 20 | Micro-expressions, gaze fixation, blink rebound, pupil dilation |
| Audio / vocal | 13 | VOT shortening (AUC 0.89), voice tremor, formant dispersion |
| Linguistic / NLP | 18 | Spontaneous corrections, MTLD diversity, NLI contradiction |
| Physiological rPPG | 5 | Multi-ROI divergence, contactless EDA proxy |
| CBCA / RM | 10 | Peripheral details (g=0.64), cognitive operations density |

Full catalog: [docs/CUE_CATALOG.md](docs/CUE_CATALOG.md)

---

## Quick Start (planned — Phase 1)

```python
from blitz_engine import BlitzEngine

engine = BlitzEngine(modalities=["visual", "audio", "linguistic"])

session = engine.new_session(
    baseline_video="baseline_90s.mp4",
    consent=True,
    use_case="research",
    jurisdiction="CA-US"
)

result = session.analyze(
    video_clip="response.mp4",
    question="Where were you on Tuesday?"
)

print(result.risk_score)     # 0.72
print(result.uncertainty)    # 0.15
print(result.narrative)      # "At 14.2s, VOT shortening + jaw tension..."
```

---

## Repo Structure

```
blitz-engine/
├── core/              Engine: schemas, calibration, fusion, scoring, quality
├── modalities/        Plugins: visual, audio, linguistic, physiological, cbca_rm
├── apps/              Adapters: chrome-extension, web-api, cli
├── evaluation/        Benchmarks, fairness audits, baselines
├── governance/        Ethics, intended use, prohibited uses, model card
├── docs/              Architecture spec, cue catalog, guides
└── planning/          Canonical research bundle and implementation map
```

---

## Ethics & Legal

This software is for **research, education, and journalism only**.

- Accuracy is 70-75% — false positive rate is ~25-30%
- Every API call requires declared consent, use case, and jurisdiction
- `not_for_sole_decision` flag is always true and cannot be disabled
- **Prohibited:** hiring, law enforcement, insurance, healthcare, education discipline

See [governance/PROHIBITED_USES.md](governance/PROHIBITED_USES.md) and [governance/ETHICS.md](governance/ETHICS.md).

EU AI Act (Regulation 2024/1689) applies. Do not deploy for high-risk uses in EU without legal review.

---

## Status

- [x] Phase 0 — Research complete, planning consolidated, repo initialized
- [ ] Phase 1 — Core engine (all 5 layers + modality plugins + CLI)
- [ ] Phase 2 — Applications (FastAPI, Python SDK, Chrome Extension)
- [ ] Phase 3 — Validation (benchmark + fairness audit + model card)
- [ ] Phase 4 — Hardware extension (thermal camera)

---

## License

Apache 2.0 — free for academic, research, and personal use. Attribution required.
See [governance/PROHIBITED_USES.md](governance/PROHIBITED_USES.md) for use restrictions.

---

## Competitive Landscape

Key open-source repositories in this field (full analysis in [planning/COMPETITIVE_RESEARCH.md](planning/COMPETITIVE_RESEARCH.md)):

| Repo | What it does | Relevance |
|---|---|---|
| [RH-Lin/MMPDA](https://github.com/RH-Lin/MMPDA) | SVC 2025 winner — cross-domain adaptation | Phase 2 domain shift fix |
| [dclay0324/ATSFace](https://github.com/dclay0324/ATSFace) | LoRA per-subject calibration → 92% | Phase 2 calibration upgrade |
| [NMS05/DOLOS-PECL](https://github.com/NMS05/Audio-Visual-Deception-Detection-DOLOS-Dataset-and-Parameter-Efficient-Crossmodal-Learning) | Temporal adapter + crossmodal fusion (ICCV 2023) | Architecture reference |
| [cai-cong/MDPE](https://github.com/cai-cong/MDPE) | 104hr dataset + Big Five personality (HuggingFace) | Free training data |
| [ubicomplab/rPPG-Toolbox](https://github.com/ubicomplab/rPPG-Toolbox) | NeurIPS 2023 rPPG — HR/HRV from webcam | vitallens upgrade path |
| [Redaimao/awesome-deception](https://github.com/Redaimao/awesome-multimodal-deception-detection) | Curated field index | Research tracking |

**Why we're different:** Every published system uses population thresholds on tiny datasets (Michigan = 121 clips). The SVC 2025 cross-domain winner scored 60.43%. Blitz Engine's 70-75% target is achievable specifically because of personal calibration — a measurement advantage, not a model advantage.

---

## Research Foundation

- DePaulo et al., 2003 — Cues to deception (PMID: 12555795)
- Bond & DePaulo, 2006 — Accuracy of deception judgments (PMID: 16859438)
- Bogaard et al., 2024 — Baselining efficacy (doi:10.1016/j.actpsy.2023.104112)
- Guo et al., 2023 — DOLOS + PECL (arXiv:2303.12745)
- Lin et al., 2025 — SVC 2025 challenge results (arXiv:2508.04129)
- Cai et al., 2024 — MDPE dataset + personality modulation (arXiv:2407.12274)
- Lee et al., 2023 — ATSFace LoRA calibration (arXiv:2309.01383)
- Liu et al., 2023 — rPPG-Toolbox (NeurIPS 2023)
- EU AI Act, 2024 — Regulation 2024/1689
