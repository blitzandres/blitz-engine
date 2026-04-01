# Blitz Engine — Intended Use Policy

## What This Is

Blitz Engine is an open-source behavioral deception signal analyzer built on peer-reviewed deception research. It uses 66 behavioral cues across 5 modality families and Bayesian fusion to compute a deception signal probability.

It is a **research and educational tool**. It is not a product. It is not a service. It is not a weapon.

---

## Intended Users

- Behavioral science researchers
- Academic institutions (with IRB approval)
- Investigative journalists (as supplementary context only)
- Developers building behavioral analysis applications for research
- Individuals exploring behavioral science on consented subjects

---

## Intended Context

- Laboratory research environments
- Academic demonstrations and teaching
- Investigative journalism with proper editorial oversight
- Personal exploration with explicit mutual consent

---

## Required Conditions for All Use

1. **Consent** — The subject must consent to behavioral analysis
2. **Disclosure** — Subject must be informed that Blitz Engine is ~70-75% accurate with ~25-30% false positive rate
3. **Human review** — No automated decision may be made based solely on Blitz Engine output
4. **Appropriate expertise** — User must understand the limitations before interpreting results

---

## The "Not For Sole Decision" Principle

Every Blitz Engine output includes:

```json
"compliance": {
  "not_for_sole_decision": true
}
```

This flag is hardcoded. It cannot be disabled. It is a reminder that Blitz Engine output is **one signal among many**, never a verdict.

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 0.1.0 | 2026-03 | Planning complete, pre-implementation |
