# alveolar.py
import numpy as np
from physiology import PhysiologyConstants as PC

def calculate_patm(altitude_ft: float) -> float:
    return PC.P0 * np.exp(-altitude_ft/145366.45)

def paCO2_with_altitude_and_discomfort(altitude_ft: float, discomfort_factor: float) -> float:
    PaCO2 = PC.PaCO2_sea
    if altitude_ft > PC.altitude_threshold_ft:
        extra_alt = (altitude_ft - PC.altitude_threshold_ft)/1000.0
        drop = min(extra_alt*PC.PaCO2_drop_per_1000ft, PC.PaCO2_sea - PC.PaCO2_min)
        PaCO2 -= drop
    PaCO2 -= discomfort_factor*PC.max_discomfort_reduction
    PaCO2 = max(PaCO2, PC.PaCO2_min)
    return PaCO2

def alveolar_gas_equation(Patm: float, paCO2: float) -> np.ndarray:
    noise_factor = 1.0 + np.random.uniform(-0.05,0.05)
    FiO2 = PC.FiO2*noise_factor
    PAO2 = FiO2*(Patm - PC.PH2O) - (paCO2/PC.Respiratory_Quotient)
    PAO2 = max(PAO2, 15.0)
    PACO2 = paCO2
    PAH2O = PC.PH2O
    PAN2 = Patm - (PAO2 + PACO2 + PAH2O)
    return np.array([PAO2, PACO2, PAH2O, PAN2])
