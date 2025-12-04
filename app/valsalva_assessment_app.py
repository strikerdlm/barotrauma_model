"""
Valsalva Maneuver Assessment App for Barotrauma Risk Prediction.

This Streamlit application provides a clinical interface for:
1. Analyzing Valsalva maneuver videos from endoscopy
2. Predicting middle ear barotrauma risk
3. Generating clinical recommendations for hypobaric chamber exposure
4. Managing control data for model calibration

Author: Aerospace Medicine Research
License: MIT

Usage:
    streamlit run app/valsalva_assessment_app.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from barotrauma.models.valsalva_video_analysis import (
    TMMovementFeatures,
    BilateralValsalvaResult,
    ValsalvaQualityGrade,
    TMMovementExtractor,
    ValsalvaRiskPredictor,
    generate_clinical_report,
)
from barotrauma.models.valsalva_chamber_integration import (
    IntegratedBarotraumaAssessment,
    IntegratedRiskAssessment,
    quick_assess,
)
from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
)


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Valsalva Assessment - Barotrauma Risk",
    page_icon="🦻",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# Styling
# ============================================================================

st.markdown("""
<style>
    .risk-low { color: #28a745; font-weight: bold; }
    .risk-moderate { color: #ffc107; font-weight: bold; }
    .risk-high { color: #dc3545; font-weight: bold; }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
    .stAlert { margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State Initialization
# ============================================================================

if 'assessment_system' not in st.session_state:
    st.session_state.assessment_system = IntegratedBarotraumaAssessment()

if 'current_assessment' not in st.session_state:
    st.session_state.current_assessment = None

if 'controls_database' not in st.session_state:
    st.session_state.controls_database = []


# ============================================================================
# Helper Functions
# ============================================================================

def create_risk_gauge(risk_score: float, title: str = "Risk Score") -> go.Figure:
    """Create a gauge chart for risk visualization."""
    # Determine color based on risk
    if risk_score < 0.3:
        color = "green"
    elif risk_score < 0.6:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18}},
        number={'suffix': '%', 'font': {'size': 30}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(40, 167, 69, 0.3)'},
                {'range': [30, 60], 'color': 'rgba(255, 193, 7, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(220, 53, 69, 0.3)'},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score * 100,
            },
        },
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    return fig


def create_bilateral_comparison(
    left_features: TMMovementFeatures,
    right_features: TMMovementFeatures,
) -> go.Figure:
    """Create bilateral ear comparison chart."""
    categories = [
        'Max Displacement',
        'Movement Smoothness',
        'Completeness',
        'Response Speed',
    ]
    
    # Normalize latency to 0-1 (lower latency = better)
    left_speed = max(0, 1 - left_features.response_latency / 2.0)
    right_speed = max(0, 1 - right_features.response_latency / 2.0)
    
    left_values = [
        left_features.max_displacement,
        left_features.movement_smoothness,
        left_features.movement_completeness,
        left_speed,
    ]
    
    right_values = [
        right_features.max_displacement,
        right_features.movement_smoothness,
        right_features.movement_completeness,
        right_speed,
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=left_values + [left_values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        name='Left Ear',
        line_color='blue',
        fillcolor='rgba(0, 0, 255, 0.2)',
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=right_values + [right_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Right Ear',
        line_color='red',
        fillcolor='rgba(255, 0, 0, 0.2)',
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
        ),
        showlegend=True,
        title="Bilateral Ear Comparison",
        height=400,
    )
    
    return fig


def simulate_displacement_signal(
    max_displacement: float,
    latency: float,
    smoothness: float,
    duration: float = 5.0,
    fps: float = 30.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Simulate a displacement signal for visualization."""
    n_samples = int(duration * fps)
    t = np.linspace(0, duration, n_samples)
    
    # Create sigmoid-like displacement pattern
    latency_idx = int(latency * fps)
    peak_time = latency + 0.5 + (1 - smoothness) * 0.5
    
    signal = np.zeros(n_samples)
    for i in range(n_samples):
        if t[i] < latency:
            signal[i] = 0
        elif t[i] < peak_time:
            progress = (t[i] - latency) / (peak_time - latency)
            signal[i] = max_displacement * (1 - np.exp(-5 * progress))
        else:
            decay_rate = 2.0 * smoothness
            signal[i] = max_displacement * np.exp(-decay_rate * (t[i] - peak_time))
    
    # Add noise based on smoothness
    noise = (1 - smoothness) * 0.1 * np.random.randn(n_samples)
    signal = signal + noise
    signal = np.clip(signal, 0, 1)
    
    return t, signal


# ============================================================================
# Main App Layout
# ============================================================================

def main() -> None:
    """Main application entry point."""
    st.title("🦻 Valsalva Maneuver Assessment")
    st.markdown("""
    **Barotrauma Risk Prediction for Hypobaric Chamber Operations**
    
    This system analyzes Valsalva maneuver quality to predict middle ear barotrauma risk
    during hypobaric chamber training.
    """)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Assessment", "Simulation", "Control Database", "About"],
    )
    
    if page == "Assessment":
        assessment_page()
    elif page == "Simulation":
        simulation_page()
    elif page == "Control Database":
        control_database_page()
    else:
        about_page()


def assessment_page() -> None:
    """Main assessment page."""
    st.header("Patient Assessment")
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "Video Upload (Coming Soon)"],
        horizontal=True,
    )
    
    if input_method == "Video Upload (Coming Soon)":
        st.info("🎥 Video upload functionality will be available in a future release. "
                "Please use manual entry for now.")
        input_method = "Manual Entry"
    
    # Manual entry form
    with st.form("assessment_form"):
        st.subheader("Patient Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            patient_id = st.text_input("Patient ID", value="P001")
        with col2:
            age = st.number_input("Age", min_value=18, max_value=80, value=35)
        with col3:
            assessment_date = st.date_input("Assessment Date")
        
        # Clinical history
        st.subheader("Clinical History")
        col1, col2 = st.columns(2)
        
        with col1:
            previous_barotrauma = st.checkbox("Previous Barotrauma")
            chronic_et_dysfunction = st.checkbox("Chronic ET Dysfunction")
        with col2:
            current_uri = st.checkbox("Current Upper Respiratory Infection")
            recent_flight_problems = st.checkbox("Recent Flight Ear Problems")
        
        # Valsalva measurements
        st.subheader("Valsalva Measurements")
        st.markdown("*Enter observed TM movement quality (0 = no movement, 1 = excellent movement)*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Left Ear**")
            left_displacement = st.slider(
                "Max Displacement (L)",
                0.0, 1.0, 0.7,
                key="left_disp",
            )
            left_latency = st.slider(
                "Response Latency (L) - seconds",
                0.1, 3.0, 0.5,
                key="left_lat",
            )
            left_smoothness = st.slider(
                "Movement Smoothness (L)",
                0.0, 1.0, 0.75,
                key="left_smooth",
            )
        
        with col2:
            st.markdown("**Right Ear**")
            right_displacement = st.slider(
                "Max Displacement (R)",
                0.0, 1.0, 0.65,
                key="right_disp",
            )
            right_latency = st.slider(
                "Response Latency (R) - seconds",
                0.1, 3.0, 0.6,
                key="right_lat",
            )
            right_smoothness = st.slider(
                "Movement Smoothness (R)",
                0.0, 1.0, 0.70,
                key="right_smooth",
            )
        
        submitted = st.form_submit_button("Run Assessment", type="primary")
    
    if submitted:
        # Create feature objects
        left_features = TMMovementFeatures(
            max_displacement=left_displacement,
            mean_displacement=left_displacement * 0.6,
            displacement_velocity=left_displacement / (left_latency + 0.5),
            response_latency=left_latency,
            movement_smoothness=left_smoothness,
            movement_completeness=left_smoothness * 0.9,
            measurement_confidence=0.85,
        )
        
        right_features = TMMovementFeatures(
            max_displacement=right_displacement,
            mean_displacement=right_displacement * 0.6,
            displacement_velocity=right_displacement / (right_latency + 0.5),
            response_latency=right_latency,
            movement_smoothness=right_smoothness,
            movement_completeness=right_smoothness * 0.9,
            measurement_confidence=0.85,
        )
        
        # Create bilateral result
        valsalva_result = BilateralValsalvaResult(
            left_ear=left_features,
            right_ear=right_features,
        )
        
        # Clinical history
        clinical_history = {
            'age': age,
            'previous_barotrauma': previous_barotrauma,
            'chronic_et_dysfunction': chronic_et_dysfunction,
            'current_uri': current_uri,
            'recent_flight_problems': recent_flight_problems,
        }
        
        # Run assessment
        with st.spinner("Running integrated assessment..."):
            assessment = st.session_state.assessment_system.assess_from_valsalva(
                valsalva_result=valsalva_result,
                patient_id=patient_id,
                clinical_history=clinical_history,
            )
            st.session_state.current_assessment = assessment
        
        # Display results
        display_assessment_results(assessment, valsalva_result)


def display_assessment_results(
    assessment: IntegratedRiskAssessment,
    valsalva_result: BilateralValsalvaResult,
) -> None:
    """Display assessment results."""
    st.markdown("---")
    st.header("Assessment Results")
    
    # Risk overview
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.plotly_chart(
            create_risk_gauge(assessment.final_risk_score, "Overall Risk"),
            use_container_width=True,
        )
    
    with col2:
        st.plotly_chart(
            create_risk_gauge(assessment.simulated_risk_score, "Simulated Risk"),
            use_container_width=True,
        )
    
    with col3:
        st.plotly_chart(
            create_risk_gauge(
                assessment.ml_risk_probability if assessment.ml_risk_probability > 0 else 0.5,
                "ML Prediction"
            ),
            use_container_width=True,
        )
    
    # Risk category display
    risk_category = assessment.final_risk_category
    if "Low" in risk_category:
        st.success(f"🟢 **Risk Category: {risk_category}**")
    elif "Moderate" in risk_category:
        st.warning(f"🟡 **Risk Category: {risk_category}**")
    else:
        st.error(f"🔴 **Risk Category: {risk_category}**")
    
    # Bilateral comparison
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(
            create_bilateral_comparison(
                assessment.valsalva_result.left_ear,
                assessment.valsalva_result.right_ear,
            ),
            use_container_width=True,
        )
    
    with col2:
        st.subheader("Valsalva Quality Grades")
        st.markdown(f"""
        | Ear | Grade | Displacement |
        |-----|-------|--------------|
        | Left | **{assessment.valsalva_result.left_grade.name}** | {assessment.valsalva_result.left_ear.max_displacement:.2f} |
        | Right | **{assessment.valsalva_result.right_grade.name}** | {assessment.valsalva_result.right_ear.max_displacement:.2f} |
        | **Overall** | **{assessment.valsalva_quality_grade}** | - |
        
        **Asymmetry Score:** {assessment.valsalva_result.asymmetry_score:.2f}
        """)
    
    # Simulated displacement signals
    st.subheader("Simulated TM Movement Patterns")
    
    t_left, signal_left = simulate_displacement_signal(
        assessment.valsalva_result.left_ear.max_displacement,
        assessment.valsalva_result.left_ear.response_latency,
        assessment.valsalva_result.left_ear.movement_smoothness,
    )
    t_right, signal_right = simulate_displacement_signal(
        assessment.valsalva_result.right_ear.max_displacement,
        assessment.valsalva_result.right_ear.response_latency,
        assessment.valsalva_result.right_ear.movement_smoothness,
    )
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Left Ear", "Right Ear"))
    
    fig.add_trace(
        go.Scatter(x=t_left, y=signal_left, name="Left", line=dict(color="blue")),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_right, y=signal_right, name="Right", line=dict(color="red")),
        row=1, col=2,
    )
    
    fig.update_layout(height=300, showlegend=False)
    fig.update_xaxes(title_text="Time (s)")
    fig.update_yaxes(title_text="Displacement", range=[0, 1])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("📋 Recommendations")
    for rec in assessment.recommendations:
        st.markdown(f"- {rec}")
    
    # Contraindications
    if assessment.contraindications:
        st.subheader("⚠️ Contraindications")
        for contra in assessment.contraindications:
            st.error(contra)
    
    # Operational parameters
    st.subheader("🛡️ Safe Operational Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Max Descent Rate",
            f"{assessment.recommended_max_descent_rate:.0f} ft/min",
        )
    with col2:
        st.metric(
            "Valsalva Interval",
            f"{assessment.recommended_valsalva_interval:.0f} sec",
        )
    with col3:
        st.metric(
            "Enhanced Monitoring",
            "Required" if assessment.requires_enhanced_monitoring else "Standard",
        )
    
    # Clinical report download
    st.subheader("📄 Clinical Report")
    
    # Generate report from valsalva result
    from barotrauma.models.valsalva_video_analysis import PatientValsalvaProfile
    
    profile = PatientValsalvaProfile(
        patient_id=assessment.patient_id,
        assessment_date=assessment.assessment_date,
        valsalva_result=assessment.valsalva_result,
    )
    
    report = generate_clinical_report(profile)
    
    with st.expander("View Full Report"):
        st.text(report)
    
    st.download_button(
        label="Download Report",
        data=report,
        file_name=f"valsalva_report_{assessment.patient_id}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
    )


def simulation_page() -> None:
    """Chamber simulation page."""
    st.header("Hypobaric Chamber Simulation")
    
    st.markdown("""
    Simulate pressure dynamics and risk during hypobaric chamber descent.
    Use the current assessment parameters or customize the scenario.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scenario Parameters")
        start_altitude = st.slider(
            "Starting Altitude (ft)",
            10000, 40000, 25000, 1000,
        )
        descent_rate = st.slider(
            "Descent Rate (ft/min)",
            1000, 10000, 3000, 500,
        )
        
        et_severity = st.selectbox(
            "ET Dysfunction Severity",
            ["mild", "moderate", "severe"],
            index=1,
        )
        
        enable_valsalva = st.checkbox("Enable Valsalva", value=True)
        if enable_valsalva:
            valsalva_interval = st.slider(
                "Valsalva Interval (seconds)",
                30, 180, 120, 15,
            )
        else:
            valsalva_interval = 120
    
    with col2:
        # Run simulation
        if st.button("Run Simulation", type="primary"):
            scenario = ChamberScenario(
                start_altitude_ft=float(start_altitude),
                descent_rate_ft_min=float(descent_rate),
                et_severity=et_severity,
                enable_valsava=enable_valsalva,
                valsalva_interval_s=float(valsalva_interval),
            )
            
            model = HypobaricChamberRiskModel()
            result = model.simulate_descent(scenario)
            
            # Display results
            st.metric("Risk Score", f"{result.risk_score:.2f}")
            st.metric("Risk Category", result.risk_category)
            st.metric("Max |ΔP|", f"{max(abs(result.delta_P_mmHg)):.1f} mmHg")
            
            # Plot results
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                subplot_titles=("Altitude", "Pressure Differential", "TM Displacement"),
                vertical_spacing=0.08,
            )
            
            # Altitude
            fig.add_trace(
                go.Scatter(
                    x=result.time_s / 60,
                    y=result.altitude_ft,
                    name="Altitude",
                    line=dict(color="blue"),
                ),
                row=1, col=1,
            )
            
            # Pressure differential
            fig.add_trace(
                go.Scatter(
                    x=result.time_s / 60,
                    y=result.delta_P_mmHg,
                    name="ΔP",
                    line=dict(color="red"),
                ),
                row=2, col=1,
            )
            
            # Add thresholds
            fig.add_hline(y=-90, line_dash="dash", line_color="orange",
                         annotation_text="ET Lock", row=2, col=1)
            fig.add_hline(y=-150, line_dash="dash", line_color="red",
                         annotation_text="TM Rupture", row=2, col=1)
            
            # TM displacement
            fig.add_trace(
                go.Scatter(
                    x=result.time_s / 60,
                    y=result.tm_displacement_ml,
                    name="TM Disp",
                    line=dict(color="green"),
                ),
                row=3, col=1,
            )
            
            fig.update_layout(height=600, showlegend=False)
            fig.update_xaxes(title_text="Time (min)", row=3)
            fig.update_yaxes(title_text="Altitude (ft)", row=1)
            fig.update_yaxes(title_text="ΔP (mmHg)", row=2)
            fig.update_yaxes(title_text="Displacement (mL)", row=3)
            
            st.plotly_chart(fig, use_container_width=True)


def control_database_page() -> None:
    """Control database management page."""
    st.header("Control Database Management")
    
    st.markdown("""
    Record known outcomes from hypobaric chamber exposures to improve model predictions.
    Controls with known outcomes help calibrate the risk prediction model.
    """)
    
    # Add control outcome
    st.subheader("Add Control Outcome")
    
    if st.session_state.current_assessment is not None:
        st.info(f"Current assessment: {st.session_state.current_assessment.patient_id}")
        
        outcome = st.selectbox(
            "Actual Outcome",
            ["no_barotrauma", "mild", "moderate", "severe"],
        )
        
        notes = st.text_area("Notes (optional)")
        
        if st.button("Record Outcome"):
            control = {
                'patient_id': st.session_state.current_assessment.patient_id,
                'assessment': st.session_state.current_assessment.to_dict(),
                'outcome': outcome,
                'notes': notes,
                'recorded_at': datetime.now().isoformat(),
            }
            st.session_state.controls_database.append(control)
            
            # Add to assessment system
            st.session_state.assessment_system.add_control_outcome(
                st.session_state.current_assessment,
                outcome,
            )
            
            st.success(f"Recorded outcome: {outcome}")
    else:
        st.warning("No current assessment. Run an assessment first.")
    
    # Display database
    st.subheader("Recorded Controls")
    
    if st.session_state.controls_database:
        for i, control in enumerate(st.session_state.controls_database):
            with st.expander(f"Control {i+1}: {control['patient_id']} - {control['outcome']}"):
                st.json(control)
    else:
        st.info("No controls recorded yet.")
    
    # Train model
    st.subheader("Model Training")
    
    n_controls = len(st.session_state.controls_database)
    st.metric("Total Controls", n_controls)
    
    if n_controls >= 10:
        if st.button("Train ML Model"):
            with st.spinner("Training model..."):
                success = st.session_state.assessment_system.train_ml_model(
                    min_controls=10
                )
            
            if success:
                st.success("Model trained successfully!")
            else:
                st.error("Training failed. Need more diverse outcomes.")
    else:
        st.info(f"Need at least 10 controls for training. Current: {n_controls}")


def about_page() -> None:
    """About page with documentation."""
    st.header("About This System")
    
    st.markdown("""
    ## Valsalva Maneuver Assessment for Barotrauma Risk
    
    This clinical decision support system helps predict middle ear barotrauma risk
    during hypobaric chamber training by analyzing the quality of Valsalva maneuvers.
    
    ### Scientific Background
    
    The **Valsalva maneuver** is the primary technique for equalizing middle ear pressure
    during descent. By analyzing tympanic membrane (TM) movement during Valsalva:
    
    - **Good movement** → Effective Eustachian tube function → Lower risk
    - **Poor movement** → ET dysfunction → Higher barotrauma risk
    
    ### How It Works
    
    1. **Video Analysis**: Endoscopic video of Valsalva maneuver is analyzed
    2. **Feature Extraction**: TM displacement, latency, and quality metrics extracted
    3. **Risk Prediction**: Combined physics-based simulation and ML prediction
    4. **Recommendations**: Clinical recommendations for safe chamber operation
    
    ### Key Features
    
    - **Bilateral Assessment**: Analyzes both ears for asymmetry detection
    - **Physics-Based Simulation**: Uses validated chamber pressure models
    - **ML Enhancement**: Learns from control outcomes for improved accuracy
    - **Clinical Integration**: Generates actionable recommendations
    
    ### References
    
    - Kanick & Doyle (2005): Barotrauma during air travel - mathematical model
    - Bayoumy et al. (2021): Management of tympanic membrane retractions
    - Ryan et al. (2018): Prevention of otic barotrauma in aviation
    
    ### Contact
    
    For questions or feedback, contact the Aerospace Medicine Research team.
    """)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
