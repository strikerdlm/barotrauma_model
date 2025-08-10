"""
Database Management for Barotrauma Simulation Results
"""

import sqlite3
import pandas as pd
from typing import Dict, List
import numpy as np
from datetime import datetime

class BarotraumaDB:
    """Database manager for barotrauma simulation results"""
    
    def __init__(self, db_path: str = 'barotrauma_results.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create simulations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    condition TEXT,
                    flight_profile TEXT,
                    barotitis_risk REAL,
                    baromyringitis_risk REAL,
                    max_pressure_gradient REAL,
                    et_locked_duration REAL,
                    risk_score REAL
                )
            ''')
            
            # Create time series table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_series (
                    simulation_id INTEGER,
                    time REAL,
                    P_ME REAL,
                    P_cabin REAL,
                    pressure_gradient REAL,
                    et_locked INTEGER,
                    FOREIGN KEY(simulation_id) REFERENCES simulations(id)
                )
            ''')
            
            conn.commit()
    
    def store_results(self, 
                     results: Dict[str, np.ndarray],
                     condition: str,
                     flight_profile: str):
        """Store simulation results in database"""
        with sqlite3.connect(self.db_path) as conn:
            # Calculate risk metrics
            barotitis_risk = np.mean(results['barotitis'])
            baromyringitis_risk = np.mean(results['baromyringitis'])
            max_gradient = np.max(np.abs(results['dP']))
            et_locked_duration = np.mean(results['ET_locked'])
            risk_score = self._calculate_risk_score(results)
            
            # Insert simulation record
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO simulations 
                (timestamp, condition, flight_profile, barotitis_risk,
                 baromyringitis_risk, max_pressure_gradient,
                 et_locked_duration, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), condition, flight_profile,
                  barotitis_risk, baromyringitis_risk,
                  max_gradient, et_locked_duration, risk_score))
            
            simulation_id = cursor.lastrowid
            
            # Insert time series data
            time_series_data = [
                (simulation_id, t, pm, pc, dp, et)
                for t, pm, pc, dp, et in zip(
                    results['time'],
                    results['P_ME'],
                    results['P_cabin'],
                    results['dP'],
                    results['ET_locked']
                )
            ]
            
            cursor.executemany('''
                INSERT INTO time_series
                (simulation_id, time, P_ME, P_cabin, 
                 pressure_gradient, et_locked)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', time_series_data)
            
            conn.commit()
    
    def get_results_df(self) -> pd.DataFrame:
        """Get results as pandas DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            # Get simulations data
            df_sim = pd.read_sql_query('''
                SELECT * FROM simulations
            ''', conn)
            
            # Get time series data
            df_ts = pd.read_sql_query('''
                SELECT * FROM time_series
            ''', conn)
            
            # Merge data
            df = pd.merge(df_sim, df_ts, 
                         left_on='id', 
                         right_on='simulation_id')
            
            return df
    
    def _calculate_risk_score(self, results: Dict[str, np.ndarray]) -> float:
        """Calculate overall risk score"""
        barotitis_weight = 0.4
        baromyringitis_weight = 0.6
        
        barotitis_risk = np.mean(results['barotitis'])
        baromyringitis_risk = np.mean(results['baromyringitis'])
        
        return (barotitis_weight * barotitis_risk + 
                baromyringitis_weight * baromyringitis_risk) 