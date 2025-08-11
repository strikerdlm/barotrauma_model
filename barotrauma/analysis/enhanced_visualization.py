"""
Enhanced Visualization Module for Barotrauma Risk Analysis

This module provides comprehensive visualization tools for analyzing the relationship
between barotrauma risk, ET dysfunction, and various flight/chamber parameters.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
from scipy.interpolate import griddata
from scipy import stats


class EnhancedBarotraumaVisualizer:
    """Enhanced visualization tools for comprehensive barotrauma analysis."""
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """Initialize visualizer with modern style."""
        try:
            plt.style.use(style)
        except:
            plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def plot_barotrauma_risk_vs_et_dysfunction(
        self,
        et_dysfunction_values: np.ndarray,
        risk_scores: np.ndarray,
        pressure_diffs: Optional[np.ndarray] = None,
        volume_changes: Optional[np.ndarray] = None,
        title: str = "Barotrauma Risk vs ET Dysfunction"
    ) -> go.Figure:
        """
        Create comprehensive plot of barotrauma risk vs ET dysfunction.
        
        Parameters:
        -----------
        et_dysfunction_values : np.ndarray
            ET dysfunction levels (0-1)
        risk_scores : np.ndarray
            Corresponding risk scores
        pressure_diffs : np.ndarray, optional
            Maximum pressure differences
        volume_changes : np.ndarray, optional
            Volume changes in mL
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Risk Score vs ET Dysfunction',
                'Pressure Difference vs ET Dysfunction',
                'Volume Change vs ET Dysfunction',
                'Risk Categories Distribution'
            ),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'scatter'}, {'type': 'bar'}]]
        )
        
        # Plot 1: Risk Score vs ET Dysfunction
        fig.add_trace(
            go.Scatter(
                x=et_dysfunction_values,
                y=risk_scores,
                mode='lines+markers',
                name='Risk Score',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(255,0,0,0.2)'
            ),
            row=1, col=1
        )
        
        # Add risk zones
        fig.add_hrect(y0=0, y1=0.3, fillcolor="green", opacity=0.1,
                     layer="below", line_width=0, row=1, col=1)
        fig.add_hrect(y0=0.3, y1=0.6, fillcolor="yellow", opacity=0.1,
                     layer="below", line_width=0, row=1, col=1)
        fig.add_hrect(y0=0.6, y1=1.0, fillcolor="red", opacity=0.1,
                     layer="below", line_width=0, row=1, col=1)
        
        # Plot 2: Pressure Difference
        if pressure_diffs is not None:
            fig.add_trace(
                go.Scatter(
                    x=et_dysfunction_values,
                    y=pressure_diffs,
                    mode='lines+markers',
                    name='Max ΔP',
                    line=dict(color='blue', width=2),
                    marker=dict(size=6)
                ),
                row=1, col=2
            )
            # Add clinical thresholds
            fig.add_hline(y=60, line_dash="dash", line_color="orange",
                         annotation_text="Discomfort", row=1, col=2)
            fig.add_hline(y=90, line_dash="dash", line_color="red",
                         annotation_text="ET Lock", row=1, col=2)
            fig.add_hline(y=150, line_dash="dot", line_color="darkred",
                         annotation_text="Rupture Risk", row=1, col=2)
        
        # Plot 3: Volume Change
        if volume_changes is not None:
            fig.add_trace(
                go.Scatter(
                    x=et_dysfunction_values,
                    y=volume_changes,
                    mode='lines+markers',
                    name='Volume Change',
                    line=dict(color='green', width=2),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            fig.add_hline(y=2.0, line_dash="dash", line_color="red",
                         annotation_text="Physiological Limit", row=2, col=1)
        
        # Plot 4: Risk Categories Distribution
        risk_categories = ['Low', 'Moderate', 'High']
        category_counts = [
            np.sum(risk_scores < 0.3),
            np.sum((risk_scores >= 0.3) & (risk_scores < 0.6)),
            np.sum(risk_scores >= 0.6)
        ]
        
        fig.add_trace(
            go.Bar(
                x=risk_categories,
                y=category_counts,
                marker_color=['green', 'yellow', 'red'],
                text=category_counts,
                textposition='auto'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_xaxes(title_text="ET Dysfunction Level", row=1, col=1)
        fig.update_xaxes(title_text="ET Dysfunction Level", row=1, col=2)
        fig.update_xaxes(title_text="ET Dysfunction Level", row=2, col=1)
        fig.update_xaxes(title_text="Risk Category", row=2, col=2)
        
        fig.update_yaxes(title_text="Risk Score", row=1, col=1)
        fig.update_yaxes(title_text="Pressure (mmHg)", row=1, col=2)
        fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=2)
        
        fig.update_layout(
            title_text=title,
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def plot_3d_risk_surface(
        self,
        et_dysfunction: np.ndarray,
        descent_rates: np.ndarray,
        risk_matrix: np.ndarray,
        title: str = "3D Risk Surface: ET Dysfunction × Descent Rate × Risk"
    ) -> go.Figure:
        """
        Create 3D surface plot of risk as function of ET dysfunction and descent rate.
        """
        fig = go.Figure(data=[
            go.Surface(
                x=et_dysfunction,
                y=descent_rates,
                z=risk_matrix,
                colorscale='RdYlGn_r',
                colorbar=dict(title="Risk Score"),
                contours={
                    "z": {"show": True, "usecolormap": True,
                          "highlightcolor": "limegreen", "project": {"z": True}}
                }
            )
        ])
        
        # Add threshold planes
        fig.add_trace(go.Surface(
            x=et_dysfunction,
            y=descent_rates,
            z=np.full_like(risk_matrix, 0.3),
            opacity=0.3,
            colorscale=[[0, 'yellow'], [1, 'yellow']],
            showscale=False,
            name='Moderate Risk Threshold'
        ))
        
        fig.add_trace(go.Surface(
            x=et_dysfunction,
            y=descent_rates,
            z=np.full_like(risk_matrix, 0.6),
            opacity=0.3,
            colorscale=[[0, 'red'], [1, 'red']],
            showscale=False,
            name='High Risk Threshold'
        ))
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='ET Dysfunction',
                yaxis_title='Descent Rate (ft/min)',
                zaxis_title='Risk Score',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
            ),
            height=700,
            template='plotly_white'
        )
        
        return fig
    
    def plot_3d_pressure_volume_risk(
        self,
        pressure_values: np.ndarray,
        volume_values: np.ndarray,
        risk_values: np.ndarray,
        et_dysfunction_levels: Optional[np.ndarray] = None,
        title: str = "3D Relationship: Pressure × Volume × Risk"
    ) -> go.Figure:
        """
        Create 3D scatter plot showing relationship between pressure, volume, and risk.
        """
        # Color by ET dysfunction if provided, otherwise by risk
        if et_dysfunction_levels is not None:
            color_values = et_dysfunction_levels
            colorbar_title = "ET Dysfunction"
            colorscale = 'Viridis'
        else:
            color_values = risk_values
            colorbar_title = "Risk Score"
            colorscale = 'RdYlGn_r'
        
        fig = go.Figure(data=[
            go.Scatter3d(
                x=pressure_values,
                y=volume_values,
                z=risk_values,
                mode='markers',
                marker=dict(
                    size=5,
                    color=color_values,
                    colorscale=colorscale,
                    showscale=True,
                    colorbar=dict(title=colorbar_title),
                    opacity=0.8
                ),
                text=[f'P: {p:.1f}<br>V: {v:.2f}<br>R: {r:.2f}' 
                      for p, v, r in zip(pressure_values, volume_values, risk_values)],
                hovertemplate='%{text}<extra></extra>'
            )
        ])
        
        # Add reference planes for risk thresholds
        xx, yy = np.meshgrid(
            np.linspace(pressure_values.min(), pressure_values.max(), 10),
            np.linspace(volume_values.min(), volume_values.max(), 10)
        )
        
        # Low risk plane
        fig.add_trace(go.Surface(
            x=xx, y=yy, z=np.full_like(xx, 0.3),
            opacity=0.2, colorscale=[[0, 'green'], [1, 'green']],
            showscale=False, name='Low Risk Boundary'
        ))
        
        # High risk plane
        fig.add_trace(go.Surface(
            x=xx, y=yy, z=np.full_like(xx, 0.6),
            opacity=0.2, colorscale=[[0, 'red'], [1, 'red']],
            showscale=False, name='High Risk Boundary'
        ))
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='Pressure Difference (mmHg)',
                yaxis_title='Volume Change (mL)',
                zaxis_title='Risk Score',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
            ),
            height=700,
            template='plotly_white'
        )
        
        return fig
    
    def plot_time_series_comparison(
        self,
        results_dict: Dict[str, Dict],
        title: str = "Time Series Comparison Across ET Dysfunction Levels"
    ) -> go.Figure:
        """
        Compare time series data across different ET dysfunction levels.
        
        Parameters:
        -----------
        results_dict : dict
            Dictionary with ET dysfunction levels as keys and simulation results as values
        """
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                'Pressure Difference Over Time',
                'Volume Change Over Time',
                'Equalization Rate Over Time'
            ),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        colors = px.colors.qualitative.Plotly
        
        for idx, (et_level, result) in enumerate(results_dict.items()):
            color = colors[idx % len(colors)]
            
            # Pressure difference
            if 'delta_P' in result and 'time' in result:
                fig.add_trace(
                    go.Scatter(
                        x=result['time'],
                        y=result['delta_P'],
                        mode='lines',
                        name=f'ET={et_level}',
                        line=dict(color=color, width=2),
                        legendgroup=et_level
                    ),
                    row=1, col=1
                )
            
            # Volume change
            if 'volume' in result and 'time' in result:
                fig.add_trace(
                    go.Scatter(
                        x=result['time'],
                        y=result['volume'] * 1000,  # Convert to mL
                        mode='lines',
                        name=f'ET={et_level}',
                        line=dict(color=color, width=2),
                        showlegend=False,
                        legendgroup=et_level
                    ),
                    row=2, col=1
                )
            
            # Equalization rate
            if 'eq_rate' in result and 'time' in result:
                fig.add_trace(
                    go.Scatter(
                        x=result['time'],
                        y=result['eq_rate'],
                        mode='lines',
                        name=f'ET={et_level}',
                        line=dict(color=color, width=2),
                        showlegend=False,
                        legendgroup=et_level
                    ),
                    row=3, col=1
                )
        
        # Add clinical thresholds
        fig.add_hline(y=90, line_dash="dash", line_color="red",
                     annotation_text="ET Lock", row=1, col=1)
        fig.add_hline(y=2.0, line_dash="dash", line_color="red",
                     annotation_text="Volume Limit", row=2, col=1)
        
        # Update axes
        fig.update_xaxes(title_text="Time (minutes)", row=3, col=1)
        fig.update_yaxes(title_text="ΔP (mmHg)", row=1, col=1)
        fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
        fig.update_yaxes(title_text="Rate (mmHg/s)", row=3, col=1)
        
        fig.update_layout(
            title_text=title,
            height=900,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_sensitivity_analysis(
        self,
        parameters: Dict[str, np.ndarray],
        sensitivities: Dict[str, np.ndarray],
        title: str = "Parameter Sensitivity Analysis"
    ) -> go.Figure:
        """
        Create tornado diagram for sensitivity analysis.
        """
        # Calculate sensitivity indices
        param_names = list(parameters.keys())
        sensitivity_values = []
        
        for param in param_names:
            if param in sensitivities:
                # Calculate range of effect
                effect_range = np.max(sensitivities[param]) - np.min(sensitivities[param])
                sensitivity_values.append(effect_range)
            else:
                sensitivity_values.append(0)
        
        # Sort by sensitivity
        sorted_indices = np.argsort(sensitivity_values)[::-1]
        sorted_params = [param_names[i] for i in sorted_indices]
        sorted_values = [sensitivity_values[i] for i in sorted_indices]
        
        # Create tornado diagram
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            y=sorted_params[:10],  # Top 10 most sensitive
            x=sorted_values[:10],
            orientation='h',
            marker=dict(
                color=sorted_values[:10],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sensitivity")
            ),
            text=[f'{v:.3f}' for v in sorted_values[:10]],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Risk Score Range",
            yaxis_title="Parameter",
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def plot_risk_prediction_dashboard(
        self,
        et_dysfunction: float,
        descent_rate: float,
        predicted_risk: float,
        feature_importance: Optional[Dict[str, float]] = None,
        historical_data: Optional[pd.DataFrame] = None
    ) -> go.Figure:
        """
        Create comprehensive dashboard for risk prediction display.
        """
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Current Risk Level',
                'Risk Factors',
                'Historical Comparison',
                'Safe Operating Envelope',
                'Feature Importance',
                'Recommendations'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'bar'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'bar'}, {'type': 'table'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # 1. Risk Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=predicted_risk,
                title={'text': "Risk Score"},
                delta={'reference': 0.3, 'increasing': {'color': "red"}},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 0.3], 'color': "lightgreen"},
                        {'range': [0.3, 0.6], 'color': "yellow"},
                        {'range': [0.6, 1], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.6
                    }
                }
            ),
            row=1, col=1
        )
        
        # 2. Risk Factors Bar
        factors = {
            'ET Dysfunction': et_dysfunction,
            'Descent Rate': min(descent_rate / 5000, 1),  # Normalize
            'Combined Risk': predicted_risk
        }
        
        fig.add_trace(
            go.Bar(
                x=list(factors.keys()),
                y=list(factors.values()),
                marker_color=['blue', 'green', 'red'],
                text=[f'{v:.2f}' for v in factors.values()],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 3. Historical Comparison (if data available)
        if historical_data is not None and not historical_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=historical_data.index,
                    y=historical_data['risk_score'],
                    mode='lines',
                    name='Historical',
                    line=dict(color='gray', width=1)
                ),
                row=1, col=3
            )
            fig.add_trace(
                go.Scatter(
                    x=[historical_data.index[-1]],
                    y=[predicted_risk],
                    mode='markers',
                    name='Current',
                    marker=dict(color='red', size=10)
                ),
                row=1, col=3
            )
        
        # 4. Safe Operating Envelope
        et_range = np.linspace(0, 1, 50)
        descent_range = np.linspace(1000, 10000, 50)
        
        # Create safety boundary
        safe_et = []
        safe_descent = []
        for et in et_range:
            # Simple model for safe descent rate given ET dysfunction
            safe_rate = 5000 * (1 - et) + 1000
            safe_et.append(et)
            safe_descent.append(safe_rate)
        
        fig.add_trace(
            go.Scatter(
                x=safe_et,
                y=safe_descent,
                mode='lines',
                name='Safe Boundary',
                line=dict(color='green', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,255,0,0.2)'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=[et_dysfunction],
                y=[descent_rate],
                mode='markers',
                name='Current',
                marker=dict(
                    color='red' if predicted_risk > 0.6 else 'yellow' if predicted_risk > 0.3 else 'green',
                    size=15,
                    symbol='star'
                )
            ),
            row=2, col=1
        )
        
        # 5. Feature Importance
        if feature_importance:
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            fig.add_trace(
                go.Bar(
                    x=[f[1] for f in sorted_features],
                    y=[f[0] for f in sorted_features],
                    orientation='h',
                    marker_color='purple'
                ),
                row=2, col=2
            )
        
        # 6. Recommendations Table
        recommendations = []
        if predicted_risk > 0.6:
            recommendations.append("⚠️ HIGH RISK - Reduce descent rate immediately")
            recommendations.append("⚠️ Consider medical intervention")
            recommendations.append("⚠️ Monitor for symptoms closely")
        elif predicted_risk > 0.3:
            recommendations.append("⚠ MODERATE RISK - Reduce descent rate")
            recommendations.append("⚠ Perform Valsalva maneuvers")
            recommendations.append("⚠ Monitor symptoms")
        else:
            recommendations.append("✓ LOW RISK - Continue current protocol")
            recommendations.append("✓ Maintain awareness")
            recommendations.append("✓ Regular monitoring sufficient")
        
        fig.add_trace(
            go.Table(
                cells=dict(
                    values=[recommendations],
                    align='left',
                    font=dict(size=11),
                    height=30
                )
            ),
            row=2, col=3
        )
        
        # Update layout
        fig.update_xaxes(title_text="Risk Factors", row=1, col=2)
        fig.update_xaxes(title_text="Time", row=1, col=3)
        fig.update_xaxes(title_text="ET Dysfunction", row=2, col=1)
        fig.update_xaxes(title_text="Importance", row=2, col=2)
        
        fig.update_yaxes(title_text="Value", row=1, col=2)
        fig.update_yaxes(title_text="Risk Score", row=1, col=3)
        fig.update_yaxes(title_text="Descent Rate (ft/min)", row=2, col=1)
        
        fig.update_layout(
            title_text=f"Barotrauma Risk Assessment Dashboard",
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def create_animation(
        self,
        time_series_data: Dict[str, np.ndarray],
        title: str = "Barotrauma Risk Evolution"
    ) -> go.Figure:
        """
        Create animated visualization of risk evolution over time.
        """
        # Prepare data for animation
        times = time_series_data['time']
        pressures = time_series_data.get('pressure', np.zeros_like(times))
        volumes = time_series_data.get('volume', np.zeros_like(times))
        risks = time_series_data.get('risk', np.zeros_like(times))
        
        # Create frames
        frames = []
        for i in range(0, len(times), max(1, len(times) // 100)):  # Sample 100 frames
            frame_data = go.Frame(
                data=[
                    go.Scatter(x=pressures[:i], y=risks[:i], mode='lines',
                              name='Risk vs Pressure'),
                    go.Scatter(x=[pressures[i]], y=[risks[i]], mode='markers',
                              marker=dict(size=15, color='red'))
                ],
                name=f'frame_{i}'
            )
            frames.append(frame_data)
        
        # Create initial figure
        fig = go.Figure(
            data=[
                go.Scatter(x=[pressures[0]], y=[risks[0]], mode='markers',
                          marker=dict(size=15, color='red'))
            ],
            frames=frames
        )
        
        # Add play/pause buttons
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(label="Play",
                             method="animate",
                             args=[None, {"frame": {"duration": 50, "redraw": True},
                                        "fromcurrent": True}]),
                        dict(label="Pause",
                             method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False},
                                          "mode": "immediate"}])
                    ]
                )
            ],
            title=title,
            xaxis_title="Pressure Difference (mmHg)",
            yaxis_title="Risk Score",
            template='plotly_white'
        )
        
        return fig