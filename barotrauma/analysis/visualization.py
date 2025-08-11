"""
Visualization Tools for Middle Ear Barotrauma Analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import plotly.graph_objects as go
import seaborn as sns
from typing import Dict, List, Optional
import pandas as pd

class BarotraumaVisualizer:
    """Visualization tools for barotrauma simulation results"""
    
    def __init__(self, style: str = 'seaborn'):
        """Initialize visualizer with style"""
        plt.style.use(style)
        
    def plot_pressure_dynamics(self, 
                             results: Dict[str, np.ndarray],
                             title: Optional[str] = None):
        """Plot pressure dynamics during flight"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Pressure differentials
        ax1.plot(results['time'], results['P_ME'], label='Middle Ear')
        ax1.plot(results['time'], results['P_cabin'], label='Cabin')
        ax1.set_xlabel('Time (min)')
        ax1.set_ylabel('Pressure (mmH2O)')
        ax1.set_title(title or 'Pressure Dynamics')
        ax1.legend()
        ax1.grid(True)
        
        # Pressure gradient
        ax2.plot(results['time'], results['dP'])
        ax2.axhline(y=250, color='r', linestyle='--', label='Barotitis Threshold')
        ax2.axhline(y=1300, color='r', linestyle=':', label='Baromyringitis Threshold')
        ax2.set_xlabel('Time (min)')
        ax2.set_ylabel('ΔP_ME-cabin (mmH2O)')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        return fig
    
    def plot_3d_pressure_surface(self, time: np.ndarray, altitude: np.ndarray,
                                 delta_p: np.ndarray, title: str =
                                 "ΔP Surface (Time vs Altitude)"):
        """Interactive 3D surface of ΔP(time, altitude) using Plotly."""
        # Ensure proper grid
        T, A = np.meshgrid(time, altitude)
        Z = delta_p
        if Z.ndim == 1:
            # Attempt to reshape if provided as vector for each time
            Z = np.tile(Z, (len(altitude), 1))

        fig = go.Figure(data=go.Surface(z=Z, x=T, y=A, colorscale='Viridis'))
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='Time (min)',
                yaxis_title='Altitude (ft)',
                zaxis_title='ΔP (mmHg)'
            ),
            autosize=True,
            template='plotly_white'
        )
        return fig

    def plot_3d_equalization_field(self, time: np.ndarray, eq_rate: np.ndarray,
                                   delta_p: np.ndarray,
                                   title: str = '3D Equalization Field'):
        """3D scatter of equalization speed vs time vs ΔP."""
        fig = go.Figure(
            data=go.Scatter3d(
                x=time,
                y=delta_p,
                z=eq_rate,
                mode='markers',
                marker=dict(
                    size=3,
                    color=np.abs(delta_p),
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title='|ΔP|')
                )
            )
        )
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='Time (s)',
                yaxis_title='ΔP (mmHg)',
                zaxis_title='Equalization speed (mmHg/s)'
            ),
            template='plotly_white'
        )
        return fig

    def plot_risk_analysis(self, df: pd.DataFrame):
        """Plot risk analysis from database"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Risk distribution
        sns.histplot(data=df, x='barotitis_risk', ax=ax1)
        ax1.set_title('Barotitis Risk Distribution')
        
        sns.histplot(data=df, x='baromyringitis_risk', ax=ax2)
        ax2.set_title('Baromyringitis Risk Distribution')
        
        # Risk by condition
        sns.boxplot(data=df, x='condition', y='barotitis_risk', ax=ax3)
        ax3.set_title('Barotitis Risk by Condition')
        ax3.tick_params(axis='x', rotation=45)
        
        # Time series of pressure gradients
        sns.lineplot(data=df, x='time', y='pressure_gradient', 
                    hue='condition', ax=ax4)
        ax4.set_title('Pressure Gradient Evolution')
        
        plt.tight_layout()
        return fig
    
    def plot_statistical_summary(self, df: pd.DataFrame):
        """Plot statistical summary of results"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Risk correlation matrix
        risk_cols = ['barotitis_risk', 'baromyringitis_risk', 
                    'max_pressure_gradient', 'et_locked_duration']
        corr = df[risk_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax1)
        ax1.set_title('Risk Correlation Matrix')
        
        # Risk factors analysis
        sns.barplot(data=df, x='condition', y='risk_score', ax=ax2)
        ax2.set_title('Risk Score by Condition')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig 