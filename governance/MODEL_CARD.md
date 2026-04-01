# Blitz Engine — Model Card

## Model Details

| Field | Value |
|---|---|
| Name | Blitz Engine |
| Version | 0.1.0 (pre-release) |
| Type | Rule-based Bayesian fusion + pre-trained feature extractors |
| Primary use | Behavioral deception signal analysis for research |
| License | Apache 2.0 |
| Status | Planning complete — not yet implemented |

---

## Intended Use

**Primary use cases:**
- Academic research on behavioral deception signals
- Educational demonstrations of multimodal behavioral analysis
- Journalism investigative support (contextual only)
- Personal behavioral science exploration with consented subjects

**Out-of-scope uses:**
See [PROHIBITED_USES.md](PROHIBITED_USES.md).

---

## Training Data

Blitz Engine uses **no trained models for deception classification**. The fusion weights are derived from published meta-analyses:
- Effect sizes from DePaulo et al. 2003 (158 cues, meta-analysis)
- Sporer & Schwandt 2006/2007 (nonverbal and paraverbal meta-analyses)
- CBCA reliability meta-analysis (Amado et al. 2016)

The pre-trained feature extractors (MediaPipe, OpenGraphAU, InsightFace, etc.) were trained on their respective original datasets — see each library's model card for details.

---

## Performance

### Overall System

| Setting | Accuracy | Notes |
|---|---|---|
| Human judges (literature baseline) | 54% | Bond & DePaulo 2006 |
| SVC 2025 winner (cross-domain) | ~62% | Hard setting |
| Blitz Engine Phase 1 target | 70-75% | With personal calibration |
| Blitz Engine Phase 2 target | 75-80% | With drift correction |

**Note:** System has not yet been implemented. These are research-validated targets, not measured results.

### Known Performance Limitations

- rPPG accuracy degrades 2-5x under H.264 video compression (MAE 5-10 BPM vs 2 BPM in papers)
- Performance drops significantly in cross-domain settings (different lighting, camera, interview format)
- Requires minimum 480p @ 15fps front-facing video
- Personal baseline requires 90-180s of neutral speech footage

---

## Bias & Fairness

### Known Biases

| Subgroup | Known issue | Mitigation |
|---|---|---|
| Skin tone | rPPG error higher on darker skin | Multi-ROI methods reduce (not eliminate) |
| Gender | Vocal F0 baseline differs by sex | Speaker-normalized prosody (semitone-relative) |
| Culture | Eye contact, gesture norms vary | Person-relative baseline (not population) |
| Age | Blink rate, voice tremor change with age | Personal baseline required |

### Fairness Testing Planned

Phase 3 will include subgroup accuracy audits by:
- Gender (male/female/non-binary)
- Approximate skin tone category (Fitzpatrick scale)
- Language/accent background
- Age group

---

## Ethical Considerations

- False positive rate: ~25-30%
- Output must never be sole basis for decisions about people
- Consent required for every analysis
- Full ethics framework: [ETHICS.md](ETHICS.md)
- Prohibited uses: [PROHIBITED_USES.md](PROHIBITED_USES.md)
- EU AI Act (2024/1689) applies

---

## Caveats and Recommendations

1. Always use personal baseline calibration — population thresholds are brittle
2. Require convergence across ≥2 independent modality families before flagging
3. Report uncertainty bounds, not point estimates
4. Validate on your specific target population before any operational use
5. Review output with a domain expert before drawing conclusions

---

## Contact & Reporting

- Ethics concerns: open a GitHub issue tagged `ethics-concern`
- Accuracy issues: open a GitHub issue tagged `accuracy`
- Misuse reports: open a GitHub issue tagged `misuse`
