"""
barotrauma.v2.types
===================

Typed data structures for the v2 MEB risk pipeline: patient state, chamber
profile, simulation result, risk result.

All dataclasses here are immutable (``frozen=True``) except the mutable
``SimulationResult`` container for trace arrays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

# ------------------------------------------------------------------ enums --
# Explicit Literal types rather than enum classes keep the public API trivial
# to serialize (JSON / Streamlit widgets / CLI args) and match the research
# brief tables exactly.

UriState = Literal[
    "none",
    "day_1_3",
    "day_4_7",
    "day_8_14",
    "day_15_21",
    "day_22_28",
]
"""URI temporal state used by the pathophysiology modifier layer."""

PetState = Literal["normal", "s1", "s2", "s3", "s4"]
"""Patulous ET state. S1 baseline-patent · S2 PET+edema · S3 sniffer · S4 post-plug.
The state machine is implemented in ``pathophysiology._pet_modifiers``."""

EtSeverity = Literal["normal", "mild", "moderate", "severe"]
"""Obstructive ET dysfunction severity (independent of PET / URI)."""

ChronicRhinitis = Literal["none", "allergic", "chronic_rhinosinusitis"]

MedicationEffect = Literal[
    "none",
    "pseudoephedrine_oral",
    "oxymetazoline_topical",
    "intranasal_steroid",
    "antihistamine_spray",
]


# ------------------------------------------------------- patient state ---
@dataclass(frozen=True)
class PatientAnatomy:
    """
    Individual anatomical parameters. Defaults = Kanick-Doyle 2005 Table 1.

    Mastoid volume is the dominant inter-subject source of variance
    (~10× range 2–15 mL; Alper 2011 PMID 21271597). Expose as a free parameter
    rather than hard-coding.
    """

    tympanum_volume_ml: float = 1.0              # Kanick-Doyle 2005
    mastoid_volume_ml: float = 7.75              # Kanick-Doyle 2005 (adult mean)
    tm_area_cm2: float = 0.6                     # Kanick-Doyle 2005
    tm_stiffness_mmHg_per_ml: float = 179.0      # Kanick-Doyle 2005
    tm_max_displacement_ml: float = 0.025        # Kanick-Doyle 2005 (~1% Vme)
    age_years: int = 30
    sex: Literal["male", "female", "unspecified"] = "unspecified"

    @property
    def me_volume_ml(self) -> float:
        return self.tympanum_volume_ml + self.mastoid_volume_ml

    def validate(self) -> None:
        if self.tympanum_volume_ml <= 0:
            raise ValueError("tympanum_volume_ml must be positive")
        if self.mastoid_volume_ml <= 0:
            raise ValueError("mastoid_volume_ml must be positive (2–15 mL typical)")
        if self.tm_max_displacement_ml <= 0:
            raise ValueError("tm_max_displacement_ml must be positive")
        if self.age_years < 0 or self.age_years > 120:
            raise ValueError("age_years out of range")


@dataclass(frozen=True)
class EtFunction:
    """
    Eustachian-tube function, adult disease-free defaults from Kanick-Doyle
    2005 Table 1 (SI units converted: 350 mmH2O ≈ 25.7 mmHg, etc.).

    All values are ReferencedtoAmbient (P_opening - P_ambient) unless noted.
    """

    severity: EtSeverity = "normal"

    # Pressure-response parameters (Kanick-Doyle 2005; Alper 2020 PMID 32176133)
    passive_opening_mmHg_me: float = 25.7         # P_ME-ET^O'  (350 mmH2O)
    passive_opening_mmHg_np: float = 44.1         # P_NP-ET^O'  (600 mmH2O)
    closing_mmHg: float = 7.35                    # P_C'        (100 mmH2O)

    # Active (muscle-assisted) opening
    active_resistance_mmHg_ml_min: float = 2.0    # R_A
    active_open_duration_s: float = 0.25          # T_A
    swallow_freq_per_hr_cruise: float = 5.2       # S_f at rest (KD2005)
    swallow_freq_per_hr_descent: float = 60.0     # S_f during descent
                                                  # (trained aircrew — 31.0 for
                                                  # Kanick-Doyle passive baseline)
    fge_controls: float = 0.32                    # Fractional gradient equalized
                                                  # per swallow (Mandel 2016)

    def validate(self) -> None:
        if self.passive_opening_mmHg_me <= 0:
            raise ValueError("passive_opening_mmHg_me must be positive")
        if self.active_resistance_mmHg_ml_min <= 0:
            raise ValueError("active_resistance_mmHg_ml_min must be positive")
        if self.active_open_duration_s <= 0:
            raise ValueError("active_open_duration_s must be positive")
        if self.swallow_freq_per_hr_cruise < 0 or self.swallow_freq_per_hr_descent < 0:
            raise ValueError("swallow frequencies must be non-negative")
        if not 0 <= self.fge_controls <= 1:
            raise ValueError("fge_controls must be in [0,1]")


@dataclass(frozen=True)
class PatientState:
    """
    Full patient snapshot for a single chamber exposure.

    Combines anatomy (slow variables) + ET function + acute state (URI/PET)
    + comorbidities + medications.
    """

    anatomy: PatientAnatomy = field(default_factory=PatientAnatomy)
    et: EtFunction = field(default_factory=EtFunction)

    # Acute / subacute state
    uri: UriState = "none"
    pet: PetState = "normal"
    rhinitis: ChronicRhinitis = "none"

    # History
    previous_meb: bool = False

    # Medications (at time of exposure)
    medication: MedicationEffect = "none"

    # Behavior during exposure
    enable_valsalva: bool = True
    valsalva_interval_s: float = 60.0   # every ~60 s in chamber trainees
    habitual_sniffer: bool = False      # Shindo 2025 type-B/C tymp in 42.6%

    # v2.3.0 covariates from the 2025-2026 literature scan; citation notes
    # for the corresponding RRs live in constants.py.
    sensory_neuropathy: bool = False
    """Voigt 2025 (PMID 41429031): risk factor for MEB in HBOT pooled MA.
    RR applied in pathophysiology.modifiers_for_patient via
    constants.SENSORY_NEUROPATHY_RR."""

    impaired_volitional_equalization: bool = False
    """Lee 2025 (PMID 40364015, 40288902): altered mental status OR
    2.50-3.16 across two HBOT cohorts. Applies to sedated HBOT,
    intoxicated aeromedical evacuation, post-op altered sensorium."""

    glp1_exposure: bool = False
    """Sudhoff 2025 (PMID 40721956): semaglutide/tirzepatide-induced PET
    via Ostmann fat-pad atrophy during 8.2-18.7% weight loss. Low
    confidence (case series). Applied as a narrow precautionary modifier."""

    bdet_treated: bool = False
    """Swords 2025 Cochrane (PMID 40008607) + Khan 2026 (PMID 41776716):
    prior balloon dilation of the Eustachian tube. When True, partially
    restores ET function via ra_mult 0.70, opening-shift −5 mmHg,
    eq_rate_mult 1.20, and per-descent RR 0.65. Contraindicated in PET;
    the pathophysiology layer surfaces a clinical-decision-support note
    when bdet_treated is set alongside a non-normal PET state."""

    def validate(self) -> None:
        self.anatomy.validate()
        self.et.validate()
        if self.valsalva_interval_s <= 0:
            raise ValueError("valsalva_interval_s must be positive")


# ----------------------------------------------------- chamber profile ---
@dataclass(frozen=True)
class ChamberSegment:
    """One segment of a chamber profile."""

    duration_s: float
    end_altitude_ft: float
    label: str = ""

    def validate(self) -> None:
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        if self.end_altitude_ft < 0:
            raise ValueError("end_altitude_ft must be non-negative")


@dataclass(frozen=True)
class ChamberProfile:
    """
    Piecewise-linear pressure profile for a hypobaric chamber run.

    Starts at ``start_altitude_ft`` and marches through segments. Each segment
    specifies the target altitude at its end and the time to reach it. This
    captures ascents, holds, descents, and rapid decompression events.
    """

    name: str
    start_altitude_ft: float
    segments: tuple[ChamberSegment, ...]

    def validate(self) -> None:
        if self.start_altitude_ft < 0:
            raise ValueError("start_altitude_ft must be non-negative")
        if not self.segments:
            raise ValueError("profile must have at least one segment")
        for seg in self.segments:
            seg.validate()

    def total_duration_s(self) -> float:
        return sum(s.duration_s for s in self.segments)


# ------------------------------------------------------------ results ---
@dataclass
class SimulationTrace:
    """Time-domain simulation output."""

    t_s: NDArray[np.float64]
    altitude_ft: NDArray[np.float64]
    p_ambient_mmHg: NDArray[np.float64]
    p_me_mmHg: NDArray[np.float64]
    delta_p_mmHg: NDArray[np.float64]        # P_ME - P_ambient (negative on descent)
    tm_displacement_ml: NDArray[np.float64]
    et_open: NDArray[np.bool_]                # binary indicator per step
    swallow_events_s: NDArray[np.float64]     # timestamps of swallow events
    valsalva_events_s: NDArray[np.float64]    # timestamps of Valsalva attempts

    def dt(self) -> float:
        return float(self.t_s[1] - self.t_s[0]) if len(self.t_s) > 1 else 0.0

    def step_durations_s(self) -> NDArray[np.float64]:
        """Per-sample integration weights; first sample has zero elapsed time."""
        if len(self.t_s) == 0:
            return np.asarray([], dtype=np.float64)
        return np.diff(self.t_s, prepend=self.t_s[0]).astype(np.float64)

    def max_abs_delta_p(self) -> float:
        return float(np.max(np.abs(self.delta_p_mmHg)))

    def time_above(self, threshold_mmHg: float) -> float:
        """Seconds spent with |ΔP| > threshold."""
        if len(self.t_s) < 2:
            return 0.0
        weights = self.step_durations_s()
        return float(np.sum((np.abs(self.delta_p_mmHg) > threshold_mmHg) * weights))

    def auc_abs_delta_p(self, threshold_mmHg: float = 0.0) -> float:
        """∫ max(0, |ΔP| - threshold) dt — dose-response exposure integral."""
        if len(self.t_s) < 2:
            return 0.0
        weights = self.step_durations_s()
        excess = np.clip(np.abs(self.delta_p_mmHg) - threshold_mmHg, 0.0, None)
        return float(np.sum(excess * weights))


@dataclass(frozen=True)
class RiskResult:
    """
    Outputs of the hazard model for a single simulated exposure.

    ``p_barotitis`` is any-grade MEB (Teed I+, ~barotitis onset at ~18 mmHg).
    ``p_baromyringitis`` is severe (Teed III–IV hemorrhage, ~96 mmHg).
    ``p_rupture`` is TM perforation (Teed V, conservative 150 mmHg).

    Each probability includes an approximate 95% credible interval from
    Monte-Carlo draws over physiological priors (None if not sampled).
    """

    p_barotitis: float
    p_baromyringitis: float
    p_rupture: float
    max_abs_delta_p_mmHg: float
    auc_mmHg_s_barotitis: float
    auc_mmHg_s_baromyringitis: float
    dominant_risk_factor: str
    recommended_max_descent_ft_min: float
    ci95_barotitis: tuple[float, float] | None = None
    ci95_baromyringitis: tuple[float, float] | None = None
    ci95_rupture: tuple[float, float] | None = None

    def risk_category(self) -> Literal["low", "moderate", "high", "very_high"]:
        p = self.p_barotitis
        if p < 0.05:
            return "low"
        if p < 0.20:
            return "moderate"
        if p < 0.50:
            return "high"
        return "very_high"


@dataclass(frozen=True)
class SimulationResult:
    """Combined trace + risk + metadata."""

    trace: SimulationTrace
    risk: RiskResult
    patient: PatientState
    profile: ChamberProfile
    notes: Sequence[str] = ()
