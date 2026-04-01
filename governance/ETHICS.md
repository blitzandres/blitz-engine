# Blitz Engine — Ethics Framework

## Core Principle

Blitz Engine is a **behavioral signal analyzer**, not a lie detector.

It computes a posterior probability that observed behavioral signals are consistent with deception patterns documented in peer-reviewed literature. It does NOT read minds. It does NOT detect lies with certainty. Its false positive rate is approximately 25-30%.

---

## What Blitz Engine Is

- A research tool for studying behavioral deception signals
- An educational demonstration of multimodal behavioral analysis
- A journalism aid for investigative context (not evidence)
- A personal exploration tool for behavioral science

---

## What Blitz Engine Is NOT

- A polygraph replacement
- A court-admissible lie detector
- A tool for making decisions about people
- A surveillance system
- A diagnostic instrument

---

## Accuracy Disclosure (Required in All Deployments)

Every deployment must display this disclosure before use:

```
BLITZ ENGINE ETHICAL DISCLOSURE

This system analyzes behavioral patterns associated with deception.
It does NOT detect lies with certainty.

Accuracy: 70-75% (vs 54% human baseline)
False positive rate: ~25-30%

This output is a probability, not a verdict.
A high risk score does NOT mean someone is lying.
Do not use to make decisions about people without additional evidence.
Consent of the subject is required.
```

---

## Mandatory API Fields

Every API call must include:

| Field | Purpose |
|---|---|
| `consent: true` | Caller declares consent was obtained |
| `use_case` | One of: research \| education \| journalism \| personal \| other |
| `jurisdiction` | For legal compliance awareness |

The `not_for_sole_decision: true` flag is always returned and cannot be suppressed.

---

## Protected Groups

The system has been designed to minimize demographic bias, but known limitations exist:

- rPPG heart rate extraction has higher error on darker skin tones (MAE 14.1 bpm vs 5.2 bpm for lighter skin tones in traditional methods)
- Blitz Engine uses multi-ROI methods that partially mitigate this, but the bias has not been eliminated
- Gender differences in vocal cues exist at the physiological level; Blitz Engine uses speaker-normalized features to mitigate but not eliminate this
- Cultural differences in eye contact norms, gesture, and linguistic style affect cue reliability

**The system must be validated on your specific target population before any operational use.**

---

## EU AI Act Compliance

Under EU Regulation 2024/1689, behavioral analysis directed at individuals may qualify as a **high-risk AI system** or, in some contexts, a **prohibited practice**.

Specifically prohibited (Article 5):
- Emotion recognition in workplaces or educational institutions
- Real-time remote biometric identification in public spaces

High-risk (Annex III) if used for:
- Employment and worker management
- Access to essential private services
- Law enforcement
- Migration and border control

**Do not deploy Blitz Engine in any EU-regulated context without legal review.**

---

## Research Use Guidelines

When using Blitz Engine for academic research:
1. Obtain IRB/ethics board approval before analyzing real subjects
2. Anonymize all output data
3. Do not store video footage longer than necessary
4. Report findings with uncertainty bounds, not point estimates
5. Acknowledge the 25-30% false positive rate in publications

---

## Reporting Misuse

If you observe Blitz Engine being used in violation of these guidelines, please open a GitHub issue tagged `ethics-concern` or email the maintainers directly.
