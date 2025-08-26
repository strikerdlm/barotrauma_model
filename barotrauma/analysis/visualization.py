"""
Visualization Tools for Middle Ear Barotrauma Analysis
"""

import numpy as np
# Make matplotlib optional
try:
	import matplotlib.pyplot as plt  # type: ignore
	from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
	plt = None  # type: ignore
import plotly.graph_objects as go
import io
import tempfile
import os
import warnings
# Make seaborn optional
try:
	import seaborn as sns  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	sns = None  # type: ignore
from typing import Dict, List, Optional
# Make pandas optional
try:
	import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	pd = None  # type: ignore

class BarotraumaVisualizer:
    """Visualization tools for barotrauma simulation results"""
    
    def __init__(self, style: str = 'seaborn'):
        """Initialize visualizer with style"""
        if plt is not None:
            try:
                plt.style.use(style)
            except Exception:
                pass
        
    def plot_pressure_dynamics(self, 
                             results: Dict[str, np.ndarray],
                             title: Optional[str] = None):
        """Plot pressure dynamics during flight"""
        if plt is None:
            warnings.warn('matplotlib not available; skip static plot generation')
            return None
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

    def plot_tm_surface(self, time: np.ndarray, altitude: np.ndarray,
                         tm_disp_ml: np.ndarray,
                         title: str = 'TM Displacement Surface (mL)'):
        """Interactive 3D surface of TM displacement."""
        T, A = np.meshgrid(time, altitude)
        Z = tm_disp_ml
        if Z.ndim == 1:
            Z = np.tile(Z, (len(altitude), 1))
        fig = go.Figure(data=go.Surface(z=Z, x=T, y=A, colorscale='Viridis'))
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='Time (min)',
                yaxis_title='Altitude (ft)',
                zaxis_title='TM displacement (mL)'
            ),
            template='plotly_white'
        )
        return fig

    def plot_risk_heatmap(self, severities: List[str], rates: np.ndarray,
                           score_matrix: np.ndarray,
                           title: str = 'Risk Heatmap (ET severity × descent rate)'):
        """Interactive heatmap of risk scores across severities and descent rates."""
        fig = go.Figure(
            data=go.Heatmap(
                z=score_matrix,
                x=rates,
                y=severities,
                colorscale='YlOrRd',
                zmin=0,
                zmax=1,
                colorbar=dict(title='Risk')
            )
        )
        fig.update_layout(
            title=title,
            xaxis_title='Descent rate (ft/min)',
            yaxis_title='ET severity',
            template='plotly_white'
        )
        return fig

    # ---------- Optional backends: Matplotlib 3D, PyVista, Mayavi ---------- #
    def plot_3d_surface_matplotlib(self, time: np.ndarray, altitude: np.ndarray,
                                   delta_p: np.ndarray,
                                   title: str = 'ΔP Surface (Matplotlib 3D)'):
        """Static 3D surface using Matplotlib's mplot3d."""
        if plt is None:
            warnings.warn('matplotlib not available; skip static 3D surface plot')
            return None
        T, A = np.meshgrid(time, altitude)
        Z = delta_p
        if Z.ndim == 1:
            Z = np.tile(Z, (len(altitude), 1))

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(T, A, Z, cmap='viridis', linewidth=0, antialiased=True)
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Altitude (ft)')
        ax.set_zlabel('ΔP (mmHg)')
        ax.set_title(title)
        fig.colorbar(surf, shrink=0.5, aspect=10)
        fig.tight_layout()
        return fig

    def plot_3d_surface_pyvista(self, time: np.ndarray, altitude: np.ndarray,
                                 delta_p: np.ndarray,
                                 screenshot_path: str | None = None):
        """3D surface using PyVista. Returns screenshot path or bytes.

        Notes: In web apps like Streamlit, interactive VTK windows are not
        supported out-of-the-box. We render a high-res screenshot instead.
        """
        try:
            import pyvista as pv
        except Exception as e:
            warnings.warn(
                'PyVista not available. Install with `pip install pyvista vtk`.'
            )
            raise

        T, A = np.meshgrid(time, altitude)
        Z = delta_p
        if Z.ndim == 1:
            Z = np.tile(Z, (len(altitude), 1))

        grid = pv.StructuredGrid(T, A, Z)
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(grid, cmap='viridis', smooth_shading=True)
        plotter.set_background('white')

        if screenshot_path is None:
            tmpdir = tempfile.mkdtemp(prefix='pyvista_')
            screenshot_path = os.path.join(tmpdir, 'pyvista_surface.png')
        plotter.show(screenshot=screenshot_path, auto_close=True)
        return screenshot_path

    def plot_3d_surface_mayavi(self, time: np.ndarray, altitude: np.ndarray,
                               delta_p: np.ndarray,
                               screenshot_path: str | None = None):
        """3D surface using Mayavi (screenshot output)."""
        try:
            from mayavi import mlab
        except Exception:
            warnings.warn(
                'Mayavi not available. Install with `pip install mayavi` or conda-forge.'
            )
            raise

        T, A = np.meshgrid(time, altitude)
        Z = delta_p
        if Z.ndim == 1:
            Z = np.tile(Z, (len(altitude), 1))

        mlab.figure(size=(800, 600), bgcolor=(1, 1, 1))
        surf = mlab.surf(T, A, Z, colormap='viridis')
        mlab.axes(xlabel='Time (min)', ylabel='Altitude (ft)', zlabel='ΔP (mmHg)')
        if screenshot_path is None:
            tmpdir = tempfile.mkdtemp(prefix='mayavi_')
            screenshot_path = os.path.join(tmpdir, 'mayavi_surface.png')
        mlab.savefig(screenshot_path)
        mlab.close(all=True)
        return screenshot_path

    def plot_risk_analysis(self, df: pd.DataFrame):
        """Plot risk analysis from database"""
        if sns is None:
            warnings.warn('seaborn not available; skip risk analysis plot')
            return None
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
        if sns is None:
            warnings.warn('seaborn not available; skip statistical summary plot')
            return None
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