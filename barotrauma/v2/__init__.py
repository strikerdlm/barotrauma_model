"""
barotrauma.v2
=============

Current middle-ear barotrauma risk model, anchored to the Colombian Aerospace
Force (FAC) 10-year hypobaric chamber training cohort.

Public API
----------
::

    from barotrauma.v2 import simulate, PatientState, EtFunction, PatientAnatomy
    from barotrauma.v2.scenarios import USAFSAM_TYPE_I, FAC_BOGOTA_DEFAULT

    patient = PatientState(uri="day_4_7", rhinitis="allergic")
    result = simulate(patient, FAC_BOGOTA_DEFAULT)

    print(result.risk.p_barotitis, result.risk.risk_category())
    print(result.risk.dominant_risk_factor)

Evidence base
-------------
Physics core: Kanick & Doyle 2005 (PMID 15608090) + Doyle 2017 species-
resolved gas exchange (PMID 28917121) + Alper 2020 parameter distributions
(PMID 32176133). Pathophysiology modifiers: URI state-machine from Buchman
1994, McBride 1989, Doyle 1999, Chen 2022; Patulous ET 4-state from Ikeda
2020/2024, Shindo 2025. See ``docs/research_notes/`` for the structured
literature briefs that underpin every constant.

See also
--------
- ``barotrauma.legacy`` — the v1 stack (frozen, reproducibility-only).
- ``docs/model_card.md`` — inputs, outputs, assumptions, known limitations.
- ``CHANGELOG.md`` — version history.
"""

from __future__ import annotations

from . import (
    anatomy,
    atmosphere,
    calibration,
    constants,
    engine,
    et_dynamics,
    et_muscle,
    middle_ear,
    pathophysiology,
    risk,
    scenarios,
    types,
)
from .engine import simulate
from .et_muscle import (
    MuscleMechanics,
    default_dysfunctional_mechanics,
    default_healthy_mechanics,
)
from .ml_hybrid import (
    HybridEvaluation,
    HybridPrediction,
    PhysicsMLPredictor,
    extract_features,
)
from .pathophysiology import Modifiers, modifiers_for_patient
from .risk import score_trace, score_with_uncertainty
from .scenarios import (
    COMMERCIAL_CABIN_DESCENT,
    FAC_BOGOTA_DEFAULT,
    GROTH_1986_VALIDATION,
    ISRAELI_AF_POST_2022,
    PRESETS,
    RAPID_DESCENT_10K_FT_MIN,
    SLOW_DESCENT_1K_FT_MIN,
    USAFSAM_TYPE_I,
    USAFSAM_TYPE_II_RD,
    get_profile,
)
from .types import (
    ChamberProfile,
    ChamberSegment,
    ChronicRhinitis,
    EtFunction,
    EtSeverity,
    MedicationEffect,
    PatientAnatomy,
    PatientState,
    PetState,
    RiskResult,
    SimulationResult,
    SimulationTrace,
    UriState,
)

__all__ = [
    # submodules
    "anatomy", "atmosphere", "calibration", "constants", "engine",
    "et_dynamics", "et_muscle", "middle_ear", "pathophysiology",
    "risk", "scenarios", "types",
    # primary functions
    "simulate", "score_trace", "score_with_uncertainty",
    "modifiers_for_patient",
    # muscle mechanics (Ghadiali FEM extension, v2.2)
    "MuscleMechanics", "default_healthy_mechanics",
    "default_dysfunctional_mechanics",
    # hybrid physics-ML head (v2.2)
    "PhysicsMLPredictor", "HybridPrediction", "HybridEvaluation",
    "extract_features",
    # scenarios
    "PRESETS", "get_profile",
    "USAFSAM_TYPE_I", "USAFSAM_TYPE_II_RD",
    "ISRAELI_AF_POST_2022", "FAC_BOGOTA_DEFAULT",
    "COMMERCIAL_CABIN_DESCENT", "RAPID_DESCENT_10K_FT_MIN",
    "SLOW_DESCENT_1K_FT_MIN", "GROTH_1986_VALIDATION",
    # types
    "ChamberProfile", "ChamberSegment",
    "EtFunction", "EtSeverity", "PatientAnatomy",
    "PatientState", "PetState", "UriState",
    "ChronicRhinitis", "MedicationEffect",
    "RiskResult", "SimulationResult", "SimulationTrace",
    "Modifiers",
]
