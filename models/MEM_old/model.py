# model.py
import numpy as np
from scipy.integrate import odeint
from typing import Callable, Dict
from physiology import PhysiologyConstants as PC, paCO2_with_altitude_and_discomfort
from alveolar import alveolar_gas_equation, calculate_patm
from et import EustachianTube

class AdvancedPhysiologicalMEModel:
    def __init__(self, et_dysfunction=0.0, perform_valsava=False, seed=42):
        np.random.seed(seed)
        self.et = EustachianTube(et_dysfunction)
        self.perform_valsava = perform_valsava
        self.last_valsava_time = -9999.0
        self.is_valsava_active = False

        self.reflex_active = False
        self.reflex_start_time = None

        self.P_O2_init = 40.0
        self.P_CO2_init = 46.0
        self.P_H2O_init = 47.0
        self.P_N2_init = 760.0 - (self.P_O2_init + self.P_CO2_init + self.P_H2O_init)
        self.y0 = [760.0, 0.0, self.P_O2_init, self.P_CO2_init, self.P_H2O_init, self.P_N2_init]

    def tm_compliance(self, delta_P_h2o: float):
        stiffening_factor = 1.0 + (abs(delta_P_h2o)/500.0)**2
        return PC.CTM_base / stiffening_factor

    def adjust_swallow_rate(self, delta_P_h2o: float):
        extra = max((abs(delta_P_h2o)-200)/100, 0)
        extra_reflex = 2.0 if self.reflex_active else 0.0
        return PC.baseline_swallow_rate + extra + extra_reflex

    def initiate_valsava(self, t: float):
        if self.perform_valsava:
            if (t - self.last_valsava_time) > PC.valsalva_interval:
                self.is_valsava_active = True
                self.last_valsava_time = t

    def check_valsava_end(self, t: float):
        if self.perform_valsava and self.is_valsava_active:
            if (t - self.last_valsava_time) > PC.valsalva_duration:
                self.is_valsava_active = False

    def reflex_check(self, t: float, delta_P_mmH2O: float):
        if abs(delta_P_mmH2O) > PC.reflex_threshold_mmH2O:
            if self.reflex_start_time is None:
                self.reflex_start_time = t
            else:
                if (t - self.reflex_start_time) > PC.reflex_sustain_time:
                    self.reflex_active = True
                    if self.perform_valsava and not self.is_valsava_active:
                        self.is_valsava_active = True
                        self.last_valsava_time = t
        else:
            self.reflex_start_time = None
            self.reflex_active = False

    def model_ode(self, y, t, altitude_func: Callable):
        P_ME, V_change, P_O2, P_CO2, P_H2O, P_N2 = y
        P_ME_gases = np.array([P_O2, P_CO2, P_H2O, P_N2])

        altitude = altitude_func(t)
        Patm = calculate_patm(altitude)

        delta_P = P_ME - Patm
        delta_P_h2o = delta_P*13.6
        delta_P_mmH2O = delta_P_h2o
        discomfort_factor = min(abs(delta_P_mmH2O)/PC.reflex_threshold_mmH2O, 1.0)

        PaCO2_current = paCO2_with_altitude_and_discomfort(altitude, discomfort_factor)
        PA_gases = alveolar_gas_equation(Patm, PaCO2_current)

        V_ME = PC.Vtym + PC.Vmas

        self.check_valsava_end(t)
        self.reflex_check(t, delta_P_mmH2O)
        self.initiate_valsava(t)

        swallow_rate = self.adjust_swallow_rate(delta_P_h2o)
        lambda_swallow = (swallow_rate / 3600.0)*(1.0 - 0.5*self.et.et_dysfunction)
        dt = 0.001
        swallow_prob = lambda_swallow*dt

        # Update ET states (edema, dryness, muscle tone)
        low_dp = (abs(delta_P_h2o) < 50) # if deltaP small, recovery conditions
        self.et.update_states(dt, delta_P_h2o, altitude, low_dp)

        self.et.update_ET_state(t, dt, delta_P_h2o, swallow_prob, self.is_valsava_active)

        # If dp stable, muscle tone may recover slightly:
        if low_dp:
            self.et.muscle_tone = min(self.et.muscle_tone + PC.muscle_recovery_rate*dt, 1.0)

        # TM displacement
        CTM = self.tm_compliance(delta_P_h2o)
        ATM_cm2 = PC.ATM_mm2/100.0
        dV_TM = (delta_P_h2o * CTM * ATM_cm2)/1000.0
        dV_TM = np.clip(dV_TM, -PC.max_TM_displacement, PC.max_TM_displacement)
        V_ME_eff = V_ME + dV_TM

        V_prev = V_ME + V_change
        dP_volume = -P_ME*(V_ME_eff - V_prev)/V_prev if V_prev != 0 else 0.0

        # Blood gas exchange
        K = np.array([PC.k_O2, PC.k_CO2, PC.k_H2O, PC.k_N2])
        K_eff = K*(1.0 - 0.5*self.et.et_dysfunction)
        dP_gas_blood = -K_eff*(P_ME_gases - PA_gases)*0.001
        P_ME_gases_intermediate = P_ME_gases + dP_gas_blood

        # ET exchange if open
        if self.et.is_et_open and V_ME_eff > 0:
            if self.is_valsava_active:
                P_NP = Patm + (PC.valsalva_force_mmH2O/13.6)
            else:
                P_NP = Patm
            fraction = 0.01*(1.0 - 0.5*self.et.et_dysfunction)
            P_amb_gases = np.array([0.21*P_NP, 0.0004*P_NP, 0.0, 0.789*P_NP])
            dP_gas_ET = fraction*(P_amb_gases - P_ME_gases_intermediate)
        else:
            dP_gas_ET = np.zeros(4)

        P_ME_gases_new = P_ME_gases_intermediate + dP_gas_ET
        P_ME_intermediate = P_ME + dP_volume
        P_ME_final = P_ME_intermediate + (np.sum(P_ME_gases_new) - np.sum(P_ME_gases))

        dP_ME = P_ME_final - P_ME
        dV = (V_ME_eff - V_ME)
        dP_O2, dP_CO2, dP_H2O, dP_N2 = dP_gas_ET

        return [dP_ME, dV - V_change, dP_O2, dP_CO2, dP_H2O, dP_N2]

    def simulate_flight(self, t: np.ndarray, altitude_func: Callable) -> Dict[str, np.ndarray]:
        solution = odeint(self.model_ode, self.y0, t, args=(altitude_func,))
        
        P_ME = solution[:, 0]
        V_change = solution[:, 1]
        P_O2 = solution[:, 2]
        P_CO2 = solution[:, 3]
        P_H2O = solution[:, 4]
        P_N2 = solution[:, 5]

        P_amb = np.array([calculate_patm(altitude_func(tt)) for tt in t])
        delta_P = P_ME - P_amb
        delta_P_mmH2O = delta_P*13.6

        risk = np.where(np.abs(delta_P_mmH2O) > PC.risk_threshold_baromyringitis, 'Severe',
                 np.where(np.abs(delta_P_mmH2O) > PC.risk_threshold_barotitis, 'Moderate', 'Low'))

        return {
            'time': t,
            'P_ME': P_ME,
            'P_amb': P_amb,
            'delta_P': delta_P,
            'P_O2': P_O2,
            'P_CO2': P_CO2,
            'P_H2O': P_H2O,
            'P_N2': P_N2,
            'risk': risk
        }
