# Blitz Engine — Diagram Drafts

These Mermaid files are planning-ready diagram drafts for the Blitz Engine.

## Files

### Process Diagrams (user-facing, embedded in README)
- `user_session_flow.mmd` — full user journey: consent → baseline → analysis → output
- `adapter_architecture.mmd` — how CLI / API / Chrome Extension / SDK connect to the core
- `build_phases.mmd` — development roadmap across all 4 phases with accuracy targets
- `data_states_privacy.mmd` — data states + privacy boundary: RawInput → CuePacket → FinalReport

### Technical Diagrams (detailed internals, embedded in README)
- `modality_pipeline.mmd` — all 5 modality chains with actual packet names, libraries, and trigger events
- `fusion_detail.mmd` — fusion stages 1-4 with full Bayesian formula, convergence gate, and output construction

### Engine Diagrams (original, for diagrams.net)
- `data_transaction_flow.mmd` — end-to-end data movement from capture to report
- `engine_queue_flow.mmd` — worker/queue pipeline for the engine runtime

## How to use in diagrams.net

1. Open the target board in diagrams.net.
2. Use `Arrange` -> `Insert` -> `Advanced` -> `Mermaid`.
3. Paste the contents of one `.mmd` file.
4. Insert, then style or reposition as needed.

## Intent

These flows reflect the current planning source of truth in:

- `../PROJECT_MAP.md`
- `../BLITZ_ENGINE_SPEC.md`
- `../ACCURACY_PLAN.md`
- `../RESEARCH.md`

If those planning docs change, update these diagrams from the repo copy first.
