# Voice Segment

> Standalone voice-only deception detection — no video required.

This segment covers the **Voice App**: a mic-native, recorder-compatible analysis tool that detects behavioral stress signals from audio alone. It is designed to work in situations where video is unavailable — phone calls, audio interviews, voice memos, field recordings, interrogation recordings.

---

## Why Voice-Only

Most real-world deception detection happens without video. The full Blitz Engine assumes video + audio + linguistic layers. The Voice Segment is different:

- Works from a laptop mic, USB mic, or external voice recorder
- No camera required, no face tracking dependency
- Deployable in privacy-sensitive environments
- Lower compute — runs on modest hardware

Voice-only accuracy is lower than the full multimodal engine (expected ~62-68% vs 70-75% target for Phase 1), but it covers a much wider set of real-world use cases.

---

## Two Modes

### 1. Live Mode — Low Latency
**Use when:** You are in an active conversation and want real-time indicators.

- Streams directly from microphone
- Processes audio in 1-2 second sliding windows
- Triggers alert (visual flash / bell) when 3+ cues cross threshold simultaneously
- Target response time: **<500ms from event to alert**
- Uses lightweight cue subset (pitch, jitter, pauses, speech rate)
- Designed to not break conversation flow — subtle, not intrusive

### 2. Review Mode — High Accuracy
**Use when:** You have a recording and want a full behavioral analysis after the fact.

- Accepts audio file (WAV, MP3, M4A) or saved live capture
- No latency constraint — runs all 8 cues with full Parselmouth + openSMILE pipeline
- Segments audio by question/answer turns if timestamps are provided
- Outputs timestamped report with per-cue firing, z-scores, and behavioral pattern
- Exportable as JSON + human-readable summary

---

## Documents in This Folder

| File | Purpose |
|---|---|
| [VOICE_CUES.md](VOICE_CUES.md) | The 8-cue selection — why these 8, interference analysis, cue family groupings |
| [APP_SPEC.md](APP_SPEC.md) | Full technical specification — architecture, latency design, tech stack, input/output schema |

---

## Relationship to Full Engine

The Voice Segment is a **subset** of the full Blitz Engine audio layer. The full cue catalog (13 audio cues + 53 others across 5 modalities) is documented in [`docs/CUE_CATALOG.md`](../docs/CUE_CATALOG.md).

The Voice App uses 8 of those audio cues, selected specifically for:
- Low mutual interference (independent signals)
- Real-time extractability (no multi-second lookahead required)
- Robustness without video calibration anchor

See [VOICE_CUES.md](VOICE_CUES.md) for the full selection rationale.
