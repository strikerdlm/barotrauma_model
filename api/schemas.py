"""
api.schemas
===========

Pydantic v2 request/response models that mirror the ``barotrauma.v2``
dataclasses. Kept deliberately flat and serializable so the TypeScript
frontend can map them one-for-one.

Conversion helpers (``to_patient_state``, ``to_chamber_profile``) turn the
inbound Pydantic models into the frozen v2 dataclasses the engine expects.
The response models accept either point estimates or Monte-Carlo CIs.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from barotrauma.v2.types import (
    ChamberProfile,
    ChamberSegment,
    EtFunction,
    PatientAnatomy,
    PatientState,
    RiskResult,
    SimulationResult,
    SimulationTrace,
)


_STRICT = ConfigDict(extra="forbid")


# =========================================================== request ===
class PatientAnatomyRequest(BaseModel):
    model_config = _STRICT
    tympanum_volume_ml: float = 1.0
    mastoid_volume_ml: float = 7.75
    tm_area_cm2: float = 0.6
    tm_stiffness_mmHg_per_ml: float = 179.0
    tm_max_displacement_ml: float = 0.025
    age_years: int = 30
    sex: Literal["male", "female", "unspecified"] = "unspecified"


class EtFunctionRequest(BaseModel):
    model_config = _STRICT
    severity: Literal["normal", "mild", "moderate", "severe"] = "normal"
    passive_opening_mmHg_me: float = 25.7
    passive_opening_mmHg_np: float = 44.1
    closing_mmHg: float = 7.35
    active_resistance_mmHg_ml_min: float = 2.0
    active_open_duration_s: float = 0.25
    swallow_freq_per_hr_cruise: float = 5.2
    swallow_freq_per_hr_descent: float = 60.0
    fge_controls: float = 0.32


class PatientStateRequest(BaseModel):
    model_config = _STRICT
    anatomy: PatientAnatomyRequest = Field(default_factory=PatientAnatomyRequest)
    et: EtFunctionRequest = Field(default_factory=EtFunctionRequest)
    uri: Literal[
        "none", "day_1_3", "day_4_7", "day_8_14", "day_15_21", "day_22_28"
    ] = "none"
    pet: Literal["normal", "s1", "s2", "s3", "s4"] = "normal"
    rhinitis: Literal["none", "allergic", "chronic_rhinosinusitis"] = "none"
    previous_meb: bool = False
    medication: Literal[
        "none",
        "pseudoephedrine_oral",
        "oxymetazoline_topical",
        "intranasal_steroid",
        "antihistamine_spray",
    ] = "none"
    enable_valsalva: bool = True
    valsalva_interval_s: float = 60.0
    habitual_sniffer: bool = False


class ChamberSegmentRequest(BaseModel):
    model_config = _STRICT
    duration_s: float
    end_altitude_ft: float
    label: str = ""


class ChamberProfileRequest(BaseModel):
    """
    Either supply a ``preset`` key (one of ``scenarios.PRESETS``) or a full
    custom profile (``name`` + ``start_altitude_ft`` + ``segments``). If
    ``preset`` is set, the other fields are ignored.
    """
    model_config = _STRICT
    preset: str | None = None
    name: str | None = None
    start_altitude_ft: float | None = None
    segments: list[ChamberSegmentRequest] | None = None


class SimulateOptions(BaseModel):
    model_config = _STRICT
    dt_s: float = 0.1
    rng_seed: int | None = None
    gas_exchange_full: bool = False
    with_ci: bool = False
    ci_n_samples: int = Field(default=200, ge=10, le=2000)


class SimulateRequest(BaseModel):
    model_config = _STRICT
    patient: PatientStateRequest = Field(default_factory=PatientStateRequest)
    profile: ChamberProfileRequest
    options: SimulateOptions = Field(default_factory=SimulateOptions)


# =========================================================== response ==
class TraceResponse(BaseModel):
    t_s: list[float]
    altitude_ft: list[float]
    p_ambient_mmHg: list[float]
    p_me_mmHg: list[float]
    delta_p_mmHg: list[float]
    tm_displacement_ml: list[float]
    et_open: list[bool]
    swallow_events_s: list[float]
    valsalva_events_s: list[float]


class RiskResponse(BaseModel):
    p_barotitis: float
    p_baromyringitis: float
    p_rupture: float
    max_abs_delta_p_mmHg: float
    auc_mmHg_s_barotitis: float
    auc_mmHg_s_baromyringitis: float
    dominant_risk_factor: str
    recommended_max_descent_ft_min: float
    risk_category: Literal["low", "moderate", "high", "very_high"]
    ci95_barotitis: tuple[float, float] | None = None
    ci95_baromyringitis: tuple[float, float] | None = None
    ci95_rupture: tuple[float, float] | None = None


class SimulateResponse(BaseModel):
    trace: TraceResponse
    risk: RiskResponse
    notes: list[str]
    profile_name: str
    total_duration_s: float


class ProfilePresetInfo(BaseModel):
    key: str
    name: str
    start_altitude_ft: float
    total_duration_s: float
    segments: list[ChamberSegmentRequest]


# ================================================= dataclass adapters ==
def to_chamber_profile(
    req: ChamberProfileRequest,
    presets: dict[str, ChamberProfile],
) -> ChamberProfile:
    """Resolve a profile request to a v2 ``ChamberProfile``."""
    if req.preset is not None:
        if req.preset not in presets:
            raise ValueError(
                f"unknown profile preset '{req.preset}' — "
                f"available: {sorted(presets)}"
            )
        return presets[req.preset]

    if req.name is None or req.start_altitude_ft is None or not req.segments:
        raise ValueError(
            "custom profile requires name, start_altitude_ft, and segments "
            "(or supply preset instead)"
        )
    return ChamberProfile(
        name=req.name,
        start_altitude_ft=req.start_altitude_ft,
        segments=tuple(
            ChamberSegment(
                duration_s=s.duration_s,
                end_altitude_ft=s.end_altitude_ft,
                label=s.label,
            )
            for s in req.segments
        ),
    )


def to_patient_state(req: PatientStateRequest) -> PatientState:
    return PatientState(
        anatomy=PatientAnatomy(
            tympanum_volume_ml=req.anatomy.tympanum_volume_ml,
            mastoid_volume_ml=req.anatomy.mastoid_volume_ml,
            tm_area_cm2=req.anatomy.tm_area_cm2,
            tm_stiffness_mmHg_per_ml=req.anatomy.tm_stiffness_mmHg_per_ml,
            tm_max_displacement_ml=req.anatomy.tm_max_displacement_ml,
            age_years=req.anatomy.age_years,
            sex=req.anatomy.sex,
        ),
        et=EtFunction(
            severity=req.et.severity,
            passive_opening_mmHg_me=req.et.passive_opening_mmHg_me,
            passive_opening_mmHg_np=req.et.passive_opening_mmHg_np,
            closing_mmHg=req.et.closing_mmHg,
            active_resistance_mmHg_ml_min=req.et.active_resistance_mmHg_ml_min,
            active_open_duration_s=req.et.active_open_duration_s,
            swallow_freq_per_hr_cruise=req.et.swallow_freq_per_hr_cruise,
            swallow_freq_per_hr_descent=req.et.swallow_freq_per_hr_descent,
            fge_controls=req.et.fge_controls,
        ),
        uri=req.uri,
        pet=req.pet,
        rhinitis=req.rhinitis,
        previous_meb=req.previous_meb,
        medication=req.medication,
        enable_valsalva=req.enable_valsalva,
        valsalva_interval_s=req.valsalva_interval_s,
        habitual_sniffer=req.habitual_sniffer,
    )


def trace_to_response(trace: SimulationTrace) -> TraceResponse:
    return TraceResponse(
        t_s=trace.t_s.tolist(),
        altitude_ft=trace.altitude_ft.tolist(),
        p_ambient_mmHg=trace.p_ambient_mmHg.tolist(),
        p_me_mmHg=trace.p_me_mmHg.tolist(),
        delta_p_mmHg=trace.delta_p_mmHg.tolist(),
        tm_displacement_ml=trace.tm_displacement_ml.tolist(),
        et_open=trace.et_open.tolist(),
        swallow_events_s=trace.swallow_events_s.tolist(),
        valsalva_events_s=trace.valsalva_events_s.tolist(),
    )


def risk_to_response(risk: RiskResult) -> RiskResponse:
    return RiskResponse(
        p_barotitis=risk.p_barotitis,
        p_baromyringitis=risk.p_baromyringitis,
        p_rupture=risk.p_rupture,
        max_abs_delta_p_mmHg=risk.max_abs_delta_p_mmHg,
        auc_mmHg_s_barotitis=risk.auc_mmHg_s_barotitis,
        auc_mmHg_s_baromyringitis=risk.auc_mmHg_s_baromyringitis,
        dominant_risk_factor=risk.dominant_risk_factor,
        recommended_max_descent_ft_min=risk.recommended_max_descent_ft_min,
        risk_category=risk.risk_category(),
        ci95_barotitis=risk.ci95_barotitis,
        ci95_baromyringitis=risk.ci95_baromyringitis,
        ci95_rupture=risk.ci95_rupture,
    )


def result_to_response(result: SimulationResult) -> SimulateResponse:
    return SimulateResponse(
        trace=trace_to_response(result.trace),
        risk=risk_to_response(result.risk),
        notes=list(result.notes),
        profile_name=result.profile.name,
        total_duration_s=result.profile.total_duration_s(),
    )
