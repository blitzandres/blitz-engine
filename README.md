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

### User Session Flow

From consent gate through baseline calibration, live analysis, and final report — or an explicit abstain when quality is insufficient.

```mermaid
flowchart TD
    START(["User opens Blitz Engine\n(CLI / Extension / API)"])

    START --> CONSENT["Provide Consent\n+ Use Case\n+ Jurisdiction"]
    CONSENT -->|rejected or missing| BLOCKED["Access Denied\nSession ends"]
    CONSENT -->|approved| BASELINE

    subgraph SETUP ["Phase 1 — Baseline Setup (90–180s)"]
        BASELINE["Record neutral baseline\n'Talk naturally for 90–180 seconds'"]
        BASELINE --> BQUALITY{"Baseline quality\nacceptable?"}
        BQUALITY -->|no| RETRY_B["Retry baseline\n(bad audio/video)"]
        RETRY_B --> BASELINE
        BQUALITY -->|yes| CALIBRATED["Personal baseline stored\n(robust z-score per cue)"]
    end

    CALIBRATED --> QUESTION

    subgraph ANALYSIS ["Phase 2 — Live Analysis"]
        QUESTION["Ask question / Play clip\n(15–30s per response)"]
        QUESTION --> CAPTURE["Capture response clip\n(video + audio)"]
        CAPTURE --> QGATE{"Input quality\nacceptable?\n(720p+, clean audio)"}
        QGATE -->|no| ABSTAIN["Abstain\n'Insufficient quality to score'"]
        QGATE -->|yes| EXTRACT["Extract behavioral cues\n(66 signals across 5 modalities)"]
        EXTRACT --> NORMALIZE["Normalize vs baseline\n(delta from your personal neutral)"]
        NORMALIZE --> FUSE["Fuse signals\n(Bayesian log-odds + convergence gate)"]
        FUSE --> GATE{"2+ independent\nmodality families\nconverge?"}
        GATE -->|no| ABSTAIN
        GATE -->|yes| SCORE["Risk score + uncertainty\n(0.0 → 1.0, abstain threshold)"]
    end

    SCORE --> REPORT["Narrative report\n+ top contributing cues\n+ confidence interval"]
    SCORE --> LOG["Audit log written\n(session, timestamp, use case)"]
    ABSTAIN --> LOG

    REPORT --> NEXT{"Analyze another\nresponse?"}
    NEXT -->|yes| QUESTION
    NEXT -->|no| DONE(["Session complete"])
```

---

### Data States & Privacy

What form your data takes at every step — and what leaves your device.

```mermaid
flowchart TD
    subgraph INPUT ["User Input"]
        R1["CLI: local file\n.mp4 / .mov / .wav"]
        R2["SDK: file object\nor numpy array"]
        R3["Chrome Extension:\nlive tab/mic chunks"]
        R4["REST API:\nmultipart or stream"]
    end

    R1 & R2 & R3 & R4 --> SE["SessionEnvelope\nsession_id · consent flags\nretention policy · use_case"]

    SE --> NM["NormalizedMedia\nstandardized fps + audio\nsegmented clips\n⚠ Highest sensitivity"]

    NM --> FE["Feature Extraction\n— ALL LOCAL —\nVisual · Audio · Linguistic\nPhysio · CBCA/RM"]

    FE --> FG["FeatureGraph\ntime-aligned vectors\nper-cue confidence scores"]

    NM -.->|"deleted after\nextraction"| TRASH1["🗑 raw media freed"]

    FG --> SC["ScoredCues\nBayesian fused score\nuncertainty estimate\ntop contributing cues"]

    SC --> GATE{"Convergence Gate\n2+ modality families?"}
    GATE -->|no| ABS["BlitzOutput: ABSTAIN"]
    GATE -->|yes| CP

    CP["CuePacket  ← OUTBOUND BOUNDARY\n✅ JSON only — no raw video/audio\nrisk_score · modality_scores\ntop_cues · evidence_spans"]

    CP -->|"Claude API call"| NT["NarrativeText\nhuman-readable explanation\nconfidence framing + caveats"]

    SC & NT --> FR["FinalReport\nrisk_score · uncertainty\ncue_summary · narrative\nnot_for_sole_decision: true"]

    FR --> O1["CLI / SDK output"]
    FR --> O2["REST JSON response"]
    FR --> O3["VHS signal widget"]
    FR --> S1["AuditLog + SessionRecord\nstored locally"]

    S1 -.->|"temp buffers\nwiped at close"| TRASH2["🗑 no raw media retained"]
```

---

### Application Adapters

How CLI, REST API, Chrome Extension, and Python SDK all route through the ethics gate into one core engine.

```mermaid
flowchart TB
    subgraph INPUTS ["Input Sources"]
        CLI["CLI\n`blitz analyze video.mp4`"]
        API["REST API\nPOST /analyze"]
        EXT["Chrome Extension\nLive tab capture"]
        SDK["Python SDK\nblitz.run(path)"]
    end

    subgraph GATE ["Ethics & Consent Gate"]
        CONSENT["Validates:\nconsent · use_case · jurisdiction\n\nBlocks: hiring · law enforcement\nhealthcare · EU high-risk"]
    end

    CLI --> CONSENT
    API --> CONSENT
    EXT --> CONSENT
    SDK --> CONSENT

    CONSENT -->|pass| ENGINE
    CONSENT -->|fail| REJECTED["Request rejected\n403 + reason"]

    subgraph ENGINE ["Blitz Engine Core"]
        INGEST["Ingestion + Quality Gate"]
        INGEST --> FEATURES["Feature Extraction\n5 modality plugins"]
        FEATURES --> CALIB["Baseline Calibration"]
        CALIB --> FUSION["Bayesian Fusion\n+ Convergence Gate"]
        FUSION --> OUT["BlitzOutput\nscore · uncertainty · cues · narrative"]
    end

    OUT --> TERMINAL["Terminal report\n(CLI / SDK)"]
    OUT --> JSON["JSON response\n(API / SDK)"]
    OUT --> WIDGET["VHS signal widget\n(Extension)"]
    OUT --> AUDITLOG["Audit log\n(all adapters)"]
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

## Research Foundation

- DePaulo et al., 2003 — Cues to deception (PMID: 12555795)
- Bond & DePaulo, 2006 — Accuracy of deception judgments (PMID: 16859438)
- Bogaard et al., 2024 — Baselining efficacy (doi:10.1016/j.actpsy.2023.104112)
- Guo et al., 2023 — DOLOS + PECL (arXiv:2303.12745)
- Lin et al., 2025 — SVC 2025 challenge results (arXiv:2508.04129)
- EU AI Act, 2024 — Regulation 2024/1689
