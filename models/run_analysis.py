from simulation_analysis import SimulationAnalysis
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Initialize analyzer
    analyzer = SimulationAnalysis()
    
    # Define parameter ranges based on physiological data
    ascent_rates = [1000, 2000, 3000]  # ft/min
    descent_rates = [1000, 2000, 4000, 8000, 12000, 18000]  # ft/min
    cruise_altitudes = [25000]  # ft
    et_dysfunctions = [0.0, 0.1, 0.3, 0.6, 0.9]  # ranging from normal to severe
    
    print("Running batch simulation...")
    results_df = analyzer.run_batch_simulation(
        ascent_rates=ascent_rates,
        descent_rates=descent_rates,
        cruise_altitudes=cruise_altitudes,
        et_dysfunctions=et_dysfunctions,
        n_iterations=5  # 5 iterations per combination
    )
    
    print("\nGenerating analysis report...")
    stats_report = analyzer.generate_analysis_report(results_df)
    
    # Print summary statistics
    print("\nRisk Score Summary by ET Dysfunction Level:")
    print(stats_report['risk_by_dysfunction'])
    
    print("\nStatistical Tests Results:")
    print("ET Dysfunction Effect (ANOVA):")
    f_stat, p_val = stats_report['statistical_tests']['dysfunction_effect']
    print(f"F-statistic: {f_stat:.2f}, p-value: {p_val:.4f}")
    
    print("\nRate Correlations:")
    ascent_corr, ascent_p = stats_report['statistical_tests']['rate_correlations']['ascent']
    descent_corr, descent_p = stats_report['statistical_tests']['rate_correlations']['descent']
    print(f"Ascent Rate vs Risk: r={ascent_corr:.2f}, p={ascent_p:.4f}")
    print(f"Descent Rate vs Risk: r={descent_corr:.2f}, p={descent_p:.4f}")
    
    # Generate visualizations
    print("\nGenerating plots...")
    analyzer.plot_analysis_results(results_df, save_path='analysis_results.png')
    
    print("\nAnalysis complete. Results saved to 'analysis_results.png'")
    
    return results_df, stats_report

if __name__ == "__main__":
    main() 