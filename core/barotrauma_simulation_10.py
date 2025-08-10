import numpy as np
from typing import Callable, Dict, List, Union
from dataclasses import dataclass
from scipy.integrate import odeint

@dataclass
class PhysiologicalParameters:
    """
    Expanded physiological parameters based on Kanick & Doyle (2005) and previous models.
    Enhanced for more realism:
    - Altitude-dependent alveolar pressures
    - Adjustable ET dysfunction effects
    """
    # Middle Ear & Tympanic Membrane
    Vtym: float = 1.0                 # Tympanum volume (ml)
    Vmas: float = 7.75                # Mastoid volume (ml)
    ATM: float = 64.0                 # TM surface area (mm²) ~0.64 cm² if needed.
    CTM_base: float = 179             # Baseline TM stiffness (mmH2O/ml)
    max_TM_displacement: float = 0.3  # Maximum TM displacement volume (ml)
    
    # Eustachian Tube & Swallowing
    baseline_swallow_rate: float = 5.0   # Swallows/hour under normal conditions
    ET_length: float = 3.5               # ET length (cm)
    ET_base_width: float = 0.1           # ET width (cm)
    mu_air: float = 1.81e-4              # Viscosity of air (Pa·s)
    TVP_force: float = 1.0               # Normalized muscle force
    et_dysfunction: float = 0.0          # 0 = normal, 1 = severe dysfunction
    ET_open_duration: float = 0.25       # ET patency per swallow (s)
    ET_passive_threshold: float = 200    # mmH2O threshold for passive ET opening
    NP_open_threshold: float = 600       # mmH2O threshold for NP-driven opening
    ET_closing_pressure: float = 100     # mmH2O
    RA_base: float = 2.0                 # ET active resistance (arbitrary)
    
    # Gas Exchange & Alveolar References (Base values at sea level)
    # Will adjust with altitude
    PA_O2_sea: float = 100.0
    PA_CO2: float = 40.0
    PA_H2O: float = 47.0
    PA_N2_sea: float = 760.0 - (100+40+47) # ~573 mmHg

    # Gas exchange rates (1/s)
    k_O2: float = 0.0007
    k_CO2: float = 0.03
    k_H2O: float = 0.3
    k_N2: float = 0.0001
    
    # Risk parameters
    risk_threshold_barotitis: float = 100   # mmH2O
    risk_threshold_baromyringitis: float = 200  # mmH2O

    # Altitude effect on alveolar O2:
    # O2 partial pressure decreases roughly 5 mmHg per 1000 ft
    O2_drop_per_1000ft: float = 5.0

    # Valsalva parameters
    perform_valsava: bool = False
    valsalva_interval: float = 300.0  # every 5 minutes
    valsalva_duration: float = 5.0    # hold for 5s
    valsalva_force_mmH2O: float = 500 # how much NP > ambient (mmH2O)

class AdvancedPhysiologicalMEModel:
    """
    More realistic physiological model of Middle Ear pressure regulation.
    
    Improvements over previous versions:
    - Dynamic alveolar pressures w.r.t altitude
    - ET swallow rate modulated by pressure discomfort
    - ET dysfunction influences RA and ET geometry more explicitly
    - Optional periodic Valsalva maneuvers
    - Risk assessment with simpler thresholds
    """
    def __init__(self, params: Dict = None, seed: int = 42):
        if params is None:
            params = {}
        self.params = PhysiologicalParameters()
        
        # Override any parameters from dict
        for k,v in params.items():
            setattr(self.params, k, v)
        
        np.random.seed(seed)
        
        # Initial partial pressures in ME
        self.P_O2_init = 40.0
        self.P_CO2_init = 46.0
        self.P_H2O_init = 47.0
        self.P_N2_init = 760.0 - (self.P_O2_init + self.P_CO2_init + self.P_H2O_init)
        
        # State vector: [P_ME, V_change, P_O2, P_CO2, P_H2O, P_N2]
        self.y0 = [760.0, 0.0, self.P_O2_init, self.P_CO2_init, self.P_H2O_init, self.P_N2_init]
        
        # ET states
        self.is_et_open = False
        self.current_open_time = 0.0
        
        # Valsalva states
        self.is_valsava_active = False
        self.last_valsava_time = -9999.0

    def alveolar_pressures(self, altitude_ft: float) -> np.ndarray:
        """
        Approximate alveolar pressures with altitude.
        Decrease O2 linearly with altitude.
        CO2 and H2O stable, N2 adjusted as remainder.
        """
        decrease_O2 = (altitude_ft/1000)*self.params.O2_drop_per_1000ft
        PA_O2 = max(self.params.PA_O2_sea - decrease_O2, 40.0) # clamp O2 at 40 mmHg min
        PA_CO2 = self.params.PA_CO2
        PA_H2O = self.params.PA_H2O
        PA_N2 = 760.0 - (PA_O2 + PA_CO2 + PA_H2O)
        return np.array([PA_O2, PA_CO2, PA_H2O, PA_N2])

    @staticmethod
    def calculate_pressure_mmHg(altitude_ft: float) -> float:
        """ Barometric formula approximation. """
        P0 = 760.0
        return P0 * np.exp(-altitude_ft/145366.45)

    def tm_compliance(self, delta_P_h2o: float) -> float:
        """Non-linear TM compliance with saturation."""
        stiffening_factor = 1.0 + (abs(delta_P_h2o)/500.0)**2
        return self.params.CTM_base / stiffening_factor

    def mod_swallow_rate(self, delta_P_h2o: float) -> float:
        """
        Increase swallowing frequency if large pressure differentials persist:
        For every 100 mmH2O beyond 200, add extra 1 swallow/hour.
        """
        extra = max((abs(delta_P_h2o)-200)/100, 0)
        return self.params.baseline_swallow_rate + extra

    def et_open_probability(self, t: float, delta_P_h2o: float) -> bool:
        """Poisson swallow events, modulated by pressure discomfort."""
        swallow_rate = self.mod_swallow_rate(delta_P_h2o)
        lambda_swallow = (swallow_rate / 3600.0)*(1.0 - 0.5*self.params.et_dysfunction)
        dt = 0.001
        return (np.random.rand() < lambda_swallow*dt)

    def et_passive_opening(self, delta_P_h2o: float) -> bool:
        threshold = self.params.ET_passive_threshold*(1.0 + 2.0*self.params.et_dysfunction)
        return (delta_P_h2o < -threshold)

    def initiate_valsava(self, t: float):
        """
        If valsalva enabled and enough time since last valsalva, start one.
        """
        if self.params.perform_valsava:
            if (t - self.last_valsava_time) > self.params.valsalva_interval:
                self.is_valsava_active = True
                self.last_valsava_time = t

    def check_valsava_end(self, t: float):
        """
        End valsalva after valsalva_duration.
        """
        if self.params.perform_valsava and self.is_valsava_active:
            if (t - self.last_valsava_time) > self.params.valsalva_duration:
                self.is_valsava_active = False

    def et_np_driven_opening(self, delta_P_h2o: float) -> bool:
        if self.is_valsava_active:
            threshold = self.params.NP_open_threshold*(1.0 + self.params.et_dysfunction)
            return (delta_P_h2o > threshold)
        return False

    def effective_RA(self) -> float:
        """
        ET active resistance influenced by dysfunction:
        More dysfunction = higher RA = harder to equalize.
        """
        return self.params.RA_base*(1.0 + 5.0*self.params.et_dysfunction)

    def et_geometry(self) -> float:
        """ET radius reduced by dysfunction."""
        radius = (self.params.ET_base_width/2.0)*(1.0 - 0.5*self.params.et_dysfunction)
        return radius

    def gas_exchange_blood(self, P_ME_gases: np.ndarray, PA_gases: np.ndarray, dt: float) -> np.ndarray:
        K = np.array([self.params.k_O2, self.params.k_CO2, self.params.k_H2O, self.params.k_N2])
        K_eff = K*(1.0 - 0.5*self.params.et_dysfunction)
        dP = -K_eff*(P_ME_gases - PA_gases)*dt
        return dP

    def model_ode(self, y: List[float], t: float, altitude_func: Callable) -> List[float]:
        P_ME, V_change, P_O2, P_CO2, P_H2O, P_N2 = y
        P_ME_gases = np.array([P_O2, P_CO2, P_H2O, P_N2])

        # Altitude & Pressures
        altitude = altitude_func(t)
        P_amb = self.calculate_pressure_mmHg(altitude)
        PA_gases = self.alveolar_pressures(altitude)

        V_ME = self.params.Vtym + self.params.Vmas
        delta_P = P_ME - P_amb
        delta_P_h2o = delta_P*13.6

        # Valsalva management
        self.check_valsava_end(t)
        self.initiate_valsava(t)

        # ET State
        # If ET open, check closing time
        if self.is_et_open:
            self.current_open_time += 0.001
            if self.current_open_time >= self.params.ET_open_duration:
                self.is_et_open = False
        else:
            # Not open, check conditions
            if self.et_open_probability(t, delta_P_h2o):
                self.is_et_open = True
                self.current_open_time = 0.0
            elif self.et_passive_opening(delta_P_h2o):
                self.is_et_open = True
                self.current_open_time = 0.0
            elif self.et_np_driven_opening(delta_P_h2o):
                self.is_et_open = True
                self.current_open_time = 0.0

        # TM displacement
        CTM = self.tm_compliance(delta_P_h2o)
        # Convert ATM from mm² to cm² if needed: 1 cm² = 100 mm², so ATM (mm²)->(cm²)
        ATM_cm2 = self.params.ATM/100.0
        dV_TM = (delta_P_h2o * CTM * ATM_cm2)/1000.0
        dV_TM = np.clip(dV_TM, -self.params.max_TM_displacement, self.params.max_TM_displacement)
        V_ME_eff = V_ME + dV_TM

        # Volume effect
        V_prev = V_ME + V_change
        dP_volume = -P_ME*(V_ME_eff - V_prev)/V_prev if V_prev != 0 else 0

        # Blood gas exchange
        dP_gas_blood = self.gas_exchange_blood(P_ME_gases, PA_gases, 0.001)
        P_ME_gases_intermediate = P_ME_gases + dP_gas_blood

        # ET exchange if open
        if self.is_et_open and V_ME_eff > 0:
            if self.is_valsava_active:
                # Valsalva: NP > P_amb by valsalva_force_mmH2O
                P_NP = P_amb + (self.params.valsalva_force_mmH2O/13.6)
            else:
                P_NP = P_amb

            # Approximate ET flow fraction
            fraction = 0.01*(1.0 - 0.5*self.params.et_dysfunction)
            # Ambient fractions:
            # O2 ~21%, CO2~0.04%, rest N2, no H2O in dry ambient approx
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
        P_amb = np.array([self.calculate_pressure_mmHg(altitude_func(tt)) for tt in t])
        
        P_O2 = solution[:, 2]
        P_CO2 = solution[:, 3]
        P_H2O = solution[:, 4]
        P_N2 = solution[:, 5]

        delta_P = P_ME - P_amb
        # Risk levels
        risk = np.where(np.abs(delta_P*13.6) > self.params.risk_threshold_baromyringitis, 'Severe',
                 np.where(np.abs(delta_P*13.6) > self.params.risk_threshold_barotitis, 'Moderate', 'Low'))

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

# Example usage of the improved model
import numpy as np
import matplotlib.pyplot as plt

# Define a simple altitude function: ascend from 0 to 8000 ft in 15 min, cruise 15 min
def altitude_func(time_s):
    if time_s <= 900:
        return 8000*(time_s/900)   # linear ascent over 15 min
    else:
        return 8000                # cruise altitude

# Create model instance with some ET dysfunction and valsalva enabled
params = {
    'et_dysfunction': 0.3,
    'perform_valsava': True
}
model = AdvancedPhysiologicalMEModel(params=params)

# Simulate 30 min at 1 second steps
t = np.linspace(0, 1800, 1801)  # every 1s for 30 min
results = model.simulate_flight(t, altitude_func)

# Plot delta_P over time
plt.figure(figsize=(10,5))
plt.plot(results['time'], results['delta_P']*13.6, label='Delta P (mmH2O)')
plt.title('Middle Ear vs Ambient Pressure Differential')
plt.xlabel('Time (s)')
plt.ylabel('Delta P (mmH2O)')
plt.legend()
plt.grid(True)
plt.show()

# Print risk distribution
unique, counts = np.unique(results['risk'], return_counts=True)
for u,c in zip(unique, counts):
    print(f"Risk {u}: {(c/len(results['risk']))*100:.2f}%")
