"""
Enhanced analysis module with error handling
"""

from core.exceptions import AnalysisError, DatabaseError
import logging

logger = logging.getLogger(__name__)

class BarotraumaAnalyzer:
    """Analysis tools with error handling"""
    
    def analyze_simulation(self, results, condition, flight_profile):
        """Analyze simulation results with validation"""
        try:
            # Validate inputs
            self._validate_results(results)
            
            logger.info(f"Analyzing simulation for condition: {condition}")
            
            # Store results
            try:
                self.db.store_results(results, condition, flight_profile)
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                raise DatabaseError(f"Failed to store results: {str(e)}")
            
            # Generate visualizations
            try:
                fig_dynamics = self.visualizer.plot_pressure_dynamics(
                    results,
                    title=f'Pressure Dynamics - {condition}'
                )
            except Exception as e:
                logger.error(f"Visualization error: {str(e)}")
                raise AnalysisError(f"Failed to generate visualizations: {str(e)}")
            
            # Calculate metrics
            try:
                metrics = self._calculate_metrics(results)
            except Exception as e:
                logger.error(f"Metrics calculation error: {str(e)}")
                raise AnalysisError(f"Failed to calculate metrics: {str(e)}")
            
            return {
                'figures': {'dynamics': fig_dynamics},
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise AnalysisError(f"Analysis failed: {str(e)}")
    
    def _validate_results(self, results):
        """Validate simulation results"""
        required_keys = ['time', 'P_ME', 'P_cabin', 'dP', 'ET_locked', 
                        'barotitis', 'baromyringitis']
        
        for key in required_keys:
            if key not in results:
                raise AnalysisError(f"Missing required result key: {key}")
            
        if len(results['time']) == 0:
            raise AnalysisError("Empty results array")
    
    def analyze_multiple_conditions(self, 
                                  results_dict: Dict[str, Dict[str, np.ndarray]],
                                  flight_profile: str):
        """Analyze results from multiple conditions"""
        # Store all results
        for condition, results in results_dict.items():
            self.db.store_results(results, condition, flight_profile)
        
        # Get combined data
        df = self.db.get_results_df()
        
        # Generate visualizations
        fig_risk = self.visualizer.plot_risk_analysis(df)
        fig_stats = self.visualizer.plot_statistical_summary(df)
        
        # Statistical analysis
        stats_summary = self._statistical_analysis(df)
        
        return {
            'figures': {
                'risk_analysis': fig_risk,
                'statistical_summary': fig_stats
            },
            'statistics': stats_summary
        }
    
    def _calculate_metrics(self, results: Dict[str, np.ndarray]) -> Dict:
        """Calculate key metrics from results"""
        return {
            'barotitis_risk': np.mean(results['barotitis']),
            'baromyringitis_risk': np.mean(results['baromyringitis']),
            'max_pressure_gradient': np.max(np.abs(results['dP'])),
            'et_locked_duration': np.mean(results['ET_locked']),
            'time_to_symptoms': self._calculate_time_to_symptoms(results)
        }
    
    def _statistical_analysis(self, df: pd.DataFrame) -> Dict:
        """Perform statistical analysis on results"""
        # Group by condition
        grouped = df.groupby('condition')
        
        # Calculate statistics
        stats_dict = {
            'barotitis_risk': grouped['barotitis_risk'].agg(['mean', 'std']),
            'baromyringitis_risk': grouped['baromyringitis_risk'].agg(['mean', 'std']),
            'pressure_gradient': grouped['pressure_gradient'].agg(['mean', 'std', 'max'])
        }
        
        # Perform ANOVA
        conditions = df['condition'].unique()
        f_stat, p_value = stats.f_oneway(*[
            df[df['condition'] == cond]['risk_score']
            for cond in conditions
        ])
        
        stats_dict['anova'] = {
            'f_statistic': f_stat,
            'p_value': p_value
        }
        
        return stats_dict
    
    def _calculate_time_to_symptoms(self, results: Dict[str, np.ndarray]) -> float:
        """Calculate time until symptoms appear"""
        if not np.any(results['barotitis']):
            return float('inf')
        return results['time'][np.where(results['barotitis'])[0][0]] 