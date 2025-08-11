"""
Visualization Tools for Middle Ear Barotrauma Analysis
"""

import numpy as np
import matplotlib.pyplot as plt
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