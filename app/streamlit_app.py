import numpy as np
import streamlit as st

from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
    ET_SEVERITY_TO_DYSFUNCTION,
)
from barotrauma.analysis.visualization import BarotraumaVisualizer
from barotrauma.analysis.statistics import StatisticalAnalyzer


st.set_page_config(page_title="Hypobaric Chamber Barotrauma Risk",
                   layout="wide")

st.title("Hypobaric Chamber Training – Middle Ear Barotrauma Risk")
st.markdown(
    "Use this tool to explore how Eustachian tube (ET) dysfunction and"
    " descent rate affect middle-ear pressure, based on physiology and"
    " Boyle's law."
)

with st.sidebar:
    st.header("Scenario")
    et_severity = st.selectbox("ET Dysfunction", ["mild", "moderate", "severe"], index=1)
    start_alt = st.slider("Start Altitude (ft)", 8000, 30000, 25000, step=1000)
    descent_rate = st.slider("Descent Rate (ft/min)", 1000, 10000, 3000, step=100)
    enable_valsava = st.checkbox("Enable periodic Valsalva", value=True)
    valsalva_interval = st.slider("Valsalva interval (s)", 30, 600, 120, step=15)

    st.header("Anatomy (optional)")
    tympanum_ml = st.number_input(
        "Tympanum Volume (mL)", 0.5, 3.0, 1.0, step=0.1
    )
    mastoid_ml = st.number_input(
        "Mastoid Volume (mL)", 3.0, 15.0, 7.75, step=0.25
    )

scenario = ChamberScenario(
    start_altitude_ft=float(start_alt),
    descent_rate_ft_min=float(descent_rate),
    et_severity=et_severity,
    enable_valsava=enable_valsava,
    valsalva_interval_s=float(valsalva_interval),
    tympanum_volume_ml=float(tympanum_ml),
    mastoid_volume_ml=float(mastoid_ml),
)

model = HypobaricChamberRiskModel()
result = model.simulate_descent(scenario)
visual = BarotraumaVisualizer()
stats = StatisticalAnalyzer()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Risk Score", f"{result.risk_score:.2f}",
            help="0 = low, 1 = high")
col2.metric("Risk Category", result.risk_category)
col3.metric(
    "Max |ΔP| (mmHg)", f"{np.max(np.abs(result.delta_P_mmHg)):.1f}"
)
col4.metric("Time > ET Lock", f"{result.metrics['fraction_time_above_lock']*100:.1f}%")

st.subheader("Pressure and Altitude Over Time")
tab1, tab2, tab3 = st.tabs(["Pressures", "Equalization", "Risk vs Descent Rate"])

with tab1:
    st.line_chart(
        {
            "Ambient Pressure (mmHg)": result.P_amb_mmHg,
            "Middle Ear Pressure (mmHg)": result.P_ME_mmHg,
            "ΔP (mmHg)": result.delta_P_mmHg,
        },
        x=result.time_s,
    )
    # 3D interactive surface of ΔP vs time vs altitude
    fig3d = visual.plot_3d_pressure_surface(
        time=result.time_s,
        altitude=result.altitude_ft,
        delta_p=np.tile(result.delta_P_mmHg, (len(result.altitude_ft), 1)),
    )
    st.plotly_chart(fig3d, use_container_width=True)
    st.caption(
        "During descent, ambient pressure rises. Without equalization,"
        " middle-ear pressure lags, pulling the TM inward. Valsalva helps"
        " normalize pressure."
    )

with tab2:
    st.line_chart(
        {
            "Equalization speed (mmHg/s)": result.equalization_rate_mmHg_s,
            "TM displacement (mL, signed)": result.tm_displacement_ml,
        },
        x=result.time_s,
    )
    cloud3d = visual.plot_3d_equalization_field(
        time=result.time_s,
        eq_rate=result.equalization_rate_mmHg_s,
        delta_p=result.delta_P_mmHg,
    )
    st.plotly_chart(cloud3d, use_container_width=True)
    st.caption(
        "Equalization speed reflects ET function and descent rate; TM"
        " displacement reflects tension per compliance."
    )

with tab3:
    st.write("Risk across descent rates for the selected ET severity")
    rates = np.linspace(1000, 10000, 19)
    _, scores = model.risk_vs_descent_rate(scenario, rates)
    st.line_chart({"Risk Score": scores}, x=rates)
    st.caption(
        "Risk increases nonlinearly beyond severity-specific safe rates."
    )

# Statistical metrics summary
metrics = stats.compute_metrics(
    {
        'dP': result.delta_P_mmHg,
        'equalization_rate': result.equalization_rate_mmHg_s,
    }
)
st.subheader("Validation Metrics")
st.json(metrics)

st.divider()
st.markdown(
    f"ET severity '{et_severity}' modeled as dysfunction level "
    f"{ET_SEVERITY_TO_DYSFUNCTION[et_severity]:.2f}."
)



