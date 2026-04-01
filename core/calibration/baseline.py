"""
Blitz Engine — Personal Baseline Calibration
The most important layer for accuracy. Separates naturally-anxious from lying.

Method: 3-component hierarchical model
    Observed cue = TRAIT (stable baseline)
                 + STATE reactivity (stress from hard questions, not lying)
                 + DECEPTION residual (what we detect)

Normalization: Robust Z using Median Absolute Deviation
    z_robust = (x - median) / (1.4826 × MAD)

Baseline requirements:
    - Minimum: 90 seconds neutral speech (NOT 30-60s as often assumed)
    - Ideal: 180 seconds with 2+ neutral topics
    - Session drift correction every 5 minutes

References:
    - Bogaard et al. (2024) — doi:10.1016/j.actpsy.2023.104112
      Found no strong evidence that simple deviation-from-baseline is reliable alone.
    - DePaulo (2003) — person-specific variability is large; population thresholds brittle.

Status: PLACEHOLDER — implementation pending Phase 1 build authorization.
"""
import statistics
from typing import List, Optional


MINIMUM_BASELINE_SECONDS = 90    # Research-updated minimum (was 30-60s)
IDEAL_BASELINE_SECONDS = 180


def compute_robust_z(value: float, baseline_values: List[float]) -> float:
    """
    Robust Z-score using Median Absolute Deviation.
    Resistant to outliers unlike standard Z.

    z_robust = (x - median) / (1.4826 × MAD)
    The 1.4826 factor makes MAD consistent with std under normality.
    """
    if len(baseline_values) < 5:
        raise ValueError(f"Need at least 5 baseline observations, got {len(baseline_values)}")

    med = statistics.median(baseline_values)
    mad = statistics.median([abs(v - med) for v in baseline_values])

    if mad == 0:
        return 0.0  # No variation in baseline

    return (value - med) / (1.4826 * mad)


def apply_empirical_bayes_shrinkage(z_raw: float, n_obs: int, n_target: int = 30) -> float:
    """
    Shrink Z-score toward 0 (population mean) when baseline is short.
    Prevents overconfident calibration from short baselines.

    lambda = min(1.0, n_obs / n_target)
    z_shrunk = lambda × z_raw + (1 - lambda) × 0
    """
    lam = min(1.0, n_obs / n_target)
    return lam * z_raw


class PersonalBaseline:
    """
    Manages the personal baseline for a single session.
    Implementation pending Phase 1 build authorization.
    """

    REQUIRED_BASELINE_TOPICS = [
        "Tell me about your commute this morning.",
        "Describe your favorite meal.",
        "What did you do last weekend?"
    ]

    def __init__(self):
        self.trait_stats: dict = {}         # Per-cue: median, MAD
        self.stress_stats: dict = {}        # From neutral-stressful control questions
        self.baseline_duration_s: float = 0
        self.is_sufficient: bool = False

    def record_baseline(self, cue_observations: dict, duration_s: float):
        """Record baseline observations for all cues."""
        raise NotImplementedError("Pending Phase 1 build authorization.")

    def normalize(self, cue_id: str, raw_value: float) -> float:
        """Return robust Z-score vs personal baseline for a cue."""
        raise NotImplementedError("Pending Phase 1 build authorization.")

    def quality_report(self) -> dict:
        """Return baseline quality assessment."""
        return {
            "duration_s": self.baseline_duration_s,
            "is_sufficient": self.is_sufficient,
            "minimum_required_s": MINIMUM_BASELINE_SECONDS,
            "warning": None if self.is_sufficient else
                       f"Baseline {self.baseline_duration_s:.0f}s < required {MINIMUM_BASELINE_SECONDS}s"
        }
