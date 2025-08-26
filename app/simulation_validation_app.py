import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Import model components
try:
	from models.flight_profile import FlightProfile
	from models.barotrauma_simulation import BarotraumaSimulation
except Exception as e:
	st.stop()


# ------------------------------ Page Config ------------------------------ #
st.set_page_config(
	page_title="Model Simulation and Validation",
	layout="wide",
	initial_sidebar_state="expanded",
)

st.title("Model Simulation and Validation")
st.markdown(
	"""
	Configure the simulation, run the model, and review scientifically formatted results with
	quality measurements based on real validation data.
	"""
)


# ------------------------------- Utilities ------------------------------ #
@st.cache_data(show_spinner=False)
def load_paper_validation() -> Dict:
	"""Load paper validation dataset used for quality metrics."""
	data_path = Path(__file__).resolve().parents[1] / "tests" / "data" / "paper_validation.json"
	with data_path.open("r") as f:
		return json.load(f)


def compute_quality_metrics(sim_results: Dict[str, np.ndarray]) -> Dict[str, float]:
	"""Compute internal model metrics from simulation arrays (units in mmHg unless noted)."""
	dP = sim_results["dP"]
	metrics = {
		"max_abs_deltaP_mmHg": float(np.max(np.abs(dP))),
		"mean_abs_deltaP_mmHg": float(np.mean(np.abs(dP))),
		"fraction_time_ET_locked": float(np.mean(sim_results["ET_locked"])),
		"fraction_time_barotitis": float(np.mean(sim_results["barotitis"])),
		"fraction_time_baromyringitis": float(np.mean(sim_results["baromyringitis"])),
		"mean_risk_factor": float(np.mean(sim_results["risk_factor"])),
	}
	return metrics


def compute_rmse_against_paper(sim_time_min: np.ndarray, dP_mmHg: np.ndarray) -> Dict[str, float]:
	"""Compute RMSE and max error vs paper pressure chamber data (mmH2O)."""
	paper = load_paper_validation()
	paper_time_s = np.asarray(paper["pressure_chamber"]["time"], dtype=float)
	paper_pressure_mmH2O = np.asarray(paper["pressure_chamber"]["pressure"], dtype=float)

	# Convert simulation time to seconds and pressure to mmH2O
	sim_time_s = sim_time_min * 60.0
	dP_mmH2O = dP_mmHg * 13.6

	# Interpolate simulation ΔP to paper time grid
	# Guard against non-monotonic inputs
	order = np.argsort(sim_time_s)
	sim_time_s_sorted = sim_time_s[order]
	dP_sorted = dP_mmH2O[order]

	# Limit interpolation to the simulation time range
	min_t, max_t = float(sim_time_s_sorted[0]), float(sim_time_s_sorted[-1])
	mask = (paper_time_s >= min_t) & (paper_time_s <= max_t)
	if not np.any(mask):
		return {"rmse_mmH2O": float("nan"), "max_abs_error_mmH2O": float("nan")}

	paper_t_clipped = paper_time_s[mask]
	paper_p_clipped = paper_pressure_mmH2O[mask]

	sim_interp = np.interp(paper_t_clipped, sim_time_s_sorted, dP_sorted)
	errors = sim_interp - paper_p_clipped
	rmse = float(np.sqrt(np.mean(errors**2)))
	max_err = float(np.max(np.abs(errors)))
	return {"rmse_mmH2O": rmse, "max_abs_error_mmH2O": max_err}


# -------------------------------- Sidebar -------------------------------- #
with st.sidebar:
	st.header("Configuration")

	st.subheader("Flight Profile")
	cruise_altitude = st.slider("Cruise Altitude (ft)", 5000, 45000, 35000, step=1000)
	ascent_rate = st.slider("Ascent Rate (ft/min)", 500, 5000, 1500, step=100)
	descent_rate = st.slider("Descent Rate (ft/min)", 500, 5000, 3000, step=100)
	cruise_duration = st.slider("Cruise Duration (min)", 10, 300, 120, step=10)

	st.subheader("Physiology")
	et_dysfunction = st.slider("ET Dysfunction (0=normal, 1=severe)", 0.0, 1.0, 0.6, step=0.05)

	st.subheader("Simulation Controls")
	dt = st.number_input("Time step dt (minutes)", min_value=0.01, max_value=5.0, value=0.1, step=0.01)
	fix_seed = st.checkbox("Fix random seed for reproducibility", value=True)
	seed = st.number_input("Seed", min_value=0, max_value=2**32 - 1, value=42) if fix_seed else None

	st.divider()
	st.caption("Units: Pressure in mmHg unless specified; ΔP in both mmHg and mmH2O where shown.")


# ---------------------------- Run the simulation ------------------------- #
if fix_seed and seed is not None:
	np.random.seed(int(seed))

profile = FlightProfile(
	cruise_altitude=float(cruise_altitude),
	ascent_rate=float(ascent_rate),
	descent_rate=float(descent_rate),
	cruise_duration=float(cruise_duration),
	et_dysfunction=float(et_dysfunction),
)
simulator = BarotraumaSimulation(profile)
results = simulator.run_simulation(dt=float(dt))

# Derived quantities

time_min = results["time"]
P_cabin = results["P_cabin"]
P_ME = results["P_ME"]
dP = results["dP"]  # mmHg

dP_mmH2O = dP * 13.6


# ---------------------------- Metrics Summary ---------------------------- #
st.header("Summary Metrics")
internal = compute_quality_metrics(results)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
	st.metric("Max |ΔP|", f"{internal['max_abs_deltaP_mmHg']:.1f} mmHg")
with c2:
	st.metric("Mean |ΔP|", f"{internal['mean_abs_deltaP_mmHg']:.2f} mmHg")
with c3:
	st.metric("ET Locked (time)", f"{internal['fraction_time_ET_locked']*100:.1f}%")
with c4:
	st.metric("Barotitis (time)", f"{internal['fraction_time_barotitis']*100:.1f}%")
with c5:
	st.metric("Baromyringitis (time)", f"{internal['fraction_time_baromyringitis']*100:.1f}%")
with c6:
	st.metric("Mean Risk Factor", f"{internal['mean_risk_factor']:.2f}")


# --------------------------------- Plots --------------------------------- #
st.header("Time Series Plots")
plot_tab1, plot_tab2, plot_tab3 = st.tabs(["Pressures", "ΔP and Thresholds", "Altitude and Risk"])

with plot_tab1:
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=time_min, y=P_cabin, name="Cabin Pressure", mode="lines"))
	fig.add_trace(go.Scatter(x=time_min, y=P_ME, name="Middle Ear Pressure", mode="lines"))
	fig.update_layout(
		template="plotly_white",
		xaxis_title="Time (min)",
		yaxis_title="Pressure (mmHg)",
		height=420,
	)
	st.plotly_chart(fig, use_container_width=True)

with plot_tab2:
	fig2 = go.Figure()
	fig2.add_trace(go.Scatter(x=time_min, y=dP, name="ΔP (mmHg)", mode="lines"))
	# Thresholds (mmHg)
	fig2.add_hline(y=90.0, line_dash="dash", line_color="orange", annotation_text="ET Lock")
	fig2.add_hline(y=150.0, line_dash="dot", line_color="red", annotation_text="Rupture Risk")
	fig2.add_hline(y=-90.0, line_dash="dash", line_color="orange", annotation_text="ET Lock")
	fig2.add_hline(y=-150.0, line_dash="dot", line_color="red", annotation_text="Rupture Risk")
	fig2.update_layout(
		template="plotly_white",
		xaxis_title="Time (min)",
		yaxis_title="ΔP (mmHg)",
		height=420,
	)
	st.plotly_chart(fig2, use_container_width=True)

with plot_tab3:
	fig3 = go.Figure()
	fig3.add_trace(go.Scatter(x=time_min, y=results["altitude"], name="Altitude (ft)", mode="lines", yaxis="y1"))
	fig3.add_trace(go.Scatter(x=time_min, y=results["risk_factor"], name="Risk Factor", mode="lines", yaxis="y2"))
	fig3.update_layout(
		template="plotly_white",
		xaxis_title="Time (min)",
		yaxis=dict(title="Altitude (ft)", side="left", showgrid=False),
		yaxis2=dict(title="Risk Factor", overlaying="y", side="right", range=[0, 1]),
		height=420,
	)
	st.plotly_chart(fig3, use_container_width=True)


# ---------------------------- Model Quality ------------------------------ #
st.header("Model Quality Measurements")

# RMSE vs paper (pressure chamber)
q = compute_rmse_against_paper(time_min, dP)
qc1, qc2 = st.columns(2)
with qc1:
	st.metric("RMSE vs Paper (mmH2O)", f"{q['rmse_mmH2O']:.1f}" if np.isfinite(q['rmse_mmH2O']) else "N/A")
with qc2:
	st.metric("Max |Error| vs Paper (mmH2O)", f"{q['max_abs_error_mmH2O']:.1f}" if np.isfinite(q['max_abs_error_mmH2O']) else "N/A")

# Comparison plot (mmH2O)
paper = load_paper_validation()
paper_t = np.asarray(paper["pressure_chamber"]["time"], dtype=float)
paper_p = np.asarray(paper["pressure_chamber"]["pressure"], dtype=float)

sim_t_s = time_min * 60.0
order = np.argsort(sim_t_s)
sim_t_sorted = sim_t_s[order]
sim_dp_sorted = dP_mmH2O[order]

fig_comp = go.Figure()
fig_comp.add_trace(go.Scatter(x=paper_t, y=paper_p, name="Paper (mmH2O)", mode="markers+lines"))
fig_comp.add_trace(go.Scatter(x=sim_t_sorted, y=sim_dp_sorted, name="Simulation (mmH2O)", mode="lines"))
fig_comp.update_layout(
	template="plotly_white",
	title="Pressure Chamber Comparison (ΔP in mmH2O)",
	xaxis_title="Time (s)",
	yaxis_title="ΔP (mmH2O)",
	height=440,
)
st.plotly_chart(fig_comp, use_container_width=True)


# ------------------------------- Data View ------------------------------- #
st.header("Data and Export")

# Assemble tidy DataFrame
_df = pd.DataFrame({
	"time_min": time_min,
	"altitude_ft": results["altitude"],
	"P_cabin_mmHg": P_cabin,
	"P_ME_mmHg": P_ME,
	"dP_mmHg": dP,
	"dP_mmH2O": dP_mmH2O,
	"ET_locked": results["ET_locked"].astype(int),
	"barotitis": results["barotitis"].astype(int),
	"baromyringitis": results["baromyringitis"].astype(int),
	"risk_factor": results["risk_factor"],
})
st.dataframe(_df.head(200).round(3), use_container_width=True)

csv_bytes = _df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv_bytes, file_name="simulation_results.csv", mime="text/csv")