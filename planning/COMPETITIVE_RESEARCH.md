# Blitz Engine — Competitive & Academic Repository Research
> Completed April 6, 2026 | GitHub landscape + arXiv survey

This document catalogs the most relevant open-source deception detection repositories and academic findings. Purpose: identify what the field has built, extract novel techniques, and document what Blitz Engine should absorb, reference, or improve upon.

---

## TOP REPOSITORIES

### 1. Redaimao/awesome-multimodal-deception-detection
**URL:** https://github.com/Redaimao/awesome-multimodal-deception-detection
**Type:** Curated reading list / meta-index
**Why important:** The definitive living index of the field. References papers from CVPR, ICCV, CVPRW spanning 2005–present. Lists the open-source tools used across the field: OpenFace (facial AU extraction), wav2vec 2.0 (audio self-supervised), OpenSmile (handcrafted audio features). The single best starting point for tracking what methods have been benchmarked and on which datasets.

---

### 2. NMS05/Audio-Visual-Deception-Detection-DOLOS-Dataset-and-Parameter-Efficient-Crossmodal-Learning
**URL:** https://github.com/NMS05/Audio-Visual-Deception-Detection-DOLOS-Dataset-and-Parameter-Efficient-Crossmodal-Learning
**Paper:** ICCV 2023
**Tech stack:** PyTorch, Transformer-based architectures, cross-modal fusion
**Dataset:** DOLOS — 1,675 clips from 213 participants, 84 TV episodes, annotated with MUMIN coding scheme (25 visual + 5 vocal features)

**Key innovations:**
- **Uniform Temporal Adapter (UT-Adapter):** Explores temporal attention inside frozen transformer backbones — only adapter layers trained, not the full model (LoRA-style efficiency)
- **Plug-in Audio-Visual Fusion (PAVF):** Crossmodal fusion module combining audio and visual transformer streams with minimal added parameters

The LoRA-style adapter approach for crossmodal fusion is directly applicable to Phase 2 of Blitz Engine as a neural alternative to the current Bayesian fusion layer.

---

### 3. cai-cong/MDPE
**URL:** https://github.com/cai-cong/MDPE
**HuggingFace (FREE):** https://huggingface.co/datasets/MDPEdataset/MDPE_Dataset
**Paper:** arXiv:2407.12274
**Tech stack:** Multimodal fusion, personality + emotion feature integration
**Dataset:** MDPE — 104+ hours, 193 subjects, facial video + audio + transcript. **Largest publicly released multimodal deception dataset.** Uniquely includes Big Five personality scores and emotional valence/arousal labels per subject.

**Key finding:** Text modality significantly outperforms visual and acoustic alone. Multimodal fusion consistently improves over any single modality.

**Relevance:** The personality + individual-difference annotations parallel Blitz Engine's baseline calibration system. The dataset is on HuggingFace — free access, no request required. 104 hours vs. Michigan's 121 videos.

---

### 4. Sutadasuto/DDV
**URL:** https://github.com/Sutadasuto/DDV
**Paper:** "High-Level Features for Multimodal Deception Detection in Videos" (CVPRW 2019)
**Tech stack:** OpenFace, COVAREP (audio), IBM Watson ASR, SyntaxNet (NLP), Python 3.6
**Features extracted:** Facial AUs + head pose + gaze via OpenFace; prosody via COVAREP; syntactic parse features via SyntaxNet

Full multimodal pipeline with openly documented feature engineering. Demonstrates COVAREP as an alternative to Parselmouth for low-level speech features (glottal source, NAQ, QOQ, H1-H2, spectral tilt).

---

### 5. 4qlaa7/Multimodal_Deception_Detection
**URL:** https://github.com/4qlaa7/Multimodal_Deception_Detection
**Tech stack:** LSTM, BiLSTM, pretrained CNN, BERT embeddings
**Dataset:** Real Life Trials 2016 (University of Michigan, 121 videos)
**Reported accuracy:** 83.05% subject-level — **caveat: small dataset, likely high variance, not generalizable**

Uses BERT for text embeddings and BiLSTM for sequence modeling over temporal feature windows. Solid architecture reference for the linguistic modality plugin.

---

### 6. ritikamotwani/Deception-Detection
**URL:** https://github.com/ritikamotwani/Deception-Detection
**Tech stack:** NLP, verbal/linguistic cues, classical ML
**Datasets:** Real-Life Trial Michigan + Deceptive Opinion Spam Corpus v1.4

Verbal-only baseline. Clean implementation for isolating the linguistic modality. The Deceptive Opinion Spam Corpus (Ott et al.) is fully free and open — useful for training the linguistic plugin.

---

### 7. RH-Lin/MMPDA — SVC 2025 Challenge Winner
**URL:** https://github.com/RH-Lin/MMPDA
**Paper:** "Multi-source Multimodal Progressive Domain Adaptation for Audio-Visual Deception Detection" (ACM MM 2025 SVC Workshop)
**Accuracy:** 60.43% / 56.99% F1 on cross-domain test set — **beat 1st place by 5.59% F1**

**Key innovation:** Multi-source Progressive Domain Adaptation (MMPDA) — transfers audio-visual knowledge from multiple diverse source domains to an unseen target domain using adversarial domain confusion + domain-invariant feature learning.

This addresses the #1 real-world failure mode: models trained on courtroom/lab video failing on user webcam sessions. MMPDA's open implementation is the Phase 2 cross-domain adaptation starting point.

---

### 8. dclay0324/ATSFace — LoRA Per-Subject Calibration
**URL:** https://github.com/dclay0324/ATSFace
**Paper:** "LoRA-like Calibration for Multimodal Deception Detection using ATSFace Data" (IEEE BigData 2023)
**Reported accuracy:** 92% on Real-Life Trial after per-subject calibration

**Key innovation:** LoRA-inspired fine-tuning where rank decomposition matrices adapt the deception model to individual subjects — a per-person calibration layer injected into the neural network.

**Direct Blitz Engine parallel:** Our 90-180s robust Z-score baseline is the classical signal-processing analog to what ATSFace does with LoRA at the deep learning level. ATSFace proves this concept scales to neural architectures and is the Phase 2 upgrade path for the calibration layer.

---

### 9. ubicomplab/rPPG-Toolbox
**URL:** https://github.com/ubicomplab/rPPG-Toolbox
**Stars:** 1,000+ | **Paper:** NeurIPS 2023
**License:** MIT
**Tech stack:** PyTorch, PhysMamba, RhythmFormer, FactorizePhys
**Supported datasets:** UBFC-rPPG, PURE, SCAMPS, BP4D+, UBFC-Phys, MMPD, iBVP

Turnkey remote physiological sensing from facial video. Extracts rPPG (heart rate, HRV, BVP) without contact sensors. Research shows rPPG + pupil size + thermal = best non-contact deception detection (DDPM dataset, EER 0.357).

**Status:** Blitz Engine currently uses vitallens-python for rPPG. rPPG-Toolbox is the more research-grade alternative with access to training data and multiple model architectures (PhysMamba for accuracy, lightweight models for speed). Consider as a Phase 2 upgrade if vitallens accuracy is insufficient.

---

### 10. alicex2020/Deep-Learning-Lie-Detection
**URL:** https://github.com/alicex2020/Deep-Learning-Lie-Detection
**Tech stack:** Python, scikit-learn, Keras, MFCC, energy envelopes, pitch contours

Clean, minimal audio-only baseline. Good reference for validating the Blitz Engine audio modality plugin in isolation before full pipeline integration.

---

## ACCURACY BENCHMARKS (honest comparison)

| Approach | Dataset | Accuracy | Notes |
|---|---|---|---|
| FFCSN two-stream (CVPR 2019) | Michigan | 93.16% visual-only | Small dataset; visual-only; likely overfit |
| LoRA Calibration (ATSFace) | Michigan | 92% | Per-subject calibration; small dataset |
| LSTM+BiLSTM+BERT (4qlaa7) | Michigan | 83.05% | Subject-level, multimodal; small dataset |
| MMPDA (SVC 2025, **cross-domain**) | DOLOS | **60.43%** | **Most realistic real-world number** |
| rPPG + pupil + thermal (DDPM) | DDPM | EER 0.357 | Non-contact physiology baseline |
| Human judges (Bond & DePaulo 2006) | Various | 54-58% | Near-chance for untrained humans |
| **Blitz Engine Phase 1 target** | — | **70-75%** | With 90-180s personal calibration |
| **Blitz Engine Phase 2 target** | — | **75-80%** | With online drift correction |

**Key insight:** The 83-99% figures use Michigan (121 videos, ~60 deceptive). With subject-level splits and small N, variance is high and overfitting is easy. The SVC 2025 cross-domain result of 60.43% is the most honest real-world comparator. Our 70-75% target with personal calibration is positioned correctly.

---

## DATASETS (Free / Open Access)

| Dataset | Size | Modalities | Access | Notes |
|---|---|---|---|---|
| University of Michigan Real-Life Trial | 121 videos | Video + transcripts + physiological | Free (academic) | Standard benchmark; courtroom footage |
| MDPE | 104+ hours, 193 subjects | Video + audio + transcripts + Big Five personality | **HuggingFace (free, no request)** | Largest; includes personality scores |
| DOLOS | 1,675 clips, 213 subjects | Audio + video, MUMIN annotated | Request (NTU) | Reality TV, naturalistic |
| ATSFace | 309 clips | Video | GitHub | Student Q&A, controlled lab |
| CMU Deceptive Speech Corpus | ~100 recordings | Audio only | Free (academic) | Audio-only baseline |
| Deceptive Opinion Spam Corpus v1.4 | Text reviews | Text only | **Free** | Hotel reviews; Ott et al.; linguistic training |
| DDPM (non-contact physiology) | ~50 subjects | rPPG + pupil + thermal + video | Free (arXiv 2106.06583) | Non-contact physiology baseline |
| MuDD | 130 participants, 690 min | Video + audio + GSR + PPG + personality | Research request (paper) | Newest; includes contact physiology |

**Priority dataset for Phase 3 validation:** MDPE (HuggingFace, free, 104 hours) + Michigan (standard benchmark). Use MDPE to train linguistic plugin, Michigan for cross-dataset evaluation.

---

## NOVEL TECHNIQUES NOT YET IN BLITZ ENGINE SPEC

### 1. LoRA-Style Per-Subject Neural Calibration (ATSFace)
Our current calibration is robust Z-score normalization at the feature level. ATSFace shows that injecting low-rank adaptation matrices into the fusion layer — trained on 90-180s of individual baseline data — can push accuracy from ~70% to 92% on the same person. This is the Phase 2 upgrade path for the calibration layer.

**When to implement:** After Phase 1 baseline system is validated. Add as an optional `calibration_mode="neural"` flag alongside the existing robust-Z mode.

---

### 2. rPPG-Toolbox as vitallens Upgrade Path (rPPG-Toolbox)
Blitz Engine currently uses vitallens-python (POS/CHROM). rPPG-Toolbox (MIT, NeurIPS 2023) offers:
- PhysMamba and RhythmFormer — significantly higher accuracy than classical POS
- Access to training datasets for fine-tuning on your user population
- Multiple model sizes (speed/accuracy tradeoff)

**When to implement:** Phase 2 physiological plugin upgrade. Keep vitallens as the default (simpler, PyPI), add rPPG-Toolbox as the high-accuracy alternative.

---

### 3. GCN for Gesture/Body Pose as a Graph (CNN-GCN Study, arXiv:2411.08885)
Currently Blitz Engine treats MMPose keypoints as a flat feature vector. Graph Convolutional Networks model body landmarks as a graph where nodes are joints and edges are skeletal connections. GCN captures relational gesture patterns (self-touching, hand wringing, arm crossing) that raw coordinates miss.

**When to implement:** Phase 2 visual plugin enhancement. Replace the current pose feature flattening with a lightweight GCN layer (e.g., ST-GCN) over the 133-keypoint skeleton.

---

### 4. Pupil Diameter as an Explicit Cue (DDPM Research)
Pupil dilation is a validated deception cue (pupils dilate under cognitive load from deception). This is distinct from gaze direction. MediaPipe's iris landmark model (468-point FaceMesh includes iris) can estimate relative pupil size from video without hardware.

**Implementation:** Extract iris landmark spread (distance between outermost iris landmarks) and normalize to face size. Track delta vs. baseline. Add as `pupil_dilation_relative` cue in the visual plugin.

**Note:** The CUE_CATALOG.md already lists pupil dilation as a visual cue. This is the implementation path if it's not yet extracted.

---

### 5. Progressive Domain Adaptation for Cross-Context Generalization (MMPDA)
SVC 2025 winner explicitly addresses the failure mode our system will face: models trained on courtroom/lab footage fail on user webcam sessions. MMPDA uses adversarial feature alignment to make deception-relevant representations domain-invariant.

**When to implement:** Phase 2 after Phase 1 baseline accuracy is measured. If cross-context accuracy drops significantly, add adversarial domain discriminator on the fusion layer as a fine-tuning stage.

---

### 6. GSR-Guided Knowledge Distillation (MuDD, arXiv:2603.26064)
Architecture where a contact GSR sensor serves as a "teacher" during training, and the video/audio stream is the "student." After training, the student model has internalized physiological patterns visible in the video without needing hardware at inference time.

**Application:** If any users consent to a brief calibration session with a consumer heart rate monitor, that session can be used to distill physiological knowledge into the visual plugin. Future enhancement for Phase 4.

---

### 7. Personality Pre-Screen to Adjust Bayesian Prior (MDPE)
MDPE shows Big Five personality traits (particularly Conscientiousness and Neuroticism) modulate deception behavior significantly. Our prior is fixed at 0.30 (population-level). A brief BFI-10 questionnaire (~2 minutes, 10 questions) could adjust the prior per session:
- High Neuroticism → lower prior (more behavioral noise from anxiety, harder to distinguish)
- High Conscientiousness → slight higher sensitivity (more reliable baseline behavior)

**When to implement:** Can be added to the consent/setup flow as optional. Add `personality_prior_adjustment: float` to the session config.

---

### 8. LLM Integration for Verbal Analysis (Scientific Reports 2025)
Two 2025 papers demonstrate RoBERTa + emotion features + gradient boosting (LieXBerta) and fine-tuned FLAN-T5/Llama-3-8B outperform classical NLP for verbal deception detection. The current linguistic plugin uses hand-crafted features (spaCy, VADER, NRCLex). Dropping in a fine-tuned RoBERTa for transcript classification could meaningfully boost linguistic modality accuracy.

**When to implement:** Phase 2 linguistic plugin enhancement. Fine-tune `roberta-base` on Deceptive Opinion Spam Corpus + Michigan transcripts. Use as an additional feature alongside existing hand-crafted features, not as a replacement.

---

### 9. Temporal Gating — Weighting High-Cue Windows (DOLOS UT-Adapter)
The UT-Adapter applies temporal attention within the transformer to identify which video segments are most diagnostically informative. Our convergence gate is binary (2+ modalities must agree). A soft temporal attention mechanism that identifies specific video windows where cues peak — and weights the Bayesian update toward those windows — is the next logical refinement after Phase 1.

**When to implement:** Phase 2 fusion layer enhancement. Add a temporal attention weight to the Bayesian accumulation stage — instead of equal-weight windows, weight by `max(cue_z_scores_in_window)`.

---

### 10. MUMIN Coding Scheme for Consistent Annotation
DOLOS uses MUMIN — a standardized multimodal annotation scheme for nonverbal behavior. If Blitz Engine ever collects ground-truth sessions for evaluation, using MUMIN gives interoperability with DOLOS and other datasets.

---

## FEATURE EXTRACTION TOOLS — COMPETITIVE LANDSCAPE

| Tool | Modality | License | What it extracts | Blitz Engine status |
|---|---|---|---|---|
| OpenFace 2.0 | Visual | Apache 2.0 | 17 AU intensities, head pose 6-DOF, gaze vectors | Alternative to OpenGraphAU (less AUs but well-tested) |
| OpenGraphAU | Visual | Custom | 41 AUs (incl. asymmetric L/R) | **IN USE** |
| MediaPipe | Visual | Apache 2.0 | Face mesh 468 pts, iris, hands, body | **IN USE** |
| MMPose / rtmlib | Visual | Apache 2.0 | 133 keypoints (body + face + hands) | **IN USE** |
| OpenSmile | Audio | Custom free | 6,373 ComParE features, eGeMAPS (88 features) | Alternative to Parselmouth |
| COVAREP | Audio | GPL | Glottal source, NAQ, QOQ, H1-H2, spectral tilt | Alternative to Parselmouth for voice quality |
| wav2vec 2.0 | Audio | MIT | Self-supervised speech representations (768-dim) | Phase 2 audio feature upgrade |
| Parselmouth/Praat | Audio | GPL | Jitter, shimmer, HNR, F0, formants | **IN USE** |
| librosa | Audio | ISC | Prosody, MFCCs, spectral features | **IN USE** |
| rPPG-Toolbox | Physiological | MIT | HR, HRV, BVP from facial video | Alternative to vitallens |
| vitallens-python | Physiological | Custom free | HR, HRV, PPG waveform from facial video | **IN USE** |
| BERT/RoBERTa | Linguistic | Apache 2.0 | Contextual text embeddings | Phase 2 linguistic upgrade |
| spaCy + VADER + NRCLex | Linguistic | MIT/Apache | POS, sentiment, emotions | **IN USE** |

---

## ACTIONABLE ENHANCEMENTS (Ranked by effort vs. gain)

| Priority | Enhancement | Effort | Gain | Phase |
|---|---|---|---|---|
| 1 | Pupil diameter extraction via MediaPipe iris landmarks | Low | Incremental | Phase 1 (add cue) |
| 2 | MDPE dataset (HuggingFace, free) for training + evaluation | Low | High (104 hrs vs. 121 clips) | Phase 3 |
| 3 | Deceptive Opinion Spam Corpus for linguistic training | Low | Solid | Phase 3 |
| 4 | rPPG-Toolbox as high-accuracy vitallens upgrade | Medium | Better physio accuracy | Phase 2 |
| 5 | Fine-tuned RoBERTa in linguistic plugin | Medium | +5-10% linguistic accuracy | Phase 2 |
| 6 | BFI-10 personality pre-screen → adjusted prior | Low | Novel, differentiating | Phase 2 |
| 7 | Temporal attention weighting in Bayesian fusion | Medium | Architectural improvement | Phase 2 |
| 8 | GCN over MMPose skeleton for gesture modeling | Medium-High | Better gesture patterns | Phase 2 |
| 9 | LoRA-style per-subject calibration layer | High | 70% → 92% per-person | Phase 2 |
| 10 | MMPDA cross-domain adaptation | High | Fixes real-world distribution shift | Phase 3 |

---

## KEY INSIGHT: WHY ACCURACY NUMBERS LIE

Most published results use the University of Michigan dataset (121 videos, ~60 deceptive). Subject-level splits with N=121 have very high variance — a 5% accuracy swing is noise. Papers reporting 83-99% are measuring in-distribution performance on a tiny, overfitted sample.

**The SVC 2025 cross-domain result (60.43%) is the honest floor for real-world deployment.**

Blitz Engine's 70-75% Phase 1 target is achievable specifically because of personal calibration — which papers don't implement, because it requires per-subject baselines. Our competitive advantage isn't a better model, it's a better measurement system.

---

## REFERENCES

- [Redaimao/awesome-multimodal-deception-detection](https://github.com/Redaimao/awesome-multimodal-deception-detection)
- [DOLOS + PECL (ICCV 2023)](https://arxiv.org/abs/2303.12745)
- [MDPE Dataset Paper (arXiv:2407.12274)](https://arxiv.org/abs/2407.12274)
- [MDPE HuggingFace](https://huggingface.co/datasets/MDPEdataset/MDPE_Dataset)
- [DDV (CVPRW 2019)](https://github.com/Sutadasuto/DDV)
- [4qlaa7/Multimodal_Deception_Detection](https://github.com/4qlaa7/Multimodal_Deception_Detection)
- [ritikamotwani/Deception-Detection](https://github.com/ritikamotwani/Deception-Detection)
- [MMPDA SVC 2025 (arXiv:2508.04129)](https://arxiv.org/abs/2508.04129)
- [ATSFace LoRA Calibration (arXiv:2309.01383)](https://arxiv.org/abs/2309.01383)
- [rPPG-Toolbox (NeurIPS 2023)](https://github.com/ubicomplab/rPPG-Toolbox)
- [MuDD Dataset (arXiv:2603.26064)](https://arxiv.org/abs/2603.26064)
- [CNN/GCN Comparative Study (arXiv:2411.08885)](https://arxiv.org/abs/2411.08885)
- [DDPM Non-Contact Physiology (arXiv:2106.06583)](https://arxiv.org/abs/2106.06583)
- [LLM Deception Detection — Scientific Reports 2025](https://www.nature.com/articles/s41598-025-92399-6)
- [LieXBerta — Scientific Reports](https://www.nature.com/articles/s41598-025-17741-4)
- [alicex2020/Deep-Learning-Lie-Detection](https://github.com/alicex2020/Deep-Learning-Lie-Detection)
