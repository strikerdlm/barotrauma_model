"""
api.main
========

FastAPI application: wraps ``barotrauma.v2.simulate`` for the React/TS
frontend. Single simulation endpoint plus preset discovery and a
descent-rate sensitivity sweep.

Run:
    uvicorn api.main:app --reload --port 8000

The Vite dev server (``frontend/``) forwards ``/api/*`` to this process.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import numpy as np

from barotrauma.v2 import simulate
from barotrauma.v2.pathophysiology import modifiers_for_patient
from barotrauma.v2.risk import score_with_uncertainty
from barotrauma.v2.scenarios import PRESETS

from .schemas import (
    ChamberProfileRequest,
    ChamberSegmentRequest,
    ProfilePresetInfo,
    SimulateRequest,
    SimulateResponse,
    result_to_response,
    risk_to_response,
    to_chamber_profile,
    to_patient_state,
)

app = FastAPI(
    title="barotrauma_model API",
    version="2.2.1",
    description=(
        "Sidecar exposing ``barotrauma.v2`` to the React/TypeScript "
        "dashboard. Single source of truth — the Python physics engine "
        "is authoritative. See ``docs/model_card.md`` for scope."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ================================================================ routes
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.2.1"}


@app.get("/api/scenarios", response_model=list[ProfilePresetInfo])
def list_scenarios() -> list[ProfilePresetInfo]:
    """Enumerate preset chamber profiles for the UI scenario picker."""
    return [
        ProfilePresetInfo(
            key=key,
            name=profile.name,
            start_altitude_ft=profile.start_altitude_ft,
            total_duration_s=profile.total_duration_s(),
            segments=[
                ChamberSegmentRequest(
                    duration_s=seg.duration_s,
                    end_altitude_ft=seg.end_altitude_ft,
                    label=seg.label,
                )
                for seg in profile.segments
            ],
        )
        for key, profile in PRESETS.items()
    ]


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate_endpoint(req: SimulateRequest) -> SimulateResponse:
    try:
        profile = to_chamber_profile(req.profile, PRESETS)
        patient = to_patient_state(req.patient)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    try:
        result = simulate(
            patient,
            profile,
            dt_s=req.options.dt_s,
            rng_seed=req.options.rng_seed,
            gas_exchange_full=req.options.gas_exchange_full,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    response = result_to_response(result)

    if req.options.with_ci:
        rng = (
            np.random.default_rng(req.options.rng_seed)
            if req.options.rng_seed is not None
            else None
        )
        risk_with_ci = score_with_uncertainty(
            result.trace,
            patient,
            modifiers_for_patient(patient),
            n_mc=req.options.ci_n_samples,
            rng=rng,
        )
        response.risk = risk_to_response(risk_with_ci)

    return response


@app.get("/api/scenarios/{key}", response_model=ProfilePresetInfo)
def get_scenario(key: str) -> ProfilePresetInfo:
    if key not in PRESETS:
        raise HTTPException(
            status_code=404,
            detail=f"unknown profile '{key}' — available: {sorted(PRESETS)}",
        )
    profile = PRESETS[key]
    return ProfilePresetInfo(
        key=key,
        name=profile.name,
        start_altitude_ft=profile.start_altitude_ft,
        total_duration_s=profile.total_duration_s(),
        segments=[
            ChamberSegmentRequest(
                duration_s=seg.duration_s,
                end_altitude_ft=seg.end_altitude_ft,
                label=seg.label,
            )
            for seg in profile.segments
        ],
    )
