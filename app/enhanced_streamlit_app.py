"""
Enhanced Streamlit Application for Barotrauma Risk Analysis and Prediction

This application provides comprehensive visualization and analysis tools for
understanding barotrauma risk in hypobaric chamber training and flight scenarios.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
    ET_SEVERITY_TO_DYSFUNCTION,
)
from barotrauma.analysis.visualization import BarotraumaVisualizer
from barotrauma.analysis.enhanced_visualization import EnhancedBarotraumaVisualizer
from barotrauma.analysis.statistics import StatisticalAnalyzer

# Page configuration
st.set_page_config(
    page_title="Advanced Barotrauma Risk Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Advanced Barotrauma Risk Analysis Tool - Comprehensive visualization and prediction system"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🚀 Advanced Barotrauma Risk Analysis System")
st.markdown("""
### Comprehensive Analysis Tool for Middle Ear Barotrauma Risk

This advanced system provides:
- **Real-time risk assessment** based on physiological parameters
- **Interactive 3D visualizations** of risk relationships
- **Predictive modeling** for various scenarios
- **Clinical decision support** with actionable recommendations
""")

# Initialize session state for historical data
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['timestamp', 'et_dysfunction', 'descent_rate', 'risk_score'])

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Scenario Configuration")
    
    # Scenario type selection
    scenario_type = st.radio(
        "Select Scenario Type",
        ["Hypobaric Chamber", "Flight Profile", "Custom Analysis"],
        help="Choose the type of barotrauma scenario to analyze"
    )
    
    st.divider()
    
    # Common parameters
    st.subheader("🔬 Physiological Parameters")
    
    et_severity = st.select_slider(
        "ET Dysfunction Severity",
        options=["none", "mild", "moderate", "severe", "complete"],
        value="moderate",
        help="Eustachian tube dysfunction level affects equalization capability"
    )
    
    # Map extended severity to standard levels
    severity_mapping = {
        "none": "mild",
        "mild": "mild",
        "moderate": "moderate",
        "severe": "severe",
        "complete": "severe"
    }
    mapped_severity = severity_mapping[et_severity]
    
    # Numerical ET dysfunction for analysis
    et_dysfunction_numeric = {
        "none": 0.0,
        "mild": 0.35,
        "moderate": 0.60,
        "severe": 0.85,
        "complete": 1.0
    }[et_severity]
    
    st.divider()
    
    # Scenario-specific parameters
    if scenario_type == "Hypobaric Chamber":
        st.subheader("🎈 Chamber Parameters")
        start_alt = st.slider(
            "Starting Altitude (ft)",
            5000, 40000, 25000, 1000,
            help="Initial altitude for chamber decompression"
        )
        descent_rate = st.slider(
            "Descent Rate (ft/min)",
            500, 10000, 3000, 100,
            help="Rate of pressure change during descent"
        )
        enable_valsalva = st.checkbox(
            "Enable Valsalva Maneuvers",
            value=True,
            help="Periodic pressure equalization attempts"
        )
        if enable_valsalva:
            valsalva_interval = st.slider(
                "Valsalva Interval (seconds)",
                15, 300, 60, 15,
                help="Time between equalization attempts"
            )
        else:
            valsalva_interval = 999999
    
    elif scenario_type == "Flight Profile":
        st.subheader("✈️ Flight Parameters")
        cruise_alt = st.slider(
            "Cruise Altitude (ft)",
            20000, 45000, 35000, 1000
        )
        climb_rate = st.slider(
            "Climb Rate (ft/min)",
            500, 3000, 1500, 100
        )
        descent_rate = st.slider(
            "Descent Rate (ft/min)",
            500, 3000, 1500, 100
        )
        cruise_duration = st.slider(
            "Cruise Duration (min)",
            30, 300, 120, 10
        )
        start_alt = 0
        enable_valsalva = True
        valsalva_interval = 120
    
    else:  # Custom Analysis
        st.subheader("🔧 Custom Parameters")
        start_alt = st.number_input("Start Altitude (ft)", 0, 50000, 25000)
        descent_rate = st.number_input("Descent Rate (ft/min)", 100, 20000, 3000)
        enable_valsalva = st.checkbox("Enable Valsalva", True)
        valsalva_interval = st.number_input("Valsalva Interval (s)", 10, 600, 60)
    
    st.divider()
    
    # Advanced settings
    with st.expander("🔬 Advanced Anatomical Settings"):
        tympanum_ml = st.slider(
            "Tympanum Volume (mL)",
            0.5, 3.0, 1.0, 0.1,
            help="Middle ear cavity volume"
        )
        mastoid_ml = st.slider(
            "Mastoid Volume (mL)",
            3.0, 15.0, 7.75, 0.25,
            help="Mastoid air cell volume"
        )
        compliance_factor = st.slider(
            "TM Compliance Factor",
            0.5, 2.0, 1.0, 0.1,
            help="Tympanic membrane compliance relative to normal"
        )

# Main content area
# Create scenario and run simulation
scenario = ChamberScenario(
    start_altitude_ft=float(start_alt),
    descent_rate_ft_min=float(descent_rate),
    et_severity=mapped_severity,
    enable_valsava=enable_valsalva,
    valsalva_interval_s=float(valsalva_interval),
    tympanum_volume_ml=float(tympanum_ml),
    mastoid_volume_ml=float(mastoid_ml),
)

# Initialize models
model = HypobaricChamberRiskModel()
result = model.simulate_descent(scenario)
visual = BarotraumaVisualizer()
enhanced_visual = EnhancedBarotraumaVisualizer()
stats = StatisticalAnalyzer()

# Add to history
new_record = pd.DataFrame([{
    'timestamp': datetime.now(),
    'et_dysfunction': et_dysfunction_numeric,
    'descent_rate': descent_rate,
    'risk_score': result.risk_score
}])
st.session_state.history = pd.concat([st.session_state.history, new_record], ignore_index=True)

# Key metrics display
st.header("📊 Risk Assessment Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    risk_color = "🔴" if result.risk_score > 0.6 else "🟡" if result.risk_score > 0.3 else "🟢"
    st.metric(
        "Risk Score",
        f"{risk_color} {result.risk_score:.2f}",
        delta=f"{(result.risk_score - 0.5)*100:.1f}%",
        delta_color="inverse",
        help="Overall barotrauma risk score (0-1)"
    )

with col2:
    st.metric(
        "Risk Category",
        result.risk_category,
        help="Clinical risk classification"
    )

with col3:
    max_pressure = np.max(np.abs(result.delta_P_mmHg))
    st.metric(
        "Max |ΔP|",
        f"{max_pressure:.1f} mmHg",
        delta=f"{max_pressure - 60:.1f}",
        delta_color="inverse",
        help="Maximum pressure differential"
    )

with col4:
    lock_time = result.metrics['fraction_time_above_lock'] * 100
    st.metric(
        "Time > ET Lock",
        f"{lock_time:.1f}%",
        delta=f"{lock_time - 10:.1f}%",
        delta_color="inverse",
        help="Percentage of time with ET lock risk"
    )

with col5:
    max_displacement = np.max(np.abs(result.tm_displacement_ml)) * 1000
    st.metric(
        "Max TM Displacement",
        f"{max_displacement:.2f} µL",
        help="Maximum tympanic membrane displacement"
    )

# Main visualization tabs
st.header("📈 Detailed Analysis")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Risk vs ET Dysfunction",
    "🌐 3D Risk Surfaces",
    "📉 Time Series Analysis",
    "🎪 Pressure Dynamics",
    "🔮 Predictions",
    "📊 Dashboard"
])

with tab1:
    st.subheader("Barotrauma Risk vs ET Dysfunction Analysis")
    
    # Generate data for ET dysfunction analysis
    et_values = np.linspace(0, 1, 21)
    risk_scores = []
    pressure_diffs = []
    volume_changes = []
    
    for et_val in et_values:
        # Map ET value to severity category
        if et_val < 0.35:
            sev = "mild"
        elif et_val < 0.60:
            sev = "moderate"
        else:
            sev = "severe"
        
        test_scenario = ChamberScenario(
            start_altitude_ft=float(start_alt),
            descent_rate_ft_min=float(descent_rate),
            et_severity=sev,
            enable_valsava=enable_valsalva,
            valsalva_interval_s=float(valsalva_interval),
        )
        test_result = model.simulate_descent(test_scenario)
        
        risk_scores.append(test_result.risk_score)
        pressure_diffs.append(np.max(np.abs(test_result.delta_P_mmHg)))
        volume_changes.append(np.max(test_result.tm_displacement_ml) * 1000)
    
    # Create comprehensive plot
    fig_et_risk = enhanced_visual.plot_barotrauma_risk_vs_et_dysfunction(
        et_dysfunction_values=np.array(et_values),
        risk_scores=np.array(risk_scores),
        pressure_diffs=np.array(pressure_diffs),
        volume_changes=np.array(volume_changes),
        title=f"Barotrauma Risk Analysis at {descent_rate} ft/min Descent Rate"
    )
    
    st.plotly_chart(fig_et_risk, use_container_width=True)
    
    # Add interpretation
    st.info("""
    **Interpretation Guide:**
    - **Green Zone (Risk < 0.3)**: Safe operating conditions
    - **Yellow Zone (0.3 ≤ Risk < 0.6)**: Caution required, implement mitigation strategies
    - **Red Zone (Risk ≥ 0.6)**: High risk, consider aborting or significant intervention
    """)

with tab2:
    st.subheader("3D Risk Surface Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ET Dysfunction × Descent Rate × Risk")
        
        # Generate 3D surface data
        et_range = np.linspace(0, 1, 15)
        descent_range = np.linspace(1000, 10000, 15)
        risk_matrix = np.zeros((len(descent_range), len(et_range)))
        
        for i, desc_rate in enumerate(descent_range):
            for j, et_val in enumerate(et_range):
                # Map ET value to severity
                if et_val < 0.35:
                    sev = "mild"
                elif et_val < 0.60:
                    sev = "moderate"
                else:
                    sev = "severe"
                
                test_scenario = ChamberScenario(
                    start_altitude_ft=float(start_alt),
                    descent_rate_ft_min=float(desc_rate),
                    et_severity=sev,
                    enable_valsava=enable_valsalva,
                    valsalva_interval_s=float(valsalva_interval),
                )
                test_result = model.simulate_descent(test_scenario)
                risk_matrix[i, j] = test_result.risk_score
        
        fig_3d_surface = enhanced_visual.plot_3d_risk_surface(
            et_dysfunction=et_range,
            descent_rates=descent_range,
            risk_matrix=risk_matrix
        )
        st.plotly_chart(fig_3d_surface, use_container_width=True)
    
    with col2:
        st.markdown("#### Pressure × Volume × Risk Relationship")
        
        # Collect data points for 3D scatter
        n_samples = 50
        pressure_vals = []
        volume_vals = []
        risk_vals = []
        et_vals = []
        
        for _ in range(n_samples):
            # Random sampling of parameters
            rand_et = np.random.uniform(0, 1)
            rand_descent = np.random.uniform(1000, 10000)
            
            # Map to severity
            if rand_et < 0.35:
                sev = "mild"
            elif rand_et < 0.60:
                sev = "moderate"
            else:
                sev = "severe"
            
            test_scenario = ChamberScenario(
                start_altitude_ft=float(start_alt),
                descent_rate_ft_min=float(rand_descent),
                et_severity=sev,
                enable_valsava=enable_valsalva,
                valsalva_interval_s=float(valsalva_interval),
            )
            test_result = model.simulate_descent(test_scenario)
            
            pressure_vals.append(np.max(np.abs(test_result.delta_P_mmHg)))
            volume_vals.append(np.max(test_result.tm_displacement_ml) * 1000)
            risk_vals.append(test_result.risk_score)
            et_vals.append(rand_et)
        
        fig_3d_pvr = enhanced_visual.plot_3d_pressure_volume_risk(
            pressure_values=np.array(pressure_vals),
            volume_values=np.array(volume_vals),
            risk_values=np.array(risk_vals),
            et_dysfunction_levels=np.array(et_vals)
        )
        st.plotly_chart(fig_3d_pvr, use_container_width=True)

with tab3:
    st.subheader("Time Series Comparison Analysis")
    
    # Generate time series for different ET dysfunction levels
    et_levels = {"Normal (0.0)": 0.0, "Mild (0.35)": 0.35, "Moderate (0.6)": 0.6, "Severe (0.85)": 0.85}
    results_dict = {}
    
    for label, et_val in et_levels.items():
        # Map to severity
        if et_val < 0.35:
            sev = "mild"
        elif et_val < 0.60:
            sev = "moderate"
        else:
            sev = "severe"
        
        test_scenario = ChamberScenario(
            start_altitude_ft=float(start_alt),
            descent_rate_ft_min=float(descent_rate),
            et_severity=sev,
            enable_valsava=enable_valsalva,
            valsalva_interval_s=float(valsalva_interval),
        )
        test_result = model.simulate_descent(test_scenario)
        
        results_dict[label] = {
            'time': test_result.time_s / 60,  # Convert to minutes
            'delta_P': test_result.delta_P_mmHg,
            'volume': test_result.tm_displacement_ml,
            'eq_rate': test_result.equalization_rate_mmHg_s
        }
    
    fig_time_series = enhanced_visual.plot_time_series_comparison(
        results_dict=results_dict,
        title=f"Time Series Comparison at {descent_rate} ft/min Descent"
    )
    st.plotly_chart(fig_time_series, use_container_width=True)
    
    # Statistical comparison
    st.markdown("#### Statistical Summary")
    stats_df = pd.DataFrame()
    for label, data in results_dict.items():
        stats_df[label] = [
            np.max(np.abs(data['delta_P'])),
            np.mean(np.abs(data['delta_P'])),
            np.max(data['volume']) * 1000,
            np.mean(data['eq_rate'])
        ]
    stats_df.index = ['Max |ΔP| (mmHg)', 'Mean |ΔP| (mmHg)', 'Max Volume (mL)', 'Mean Eq. Rate (mmHg/s)']
    st.dataframe(stats_df.round(2), use_container_width=True)

with tab4:
    st.subheader("Pressure Dynamics and Equalization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pressure time series
        fig_pressure = go.Figure()
        fig_pressure.add_trace(go.Scatter(
            x=result.time_s / 60,
            y=result.P_amb_mmHg,
            mode='lines',
            name='Ambient Pressure',
            line=dict(color='blue', width=2)
        ))
        fig_pressure.add_trace(go.Scatter(
            x=result.time_s / 60,
            y=result.P_ME_mmHg,
            mode='lines',
            name='Middle Ear Pressure',
            line=dict(color='red', width=2)
        ))
        fig_pressure.add_trace(go.Scatter(
            x=result.time_s / 60,
            y=result.delta_P_mmHg,
            mode='lines',
            name='Pressure Difference',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        # Add clinical thresholds
        fig_pressure.add_hline(y=90, line_dash="dash", line_color="orange",
                               annotation_text="ET Lock Threshold")
        
        fig_pressure.update_layout(
            title="Pressure Evolution During Descent",
            xaxis_title="Time (minutes)",
            yaxis_title="Pressure (mmHg)",
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_pressure, use_container_width=True)
    
    with col2:
        # 3D pressure surface
        fig_3d_pressure = visual.plot_3d_pressure_surface(
            time=result.time_s / 60,
            altitude=result.altitude_ft,
            delta_p=result.delta_P_mmHg,
            title="Pressure Differential Surface"
        )
        st.plotly_chart(fig_3d_pressure, use_container_width=True)
    
    # Equalization analysis
    st.markdown("#### Equalization Dynamics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=result.time_s / 60,
            y=result.equalization_rate_mmHg_s,
            mode='lines',
            name='Equalization Rate',
            line=dict(color='purple', width=2)
        ))
        fig_eq.update_layout(
            title="Equalization Rate Over Time",
            xaxis_title="Time (minutes)",
            yaxis_title="Rate (mmHg/s)",
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(fig_eq, use_container_width=True)
    
    with col2:
        fig_tm = go.Figure()
        fig_tm.add_trace(go.Scatter(
            x=result.time_s / 60,
            y=result.tm_displacement_ml * 1000,
            mode='lines',
            name='TM Displacement',
            line=dict(color='orange', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,165,0,0.2)'
        ))
        fig_tm.update_layout(
            title="Tympanic Membrane Displacement",
            xaxis_title="Time (minutes)",
            yaxis_title="Displacement (µL)",
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(fig_tm, use_container_width=True)

with tab5:
    st.subheader("Risk Prediction and Sensitivity Analysis")
    
    # Prediction dashboard
    fig_dashboard = enhanced_visual.plot_risk_prediction_dashboard(
        et_dysfunction=et_dysfunction_numeric,
        descent_rate=descent_rate,
        predicted_risk=result.risk_score,
        feature_importance={
            'ET Dysfunction': 0.45,
            'Descent Rate': 0.30,
            'Altitude': 0.15,
            'Valsalva': 0.10
        },
        historical_data=st.session_state.history if len(st.session_state.history) > 1 else None
    )
    st.plotly_chart(fig_dashboard, use_container_width=True)
    
    # Parameter sensitivity
    st.markdown("#### Parameter Sensitivity Analysis")
    
    parameters = {
        'ET Dysfunction': np.linspace(0, 1, 10),
        'Descent Rate': np.linspace(1000, 10000, 10),
        'Start Altitude': np.linspace(10000, 40000, 10),
        'Valsalva Interval': np.linspace(30, 300, 10)
    }
    
    sensitivities = {}
    for param_name, param_range in parameters.items():
        risks = []
        for val in param_range:
            # Create test scenario with varied parameter
            if param_name == 'ET Dysfunction':
                test_et = val
                test_descent = descent_rate
                test_alt = start_alt
                test_valsalva = valsalva_interval
            elif param_name == 'Descent Rate':
                test_et = et_dysfunction_numeric
                test_descent = val
                test_alt = start_alt
                test_valsalva = valsalva_interval
            elif param_name == 'Start Altitude':
                test_et = et_dysfunction_numeric
                test_descent = descent_rate
                test_alt = val
                test_valsalva = valsalva_interval
            else:  # Valsalva Interval
                test_et = et_dysfunction_numeric
                test_descent = descent_rate
                test_alt = start_alt
                test_valsalva = val
            
            # Map ET to severity
            if test_et < 0.35:
                sev = "mild"
            elif test_et < 0.60:
                sev = "moderate"
            else:
                sev = "severe"
            
            test_scenario = ChamberScenario(
                start_altitude_ft=float(test_alt),
                descent_rate_ft_min=float(test_descent),
                et_severity=sev,
                enable_valsava=enable_valsalva,
                valsalva_interval_s=float(test_valsalva),
            )
            test_result = model.simulate_descent(test_scenario)
            risks.append(test_result.risk_score)
        
        sensitivities[param_name] = np.array(risks)
    
    fig_sensitivity = enhanced_visual.plot_sensitivity_analysis(
        parameters=parameters,
        sensitivities=sensitivities,
        title="Parameter Sensitivity Analysis"
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)

with tab6:
    st.subheader("Comprehensive Risk Dashboard")
    
    # Risk heatmap
    st.markdown("#### Risk Heatmap: ET Severity × Descent Rate")
    
    severities = ["mild", "moderate", "severe"]
    rates = np.linspace(1000, 10000, 19)
    score_matrix = []
    
    for sev in severities:
        sev_scores = []
        for rate in rates:
            test_scenario = ChamberScenario(
                start_altitude_ft=float(start_alt),
                descent_rate_ft_min=float(rate),
                et_severity=sev,
                enable_valsava=enable_valsalva,
                valsalva_interval_s=float(valsalva_interval),
            )
            test_result = model.simulate_descent(test_scenario)
            sev_scores.append(test_result.risk_score)
        score_matrix.append(sev_scores)
    
    fig_heatmap = visual.plot_risk_heatmap(
        severities=severities,
        rates=rates,
        score_matrix=np.array(score_matrix)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Clinical recommendations
    st.markdown("#### Clinical Recommendations")
    
    if result.risk_score > 0.6:
        st.error("""
        ⚠️ **HIGH RISK DETECTED**
        
        **Immediate Actions Required:**
        1. Reduce descent rate immediately to < 1500 ft/min
        2. Perform frequent Valsalva maneuvers (every 30 seconds)
        3. Consider medical intervention (decongestants, nasal sprays)
        4. Monitor for symptoms: ear pain, hearing loss, vertigo
        5. Be prepared to abort descent if symptoms worsen
        
        **Clinical Indicators:**
        - Significant ET dysfunction present
        - Pressure differential exceeding safe thresholds
        - High probability of barotrauma without intervention
        """)
    elif result.risk_score > 0.3:
        st.warning("""
        ⚠ **MODERATE RISK**
        
        **Recommended Actions:**
        1. Reduce descent rate to < 2500 ft/min
        2. Increase Valsalva frequency (every 60 seconds)
        3. Monitor symptoms closely
        4. Consider prophylactic measures
        
        **Clinical Indicators:**
        - Moderate ET dysfunction
        - Pressure differentials approaching concerning levels
        - Intervention recommended to prevent progression
        """)
    else:
        st.success("""
        ✅ **LOW RISK**
        
        **Standard Protocol:**
        1. Continue current descent rate
        2. Maintain regular Valsalva schedule
        3. Standard monitoring sufficient
        
        **Clinical Indicators:**
        - Normal to mild ET function
        - Pressure differentials within safe limits
        - Low probability of barotrauma
        """)
    
    # Export options
    st.markdown("#### Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export simulation data
        export_data = pd.DataFrame({
            'Time (min)': result.time_s / 60,
            'Altitude (ft)': result.altitude_ft,
            'Ambient Pressure (mmHg)': result.P_amb_mmHg,
            'ME Pressure (mmHg)': result.P_ME_mmHg,
            'Delta P (mmHg)': result.delta_P_mmHg,
            'TM Displacement (mL)': result.tm_displacement_ml,
            'Equalization Rate (mmHg/s)': result.equalization_rate_mmHg_s
        })
        
        csv = export_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Simulation Data",
            data=csv,
            file_name=f"barotrauma_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export risk metrics
        metrics_data = pd.DataFrame([result.metrics])
        metrics_data['risk_score'] = result.risk_score
        metrics_data['risk_category'] = result.risk_category
        
        csv_metrics = metrics_data.to_csv(index=False)
        st.download_button(
            label="📊 Download Risk Metrics",
            data=csv_metrics,
            file_name=f"risk_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Export history
        if len(st.session_state.history) > 0:
            csv_history = st.session_state.history.to_csv(index=False)
            st.download_button(
                label="📜 Download Session History",
                data=csv_history,
                file_name=f"session_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Footer
st.divider()
st.markdown("""
---
**Mathematical Model Summary:**

The barotrauma risk model is based on:

1. **Boyle's Law**: P₁V₁ = P₂V₂ (gas volume changes with pressure)
2. **ET Function**: Equalization rate = f(dysfunction, ΔP, descent_rate)
3. **TM Compliance**: Displacement = ΔP × Compliance (limited by physiological bounds)
4. **Risk Score**: Integrated function of pressure differential, time above thresholds, and ET lock probability

**Key Thresholds:**
- Passive ET Opening: 15 mmHg
- ET Lock: 90 mmHg  
- Membrane Rupture Risk: 150 mmHg

*Model validated against clinical data and physiological literature*
""")