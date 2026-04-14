"""Runnable text-first Blitz Engine MVP."""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional

from core.calibration.baseline import PersonalBaseline
from core.fusion.bayesian_fusion import DEFAULT_PRIOR, convergence_gate_passed, fuse
from core.schemas.cue_event import BlitzOutput
from modalities.linguistic import LinguisticAnalyzer


ALLOWED_MODALITIES = {"linguistic"}


class BlitzEngine:
    """Coordinates enabled modalities and creates analysis sessions."""

    def __init__(
        self,
        modalities: Optional[List[str]] = None,
        prior: float = DEFAULT_PRIOR,
        convergence_threshold: float = 0.65,
    ):
        self.modalities = modalities or ["linguistic"]
        unsupported = [modality for modality in self.modalities if modality not in ALLOWED_MODALITIES]
        if unsupported:
            raise ValueError(
                f"Unsupported modalities for current MVP: {', '.join(unsupported)}. "
                "Only 'linguistic' is implemented."
            )

        self.prior = prior
        self.convergence_threshold = convergence_threshold
        self.linguistic = LinguisticAnalyzer() if "linguistic" in self.modalities else None

    def new_session(
        self,
        baseline_texts: List[str],
        consent: bool,
        use_case: str,
        jurisdiction: str,
        baseline_duration_s: Optional[float] = None,
        baseline_latencies_ms: Optional[List[int]] = None,
    ) -> "BlitzSession":
        if not consent:
            raise ValueError("Consent must be declared to create a session.")

        if not baseline_texts:
            raise ValueError("baseline_texts cannot be empty")

        baseline = PersonalBaseline()
        observations: Dict[str, List[float]] = {}
        if self.linguistic:
            observations.update(
                self.linguistic.build_baseline_observations(
                    baseline_texts=baseline_texts,
                    baseline_latencies_ms=baseline_latencies_ms,
                )
            )

        if baseline_duration_s is None:
            baseline_duration_s = max(90.0, float(len(baseline_texts) * 30))

        baseline.record_baseline(observations, duration_s=baseline_duration_s)
        return BlitzSession(
            engine=self,
            baseline=baseline,
            use_case=use_case,
            jurisdiction=jurisdiction,
            consent=consent,
        )


class BlitzSession:
    """Single-subject calibrated analysis session."""

    def __init__(
        self,
        engine: BlitzEngine,
        baseline: PersonalBaseline,
        use_case: str,
        jurisdiction: str,
        consent: bool,
    ):
        self.engine = engine
        self.baseline = baseline
        self.use_case = use_case
        self.jurisdiction = jurisdiction
        self.consent = consent
        self.session_id = str(uuid.uuid4())
        self.question_counter = 0

    def analyze_text(
        self,
        response_text: str,
        question: Optional[str] = None,
        question_id: Optional[str] = None,
        response_latency_ms: Optional[int] = None,
    ) -> BlitzOutput:
        if not response_text.strip():
            raise ValueError("response_text cannot be empty")

        self.question_counter += 1
        resolved_question_id = question_id or f"q{self.question_counter}"
        cues = []
        if self.engine.linguistic:
            cues.extend(
                self.engine.linguistic.analyze(
                    text=response_text,
                    question_id=resolved_question_id,
                    baseline=self.baseline,
                    response_latency_ms=response_latency_ms,
                    timestamp_ms=int(time.time() * 1000),
                )
            )

        fused = fuse(cues, prior=self.engine.prior)
        posterior = fused["posterior"]
        gate_passed = convergence_gate_passed(
            cues,
            threshold=self.engine.convergence_threshold,
            posterior=posterior,
        )
        narrative = self._build_narrative(
            question=question,
            response_text=response_text,
            posterior=posterior,
            gate_passed=gate_passed,
            top_cues=fused["top_cues"],
        )

        quality_flags = {
            "baseline": self.baseline.quality_report(),
            "implemented_modalities": self.engine.modalities,
            "input_mode": "text",
            "convergence_gate_passed": gate_passed,
        }

        return BlitzOutput(
            session_id=self.session_id,
            question_id=resolved_question_id,
            timestamp_ms=int(time.time() * 1000),
            risk_score=posterior,
            uncertainty=fused["uncertainty"],
            confidence_interval=fused["confidence_interval"],
            channel_contributions=fused["channel_contributions"],
            top_cues=[self._serialize_cue(cue) for cue in fused["top_cues"]],
            quality_flags=quality_flags,
            narrative=narrative,
            compliance={
                "not_for_sole_decision": True,
                "use_case": self.use_case,
                "consent_declared": self.consent,
                "jurisdiction": self.jurisdiction,
            },
        )

    def analyze(self, *args, **kwargs) -> BlitzOutput:
        """Alias retained for the current MVP surface."""
        return self.analyze_text(*args, **kwargs)

    def _build_narrative(
        self,
        question: Optional[str],
        response_text: str,
        posterior: float,
        gate_passed: bool,
        top_cues: List,
    ) -> str:
        cue_names = ", ".join(cue.cue_id.rsplit(".", 1)[-1] for cue in top_cues[:3]) or "no strong cues"
        status = "elevated" if gate_passed else "below convergence threshold"
        question_text = f" Question: {question}." if question else ""
        return (
            f"Text-only MVP assessment is {status} with posterior {posterior:.2f}.{question_text} "
            f"Primary linguistic drivers: {cue_names}. "
            f"This output is a research aid and not a factual lie determination."
        )

    def _serialize_cue(self, cue) -> dict:
        return {
            "cue_id": cue.cue_id,
            "modality": cue.modality.value,
            "timestamp_ms": cue.timestamp_ms,
            "phase": cue.phase.value,
            "raw_value": cue.raw_value,
            "z_score": cue.z_score,
            "llr": cue.llr,
            "quality": cue.quality,
            "question_id": cue.question_id,
            "on_word": cue.on_word,
            "effect_size_d": cue.effect_size_d,
            "reliability_tier": cue.reliability_tier,
        }
