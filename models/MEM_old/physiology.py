# physiology.py
import numpy as np

class PhysiologyConstants:
    # Atmospheric
    P0 = 760.0
    PH2O = 47.0
    FiO2 = 0.21
    Respiratory_Quotient = 0.8

    # Ventilation and PaCO2
    PaCO2_sea = 40.0
    PaCO2_min = 30.0
    altitude_threshold_ft = 5000
    PaCO2_drop_per_1000ft = 1.0
    max_discomfort_reduction = 5.0

    # ET and swallowing
    baseline_swallow_rate = 5.0   # swallows/hour base
    ET_passive_threshold_base = 200  # mmH2O
    NP_open_threshold_base = 600     # mmH2O
    ET_closing_pressure = 100        # mmH2O
    ET_open_duration = 0.25          # s
    RA_base = 2.0
    dysfunction_ET_factor = 5.0

    # ET advanced parameters:
    # Mucosal edema: increases with sustained ΔP, reduces radius
    edema_rate = 0.001  # edema per second per 100 mmH2O above threshold
    edema_recovery_rate = 0.0005 # edema recovery per second if ΔP < threshold
    edema_threshold_mmH2O = 200

    # Dryness factor: increases with altitude and time
    dryness_rate_altitude = 0.0001 # dryness increase per second per 1000 ft
    dryness_base = 0.0
    dryness_effect_on_radius = 0.5 # max reduction in radius at dryness=1.0
    dryness_max = 1.0

    # Muscle tone: reduces if multiple failed attempts occur
    muscle_tone_base = 1.0
    muscle_fatigue_rate = 0.001   # reduce tone per failed opening attempt
    muscle_recovery_rate = 0.0002 # tone recovers slowly if ΔP normal

    # TM and volumes
    Vtym = 1.0
    Vmas = 7.75
    ATM_mm2 = 64.0
    CTM_base = 179
    max_TM_displacement = 0.3

    # Reflex thresholds
    reflex_threshold_mmH2O = 300
    reflex_sustain_time = 30.0
    valsalva_interval = 300.0
    valsalva_duration = 5.0
    valsalva_force_mmH2O = 500

    # Risk thresholds
    risk_threshold_barotitis = 100
    risk_threshold_baromyringitis = 200
