# et.py
import numpy as np
from physiology import PhysiologyConstants as PC

class EustachianTube:
    def __init__(self, et_dysfunction=0.0):
        self.et_dysfunction = et_dysfunction
        self.is_et_open = False
        self.current_open_time = 0.0

        # New dynamic states:
        self.edema = 0.0      # 0=no edema, can grow
        self.dryness = PC.dryness_base # dryness factor 0-1
        self.muscle_tone = PC.muscle_tone_base
        self.failed_attempts = 0

    def effective_RA(self):
        # RA scales with dysfunction and edema
        return PC.RA_base*(1.0 + PC.dysfunction_ET_factor*self.et_dysfunction + self.edema)

    def passive_threshold(self):
        # Threshold increases with edema and dryness
        # dryness also stiffens ET, requiring higher negative P
        # dryness reduces radius → effectively increasing threshold
        return PC.ET_passive_threshold_base*(1.0 + self.edema + 0.5*self.dryness + self.et_dysfunction)

    def np_threshold(self):
        # NP threshold also increases with edema/dryness
        return PC.NP_open_threshold_base*(1.0 + self.et_dysfunction + 0.5*self.edema + 0.5*self.dryness)

    def base_radius(self):
        # Base radius reduced by dysfunction and dryness
        # dryness factor reduces radius up to dryness_effect_on_radius fraction
        # edema further reduces radius linearly
        base_r = 0.05*(1.0 - 0.5*self.et_dysfunction)
        # dryness reduces radius by up to dryness_effect_on_radius * base_r
        r_dry = base_r*(1.0 - self.dryness*PC.dryness_effect_on_radius)
        # edema reduces radius by factor (1/(1+edema)) or linearly:
        # Let's do linear: radius = r_dry*(1 - edema*0.5)
        # strong edema can drastically reduce radius
        r_final = r_dry*(1.0 - min(self.edema*0.5,0.9))
        # muscle tone affects effective opening radius during swallow:
        # If muscle tone low, even with swallow radius doesn't increase well
        return r_final

    def muscle_effective_force(self):
        # muscle tone directly influences how well a swallow can open ET
        return self.muscle_tone*(1.0 - 0.3*self.et_dysfunction)

    def update_states(self, dt: float, delta_P_h2o: float, altitude: float, low_dp: bool):
        # Update edema:
        # If |ΔP|>200 mmH2O, edema accumulates
        if abs(delta_P_h2o) > PC.edema_threshold_mmH2O:
            factor = (abs(delta_P_h2o)-PC.edema_threshold_mmH2O)/100.0
            self.edema += PC.edema_rate*factor*dt
        else:
            # recover if dp low
            if low_dp:
                self.edema = max(self.edema - PC.edema_recovery_rate*dt, 0.0)

        # Update dryness with altitude and time
        # dryness ~ min( dryness + dryness_rate*(altitude/1000)*dt, dryness_max)
        self.dryness = min(self.dryness + PC.dryness_rate_altitude*(altitude/1000.0)*dt, PC.dryness_max)

        # Muscle tone recovers slowly if dp normal, else stable or reduce if fail attempts
        # Handled in update_ET_state after checking attempts

    def record_failed_attempt(self):
        self.failed_attempts += 1
        self.muscle_tone = max(self.muscle_tone - PC.muscle_fatigue_rate*self.failed_attempts,0.5)
        # muscle tone doesn't drop below 0.5 to avoid total collapse

    def successful_opening(self):
        # reset failed attempts partially
        self.failed_attempts = max(self.failed_attempts - 1,0)
        # if conditions are stable, muscle tone can recover slowly outside this function (in model)
        # no immediate effect here

    def update_ET_state(self, t: float, dt: float, delta_P_h2o: float, swallow_prob: float, valsalva_active: bool):
        previously_open = self.is_et_open

        if self.is_et_open:
            self.current_open_time += dt
            if self.current_open_time >= PC.ET_open_duration:
                self.is_et_open = False
        else:
            # closed:
            actual_swallow_prob = max(swallow_prob + np.random.normal(0, swallow_prob*0.2),0)
            # Check conditions in order of complexity:
            if np.random.rand() < actual_swallow_prob:
                # Attempt muscle-driven opening
                # If muscle force and radius is too low, attempt might fail:
                open_chance = self.muscle_effective_force()*self.base_radius()
                # A simplistic approach: if open_chance > 0.02 open ET
                # else fail attempt
                if open_chance > 0.02:
                    self.is_et_open = True
                    self.current_open_time = 0.0
                    self.successful_opening()
                else:
                    self.record_failed_attempt()
            elif delta_P_h2o < -self.passive_threshold():
                # passive opening
                if self.base_radius() > 0.01:
                    self.is_et_open = True
                    self.current_open_time = 0.0
                    self.successful_opening()
                else:
                    self.record_failed_attempt()
            elif valsalva_active and delta_P_h2o > self.np_threshold():
                # NP-driven opening
                # If muscle tone low or dryness high, might fail:
                open_chance = self.muscle_effective_force()*self.base_radius()
                if open_chance > 0.015:
                    self.is_et_open = True
                    self.current_open_time = 0.0
                    self.successful_opening()
                else:
                    self.record_failed_attempt()
            else:
                # no attempt
                pass

        # If ET opened now and wasn't before, good
        # If remained closed, conditions remain

