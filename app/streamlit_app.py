"""
Barotrauma Risk Assessment Application

A modern, interactive tool for analyzing middle ear barotrauma risk 
during hypobaric chamber training and flight operations.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
    ET_SEVERITY_TO_DYSFUNCTION,
    ET_LOCK_THRESHOLD,
    MEMBRANE_RUPTURE_THRESHOLD,
)
from barotrauma.analysis.visualization import BarotraumaVisualizer
from barotrauma.analysis.statistics import StatisticalAnalyzer

# --------------------------------------------------------------------------- #
# Page Configuration & Custom Styling
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Barotrauma Risk Assessment",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, rgba(30, 58, 95, 0.7), rgba(20, 40, 70, 0.9));
        border: 1px solid rgba(100, 180, 255, 0.2);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    div[data-testid="metric-container"] label {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        color: #a0c4ff !important;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
        border-right: 1px solid rgba(100, 180, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffd700 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 58, 95, 0.3);
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #2563eb, #1d4ed8) !important;
        color: white !important;
    }
    
    /* Risk indicator badges */
    .risk-low { 
        background: linear-gradient(145deg, #059669, #047857);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
    }
    .risk-moderate { 
        background: linear-gradient(145deg, #d97706, #b45309);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
    }
    .risk-high { 
        background: linear-gradient(145deg, #dc2626, #b91c1c);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(30, 58, 95, 0.4);
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 0 10px 10px 0;
        margin: 10px 0;
    }
    
    /* Warning boxes */
    .warning-box {
        background: rgba(180, 83, 9, 0.2);
        border-left: 4px solid #f59e0b;
        padding: 16px;
        border-radius: 0 10px 10px 0;
        margin: 10px 0;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #059669, #d97706, #dc2626) !important;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Header Section
# --------------------------------------------------------------------------- #
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("# 🫁")
with col_title:
    st.title("Barotrauma Risk Assessment System")
    st.caption("*Physics-informed analysis for hypobaric chamber training & flight safety*")

st.markdown("---")

# --------------------------------------------------------------------------- #
# Sidebar Configuration
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Scenario Type
    st.markdown("### 📋 Scenario")
    scenario_type = st.radio(
        "Environment",
        ["🎈 Hypobaric Chamber", "✈️ Flight Simulation"],
        horizontal=True,
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    
    # Physiological Parameters
    st.markdown("### 🩺 Physiological Parameters")
    
    et_severity = st.select_slider(
        "ET Dysfunction Severity",
        options=["mild", "moderate", "severe"],
        value="moderate",
        help="Eustachian tube dysfunction level affects equalization capability",
    )
    
    # Show dysfunction percentage
    dysfunction_pct = ET_SEVERITY_TO_DYSFUNCTION[et_severity] * 100
    st.progress(dysfunction_pct / 100)
    st.caption(f"Dysfunction Level: **{dysfunction_pct:.0f}%**")
    
    st.markdown("---")
    
    # Flight/Chamber Parameters
    st.markdown("### 🎯 Profile Parameters")
    
    start_alt = st.slider(
        "Starting Altitude (ft)",
        min_value=8000,
        max_value=40000,
        value=25000,
        step=1000,
        help="Initial altitude before descent",
    )
    
    descent_rate = st.slider(
        "Descent Rate (ft/min)",
        min_value=1000,
        max_value=10000,
        value=3000,
        step=100,
        help="Rate of altitude change during descent",
    )
    
    # Visual indicator for descent rate safety
    if descent_rate <= 2000:
        st.success("✅ Safe descent rate")
    elif descent_rate <= 5000:
        st.warning("⚠️ Moderate risk descent rate")
    else:
        st.error("🚨 High risk descent rate")
    
    st.markdown("---")
    
    # Valsalva Settings
    st.markdown("### 💨 Equalization Protocol")
    enable_valsalva = st.toggle("Enable Valsalva Maneuvers", value=True)
    
    if enable_valsalva:
        valsalva_interval = st.slider(
            "Valsalva Interval (seconds)",
            min_value=30,
            max_value=300,
            value=60,
            step=15,
            help="Time between equalization attempts",
        )
    else:
        valsalva_interval = 999999
    
    st.markdown("---")
    
    # Advanced Anatomy (Expander)
    with st.expander("🔬 Advanced: Anatomy Settings"):
        tympanum_ml = st.slider(
            "Tympanum Volume (mL)",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
        )
        mastoid_ml = st.slider(
            "Mastoid Volume (mL)",
            min_value=3.0,
            max_value=15.0,
            value=7.75,
            step=0.25,
        )


# --------------------------------------------------------------------------- #
# Run Simulation
# --------------------------------------------------------------------------- #
scenario = ChamberScenario(
    start_altitude_ft=float(start_alt),
    descent_rate_ft_min=float(descent_rate),
    et_severity=et_severity,
    enable_valsava=enable_valsalva,
    valsalva_interval_s=float(valsalva_interval),
    tympanum_volume_ml=float(tympanum_ml),
    mastoid_volume_ml=float(mastoid_ml),
)

model = HypobaricChamberRiskModel()
result = model.simulate_descent(scenario)
visual = BarotraumaVisualizer()
stats = StatisticalAnalyzer()

# --------------------------------------------------------------------------- #
# Risk Summary Dashboard
# --------------------------------------------------------------------------- #
st.markdown("## 📊 Risk Assessment Summary")

# Risk category styling
risk_class = {
    "Low": "risk-low",
    "Moderate": "risk-moderate", 
    "High": "risk-high",
}[result.risk_category]

# Main metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    risk_emoji = "🟢" if result.risk_score < 0.3 else "🟡" if result.risk_score < 0.6 else "🔴"
    st.metric(
        label="Risk Score",
        value=f"{risk_emoji} {result.risk_score:.2f}",
        delta=f"{(result.risk_score - 0.3) * 100:+.1f}% from baseline",
        delta_color="inverse",
    )

with col2:
    st.metric(
        label="Risk Category",
        value=result.risk_category,
        help="Clinical risk classification based on integrated metrics",
    )

with col3:
    max_dp = float(np.max(np.abs(result.delta_P_mmHg)))
    st.metric(
        label="Max |ΔP|",
        value=f"{max_dp:.1f} mmHg",
        delta=f"{max_dp - ET_LOCK_THRESHOLD:.1f} vs ET Lock",
        delta_color="inverse" if max_dp > ET_LOCK_THRESHOLD else "off",
    )

with col4:
    lock_pct = result.metrics["fraction_time_above_lock"] * 100
    st.metric(
        label="Time > ET Lock",
        value=f"{lock_pct:.1f}%",
        help=f"Fraction of time with |ΔP| > {ET_LOCK_THRESHOLD} mmHg",
    )

with col5:
    max_tm = float(np.max(np.abs(result.tm_displacement_ml))) * 1000
    st.metric(
        label="Max TM Displacement",
        value=f"{max_tm:.1f} µL",
        help="Maximum tympanic membrane displacement",
    )

# Clinical recommendations based on risk
st.markdown("---")
if result.risk_category == "High":
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ HIGH RISK - Immediate Action Required</h4>
        <ul>
            <li>Reduce descent rate to < 1500 ft/min</li>
            <li>Increase Valsalva frequency (every 30 seconds)</li>
            <li>Monitor for symptoms: ear pain, hearing changes, vertigo</li>
            <li>Consider medical intervention if symptoms persist</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
elif result.risk_category == "Moderate":
    st.markdown("""
    <div class="info-box">
        <h4>⚡ MODERATE RISK - Caution Advised</h4>
        <ul>
            <li>Consider reducing descent rate to < 2500 ft/min</li>
            <li>Maintain regular Valsalva maneuvers (every 60 seconds)</li>
            <li>Stay alert for early symptoms</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success("✅ **LOW RISK** - Current parameters within safe operational limits. Continue standard monitoring.")


# --------------------------------------------------------------------------- #
# Detailed Analysis Tabs
# --------------------------------------------------------------------------- #
st.markdown("---")
st.markdown("## 📈 Detailed Analysis")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌡️ Pressure Dynamics", 
    "⚖️ Equalization Analysis", 
    "📉 Risk Sensitivity",
    "📋 Data Export"
])

with tab1:
    st.markdown("### Pressure Evolution During Descent")
    
    # Create interactive pressure chart with Plotly
    fig_pressure = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Pressure Profiles", "Pressure Differential (ΔP)"),
        row_heights=[0.6, 0.4],
    )
    
    time_min = result.time_s / 60
    
    # Ambient and ME pressure
    fig_pressure.add_trace(
        go.Scatter(
            x=time_min, y=result.P_amb_mmHg,
            name="Ambient Pressure",
            line=dict(color="#3b82f6", width=2),
            hovertemplate="Time: %{x:.1f} min<br>P_amb: %{y:.1f} mmHg<extra></extra>",
        ),
        row=1, col=1,
    )
    fig_pressure.add_trace(
        go.Scatter(
            x=time_min, y=result.P_ME_mmHg,
            name="Middle Ear Pressure",
            line=dict(color="#10b981", width=2),
            hovertemplate="Time: %{x:.1f} min<br>P_ME: %{y:.1f} mmHg<extra></extra>",
        ),
        row=1, col=1,
    )
    
    # Pressure differential
    fig_pressure.add_trace(
        go.Scatter(
            x=time_min, y=result.delta_P_mmHg,
            name="ΔP (P_ME - P_amb)",
            line=dict(color="#f59e0b", width=2),
            fill="tozeroy",
            fillcolor="rgba(245, 158, 11, 0.2)",
            hovertemplate="Time: %{x:.1f} min<br>ΔP: %{y:.1f} mmHg<extra></extra>",
        ),
        row=2, col=1,
    )
    
    # Add threshold lines
    fig_pressure.add_hline(
        y=-ET_LOCK_THRESHOLD, line_dash="dash", line_color="#f97316",
        annotation_text="ET Lock Threshold", row=2, col=1,
    )
    fig_pressure.add_hline(
        y=-MEMBRANE_RUPTURE_THRESHOLD, line_dash="dot", line_color="#dc2626",
        annotation_text="Rupture Risk", row=2, col=1,
    )
    
    fig_pressure.update_layout(
        height=600,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,58,95,0.3)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    fig_pressure.update_xaxes(title_text="Time (minutes)", row=2, col=1)
    fig_pressure.update_yaxes(title_text="Pressure (mmHg)", row=1, col=1)
    fig_pressure.update_yaxes(title_text="ΔP (mmHg)", row=2, col=1)
    
    st.plotly_chart(fig_pressure, use_container_width=True)
    
    st.caption(
        "**Interpretation:** During descent, ambient pressure rises. The middle ear "
        "attempts to equalize through the Eustachian tube. Negative ΔP indicates the "
        "tympanic membrane is being pulled inward."
    )


with tab2:
    st.markdown("### Equalization Dynamics")
    
    col_eq1, col_eq2 = st.columns(2)
    
    with col_eq1:
        # Equalization rate chart
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=time_min, y=result.equalization_rate_mmHg_s,
            mode="lines",
            name="Equalization Rate",
            line=dict(color="#8b5cf6", width=2),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.2)",
        ))
        fig_eq.update_layout(
            title="Equalization Rate Over Time",
            xaxis_title="Time (minutes)",
            yaxis_title="Rate (mmHg/s)",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(30,58,95,0.3)",
            height=350,
        )
        st.plotly_chart(fig_eq, use_container_width=True)
    
    with col_eq2:
        # TM Displacement chart
        fig_tm = go.Figure()
        fig_tm.add_trace(go.Scatter(
            x=time_min, y=result.tm_displacement_ml * 1000,
            mode="lines",
            name="TM Displacement",
            line=dict(color="#ec4899", width=2),
            fill="tozeroy",
            fillcolor="rgba(236, 72, 153, 0.2)",
        ))
        fig_tm.update_layout(
            title="Tympanic Membrane Displacement",
            xaxis_title="Time (minutes)",
            yaxis_title="Displacement (µL)",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(30,58,95,0.3)",
            height=350,
        )
        st.plotly_chart(fig_tm, use_container_width=True)
    
    # 3D Visualization
    st.markdown("#### 3D Equalization Field")
    fig_3d = visual.plot_3d_equalization_field(
        time=result.time_s,
        eq_rate=result.equalization_rate_mmHg_s,
        delta_p=result.delta_P_mmHg,
    )
    fig_3d.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_3d, use_container_width=True)


with tab3:
    st.markdown("### Risk Sensitivity Analysis")
    
    # Risk vs Descent Rate
    st.markdown("#### Risk Score vs Descent Rate")
    rates = np.linspace(1000, 10000, 37)
    _, scores = model.risk_vs_descent_rate(scenario, rates)
    
    fig_sensitivity = go.Figure()
    
    # Add risk zones
    fig_sensitivity.add_hrect(y0=0, y1=0.3, fillcolor="green", opacity=0.1, 
                              annotation_text="Low Risk", annotation_position="top left")
    fig_sensitivity.add_hrect(y0=0.3, y1=0.6, fillcolor="yellow", opacity=0.1,
                              annotation_text="Moderate Risk", annotation_position="top left")
    fig_sensitivity.add_hrect(y0=0.6, y1=1.0, fillcolor="red", opacity=0.1,
                              annotation_text="High Risk", annotation_position="top left")
    
    fig_sensitivity.add_trace(go.Scatter(
        x=rates, y=scores,
        mode="lines+markers",
        name=f"ET Severity: {et_severity}",
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=4),
    ))
    
    # Mark current position
    fig_sensitivity.add_trace(go.Scatter(
        x=[descent_rate], y=[result.risk_score],
        mode="markers",
        name="Current Setting",
        marker=dict(color="#fbbf24", size=15, symbol="star"),
    ))
    
    fig_sensitivity.update_layout(
        xaxis_title="Descent Rate (ft/min)",
        yaxis_title="Risk Score",
        yaxis_range=[0, 1],
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,58,95,0.3)",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # Risk Heatmap
    st.markdown("#### Risk Heatmap: Severity × Descent Rate")
    severities = ["mild", "moderate", "severe"]
    score_matrix = []
    for sev in severities:
        scn = ChamberScenario(
            start_altitude_ft=float(start_alt),
            descent_rate_ft_min=float(descent_rate),
            et_severity=sev,
            enable_valsava=enable_valsalva,
            valsalva_interval_s=float(valsalva_interval),
            tympanum_volume_ml=float(tympanum_ml),
            mastoid_volume_ml=float(mastoid_ml),
        )
        _, ssev = model.risk_vs_descent_rate(scn, rates)
        score_matrix.append(ssev)
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=score_matrix,
        x=rates,
        y=severities,
        colorscale="RdYlGn_r",
        zmin=0,
        zmax=1,
        colorbar=dict(title="Risk Score"),
        hovertemplate="Descent: %{x} ft/min<br>Severity: %{y}<br>Risk: %{z:.2f}<extra></extra>",
    ))
    fig_heat.update_layout(
        xaxis_title="Descent Rate (ft/min)",
        yaxis_title="ET Severity",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300,
    )
    st.plotly_chart(fig_heat, use_container_width=True)


with tab4:
    st.markdown("### Simulation Data & Export")
    
    # Create DataFrame for export
    df_results = pd.DataFrame({
        "Time (s)": result.time_s,
        "Time (min)": result.time_s / 60,
        "Altitude (ft)": result.altitude_ft,
        "P_ambient (mmHg)": result.P_amb_mmHg,
        "P_middle_ear (mmHg)": result.P_ME_mmHg,
        "Delta_P (mmHg)": result.delta_P_mmHg,
        "TM_displacement (mL)": result.tm_displacement_ml,
        "Equalization_rate (mmHg/s)": result.equalization_rate_mmHg_s,
    })
    
    col_preview, col_download = st.columns([2, 1])
    
    with col_preview:
        st.markdown("#### Data Preview")
        st.dataframe(
            df_results.head(100).round(3),
            use_container_width=True,
            height=300,
        )
    
    with col_download:
        st.markdown("#### Export Options")
        
        # CSV Download
        csv_data = df_results.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="barotrauma_simulation.csv",
            mime="text/csv",
            use_container_width=True,
        )
        
        # Metrics summary
        st.markdown("#### Summary Metrics")
        metrics_summary = {
            "Risk Score": f"{result.risk_score:.3f}",
            "Risk Category": result.risk_category,
            "Max |ΔP| (mmHg)": f"{max_dp:.2f}",
            "Mean |ΔP| (mmHg)": f"{np.mean(np.abs(result.delta_P_mmHg)):.2f}",
            "Time > ET Lock": f"{lock_pct:.1f}%",
            "Descent Duration (min)": f"{result.time_s[-1]/60:.1f}",
        }
        for key, value in metrics_summary.items():
            st.markdown(f"**{key}:** {value}")


# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #
st.markdown("---")

col_footer1, col_footer2 = st.columns(2)

with col_footer1:
    st.markdown("""
    **Model Information:**
    - Based on Kanick & Doyle (2005) physiological parameters
    - Uses Boyle's Law (P₁V₁ = P₂V₂) for pressure-volume relationships
    - ET dysfunction modeled as continuous function affecting equalization kinetics
    """)

with col_footer2:
    st.markdown(f"""
    **Current Configuration:**
    - ET Severity: `{et_severity}` (dysfunction: {ET_SEVERITY_TO_DYSFUNCTION[et_severity]:.2f})
    - Altitude: `{start_alt:,}` ft → sea level
    - Descent Rate: `{descent_rate:,}` ft/min
    - Valsalva: `{'Enabled' if enable_valsalva else 'Disabled'}`
    """)

st.caption("*Barotrauma Risk Assessment System v2.0 | For research and educational purposes*")

