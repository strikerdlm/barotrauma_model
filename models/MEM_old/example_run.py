# example_run.py
import numpy as np
import matplotlib.pyplot as plt
from model import AdvancedPhysiologicalMEModel

def altitude_func(time_s):
    # Flight: ascend 0->12000 ft in 10 min, cruise 10 min
    if time_s <= 600:
        return 12000*(time_s/600)
    else:
        return 12000

model = AdvancedPhysiologicalMEModel(et_dysfunction=0.4, perform_valsava=True)
t = np.linspace(0,1200,1201)
results = model.simulate_flight(t, altitude_func)

plt.plot(results['time'], results['delta_P']*13.6, label='ΔP (mmH2O)')
plt.title('ME vs Ambient Pressure with Complex ET Model')
plt.xlabel('Time (s)')
plt.ylabel('ΔP (mmH2O)')
plt.grid(True)
plt.legend()
plt.show()

unique, counts = np.unique(results['risk'], return_counts=True)
for u,c in zip(unique, counts):
    print(f"Risk {u}: {100*c/len(results['risk']):.2f}%")
