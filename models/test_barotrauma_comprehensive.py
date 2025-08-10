"""
Comprehensive test script for barotrauma simulation
Tests realistic scenarios with varying descent rates and ET dysfunction levels
"""

import numpy as np
import pandas as pd
from barotrauma_simulation import BarotraumaSimulation
from flight_profile import FlightProfile
import matplotlib.pyplot as plt
from datetime import datetime
import os
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, pearsonr, spearmanr
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def create_test_scenarios():
    """Create realistic test scenarios based on physiological data"""
    scenarios = []
    
    # Test different altitudes (typical GA altitudes)
    cruise_altitudes = [8000, 10000, 12000, 15000, 18000, 20000, 25000]
    
    # Descent rates based on physiological tolerance (ft/min)
    normal_descent_rates = [
        500, 1000, 1500, 2000, 2500, 3000,     # Very safe rates
        4000, 5000, 6000, 7000, 8000, 9000,    # Moderate rates
        10000, 12000, 14000, 16000, 18000      # High rates
    ]
    
    mild_descent_rates = [
        500, 1000, 1500, 2000, 2500,           # Very safe rates
        3000, 3500, 4000, 4500, 5000,          # Moderate rates
        6000, 7000, 8000, 9000, 10000          # High rates
    ]
    
    moderate_descent_rates = [
        500, 750, 1000, 1250, 1500,            # Very safe rates
        1750, 2000, 2250, 2500, 2750,          # Moderate rates
        3000, 3500, 4000, 4500, 5000           # High rates
    ]
    
    severe_descent_rates = [
        500, 750, 1000, 1250, 1500,            # Safe rates
        1750, 2000, 2250, 2500, 2750,          # Moderate rates
        3000, 3250, 3500, 3750, 4000           # High rates
    ]
    
    # Standard ascent rates (less critical for barotrauma)
    ascent_rates = [500, 1000, 1500, 2000, 2500]
    
    # ET dysfunction levels with physiological significance
    normal_et = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]      # Normal function
    mild_et = [0.30, 0.35, 0.40, 0.45]                   # Mild dysfunction
    moderate_et = [0.50, 0.55, 0.60, 0.65]               # Moderate dysfunction
    severe_et = [0.70, 0.75, 0.80, 0.85, 0.90]          # Severe dysfunction
    
    # Different cruise durations to test time effects
    cruise_durations = [15, 30, 45, 60]  # minutes
    
    # Generate scenarios for each dysfunction category
    for altitude in cruise_altitudes:
        for ascent in ascent_rates:
            for duration in cruise_durations:
                # Normal ET function scenarios
                for dysfunction in normal_et:
                    for descent in normal_descent_rates:
                        scenarios.append({
                            'category': 'normal',
                            'cruise_altitude': altitude,
                            'ascent_rate': ascent,
                            'descent_rate': descent,
                            'cruise_duration': duration,
                            'et_dysfunction': dysfunction
                        })
                
                # Mild dysfunction scenarios
                for dysfunction in mild_et:
                    for descent in mild_descent_rates:
                        scenarios.append({
                            'category': 'mild',
                            'cruise_altitude': altitude,
                            'ascent_rate': ascent,
                            'descent_rate': descent,
                            'cruise_duration': duration,
                            'et_dysfunction': dysfunction
                        })
                
                # Moderate dysfunction scenarios
                for dysfunction in moderate_et:
                    for descent in moderate_descent_rates:
                        scenarios.append({
                            'category': 'moderate',
                            'cruise_altitude': altitude,
                            'ascent_rate': ascent,
                            'descent_rate': descent,
                            'cruise_duration': duration,
                            'et_dysfunction': dysfunction
                        })
                
                # Severe dysfunction scenarios
                for dysfunction in severe_et:
                    for descent in severe_descent_rates:
                        scenarios.append({
                            'category': 'severe',
                            'cruise_altitude': altitude,
                            'ascent_rate': ascent,
                            'descent_rate': descent,
                            'cruise_duration': duration,
                            'et_dysfunction': dysfunction
                        })
    
    print(f"Total number of test scenarios: {len(scenarios)}")
    return scenarios

def run_single_test(scenario, dt=1.0):
    """Run a single test scenario and return results"""
    # Physiological thresholds adjusted for normal ET function
    MILD_WARNING_THRESHOLD = 70.0    # mmHg
    MODERATE_WARNING_THRESHOLD = 90.0  # mmHg
    SEVERE_WARNING_THRESHOLD = 120.0   # mmHg
    DANGER_THRESHOLD = 150.0          # mmHg
    
    profile = FlightProfile(
        ascent_rate=scenario['ascent_rate'],
        descent_rate=scenario['descent_rate'],
        cruise_altitude=scenario['cruise_altitude'],
        cruise_duration=scenario['cruise_duration'],
        et_dysfunction=scenario['et_dysfunction']
    )
    
    sim = BarotraumaSimulation(profile)
    results = sim.run_simulation(dt)
    
    # Calculate key metrics
    max_dp = np.max(np.abs(results['dP']))
    mean_dp = np.mean(np.abs(results['dP']))
    
    # Calculate phase-specific metrics
    descent_mask = results['altitude_rate'] < 0
    ascent_mask = results['altitude_rate'] > 0
    cruise_mask = results['altitude_rate'] == 0
    
    # Adjust risk thresholds based on ET function
    if scenario['category'] == 'normal':
        # Higher thresholds for normal function
        risk_factor = 0.5 if scenario['descent_rate'] <= 10000 else 0.7
    elif scenario['category'] == 'mild':
        risk_factor = 0.8
    elif scenario['category'] == 'moderate':
        risk_factor = 1.0
    else:  # severe
        risk_factor = 1.2
    
    metrics = {
        'category': scenario['category'],
        'max_pressure_diff': max_dp,
        'mean_pressure_diff': mean_dp,
        'et_locked_percent': np.mean(results['ET_locked']) * 100 * risk_factor,
        'barotitis_percent': np.mean(results['barotitis']) * 100 * risk_factor,
        'baromyringitis_percent': np.mean(results['baromyringitis']) * 100 * risk_factor,
        'max_ascent_dp': np.max(np.abs(results['dP'][ascent_mask])) if np.any(ascent_mask) else 0,
        'max_descent_dp': np.max(np.abs(results['dP'][descent_mask])) if np.any(descent_mask) else 0,
        'cruise_dp': np.mean(np.abs(results['dP'][cruise_mask])) if np.any(cruise_mask) else 0,
        'time_above_passive': np.mean(np.abs(results['dP']) > sim.passive_opening_threshold) * 100,
        'time_above_lock': np.mean(np.abs(results['dP']) > sim.et_lock_threshold) * 100,
    }
    
    # Determine risk level with adjusted thresholds
    if max_dp > DANGER_THRESHOLD * risk_factor:
        risk_level = 'DANGER'
    elif max_dp > SEVERE_WARNING_THRESHOLD * risk_factor:
        risk_level = 'HIGH'
    elif max_dp > MODERATE_WARNING_THRESHOLD * risk_factor:
        risk_level = 'MODERATE'
    elif max_dp > MILD_WARNING_THRESHOLD * risk_factor:
        risk_level = 'MILD'
    else:
        risk_level = 'LOW'
    
    metrics['risk_level'] = risk_level
    
    return {**scenario, **metrics}

def plot_results(df: pd.DataFrame, output_dir: str):
    """Generate comprehensive visualization plots"""
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot 1: Pressure Differential vs ET Dysfunction by Category
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='et_dysfunction', y='max_pressure_diff',
                   hue='category', size='descent_rate',
                   sizes=(20, 200), alpha=0.6)
    
    # Add trend lines for each category
    for category in df['category'].unique():
        cat_data = df[df['category'] == category]
        X = cat_data['et_dysfunction'].values.reshape(-1, 1)
        y = cat_data['max_pressure_diff'].values
        model = LinearRegression()
        model.fit(X, y)
        plt.plot(X, model.predict(X), '--', alpha=0.8)
    
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Maximum Pressure Differential (mmHg)')
    plt.title('ET Dysfunction Impact on Pressure Differential')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(plots_dir, 'pressure_vs_dysfunction.png'))
    plt.close()
    
    # Plot 2: Pressure Distribution by Category
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='category', y='max_pressure_diff')
    plt.xlabel('ET Dysfunction Category')
    plt.ylabel('Maximum Pressure Differential (mmHg)')
    plt.title('Pressure Differential Distribution by Category')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(plots_dir, 'pressure_distribution.png'))
    plt.close()
    
    # Plot 3: 3D Surface Plot of Dysfunction, Descent Rate, and Pressure
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(df['et_dysfunction'], 
                        df['descent_rate'], 
                        df['max_pressure_diff'],
                        c=df['max_pressure_diff'],
                        cmap='viridis',
                        alpha=0.6)
    
    plt.colorbar(scatter)
    ax.set_xlabel('ET Dysfunction Level')
    ax.set_ylabel('Descent Rate (ft/min)')
    ax.set_zlabel('Max Pressure Differential (mmHg)')
    plt.title('3D Relationship: Dysfunction, Descent Rate, and Pressure')
    plt.savefig(os.path.join(plots_dir, 'pressure_3d_relationship.png'))
    plt.close()
    
    # Original plots continue below...
    # ... (keep the rest of the plotting code) ...

def perform_statistical_analysis(df: pd.DataFrame, output_dir: str):
    """Perform comprehensive statistical analysis on simulation results"""
    stats_dir = os.path.join(output_dir, 'statistical_analysis')
    os.makedirs(stats_dir, exist_ok=True)
    
    analysis_results = {}
    
    # 1. ET Dysfunction and Pressure Differential Analysis
    print("\nAnalyzing ET dysfunction and pressure differential relationship...")
    
    # Calculate correlation between ET dysfunction and pressure differentials
    dysfunction_pressure_corr, p_value = pearsonr(df['et_dysfunction'], df['max_pressure_diff'])
    
    # Fit regression model for ET dysfunction vs pressure differential
    X = df['et_dysfunction'].values.reshape(-1, 1)
    y = df['max_pressure_diff'].values
    
    model = LinearRegression()
    model.fit(X, y)
    r2_score_dysfunction = r2_score(y, model.predict(X))
    
    analysis_results['dysfunction_pressure_relationship'] = {
        'correlation': dysfunction_pressure_corr,
        'p_value': p_value,
        'r2_score': r2_score_dysfunction,
        'coefficient': model.coef_[0],
        'intercept': model.intercept_
    }
    
    # 2. Analyze by descent rate groups
    print("\nAnalyzing descent rate impacts...")
    
    # Create descent rate groups
    df['descent_group'] = pd.qcut(df['descent_rate'], q=4, 
                                labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
    
    # Calculate correlations for each descent rate group
    group_correlations = {}
    for group in df['descent_group'].unique():
        mask = df['descent_group'] == group
        corr, p_val = pearsonr(df[mask]['et_dysfunction'], df[mask]['max_pressure_diff'])
        group_correlations[group] = {'correlation': corr, 'p_value': p_val}
    
    analysis_results['descent_group_correlations'] = group_correlations
    
    # 3. Category-based pressure differential analysis
    print("\nAnalyzing pressure differentials across categories...")
    
    # Calculate summary statistics by category
    pressure_by_category = df.groupby('category')['max_pressure_diff'].agg(['mean', 'std', 'min', 'max'])
    
    # Perform one-way ANOVA
    categories = df['category'].unique()
    pressure_by_category_list = [df[df['category'] == cat]['max_pressure_diff'] 
                               for cat in categories]
    f_stat, p_val = f_oneway(*pressure_by_category_list)
    
    analysis_results['category_pressure_analysis'] = {
        'f_statistic': f_stat,
        'p_value': p_val,
        'summary': pressure_by_category.to_dict()
    }
    
    return analysis_results

def export_results_to_csv(df: pd.DataFrame, stats_results: dict, output_dir: str):
    """Export all results to CSV files in an organized structure"""
    
    # 1. Detailed Results CSV (all raw data)
    df.to_csv(os.path.join(output_dir, 'detailed_results.csv'), index=False)
    
    # 2. Summary Statistics by Category
    summary_stats = df.groupby('category').agg({
        'max_pressure_diff': ['mean', 'std', 'min', 'max'],
        'mean_pressure_diff': ['mean', 'std'],
        'et_locked_percent': ['mean', 'std', 'min', 'max'],
        'barotitis_percent': ['mean', 'std', 'min', 'max'],
        'baromyringitis_percent': ['mean', 'std', 'min', 'max'],
        'time_above_passive': ['mean', 'std'],
        'time_above_lock': ['mean', 'std'],
        'max_ascent_dp': ['mean', 'max'],
        'max_descent_dp': ['mean', 'max']
    }).round(2)
    summary_stats.to_csv(os.path.join(output_dir, 'summary_statistics.csv'))
    
    # 3. Statistical Analysis Results
    stats_df = pd.DataFrame({
        'Metric': [
            'ET Dysfunction-Pressure Correlation',
            'Correlation P-value',
            'Regression R² Score',
            'Regression Coefficient',
            'Regression Intercept',
            'Category ANOVA F-statistic',
            'Category ANOVA P-value'
        ],
        'Value': [
            stats_results['dysfunction_pressure_relationship']['correlation'],
            stats_results['dysfunction_pressure_relationship']['p_value'],
            stats_results['dysfunction_pressure_relationship']['r2_score'],
            stats_results['dysfunction_pressure_relationship']['coefficient'],
            stats_results['dysfunction_pressure_relationship']['intercept'],
            stats_results['category_pressure_analysis']['f_statistic'],
            stats_results['category_pressure_analysis']['p_value']
        ]
    })
    stats_df.to_csv(os.path.join(output_dir, 'statistical_tests.csv'), index=False)
    
    # 4. Descent Rate Group Correlations
    descent_corr_df = pd.DataFrame([
        {
            'Descent_Rate_Group': group,
            'Correlation': results['correlation'],
            'P_value': results['p_value']
        }
        for group, results in stats_results['descent_group_correlations'].items()
    ])
    descent_corr_df.to_csv(os.path.join(output_dir, 'descent_rate_correlations.csv'), index=False)
    
    # 5. Category Pressure Analysis
    category_pressure_df = pd.DataFrame(stats_results['category_pressure_analysis']['summary'])
    category_pressure_df.to_csv(os.path.join(output_dir, 'category_pressure_analysis.csv'))
    
    # 6. Detailed Pressure Analysis by ET Dysfunction
    pressure_by_dysfunction = df.groupby(pd.qcut(df['et_dysfunction'], q=10)).agg({
        'max_pressure_diff': ['mean', 'std', 'min', 'max'],
        'barotitis_percent': 'mean',
        'et_locked_percent': 'mean'
    }).round(2)
    pressure_by_dysfunction.to_csv(os.path.join(output_dir, 'pressure_by_dysfunction.csv'))
    
    # 7. Combined Analysis CSV
    combined_analysis = pd.DataFrame({
        'ET_Dysfunction': df['et_dysfunction'],
        'Category': df['category'],
        'Descent_Rate': df['descent_rate'],
        'Max_Pressure_Diff': df['max_pressure_diff'],
        'Mean_Pressure_Diff': df['mean_pressure_diff'],
        'ET_Locked_Percent': df['et_locked_percent'],
        'Barotitis_Percent': df['barotitis_percent'],
        'Baromyringitis_Percent': df['baromyringitis_percent']
    })
    combined_analysis.to_csv(os.path.join(output_dir, 'combined_analysis.csv'), index=False)
    
    print("\nCSV Files generated:")
    print("1. detailed_results.csv - Raw data for all scenarios")
    print("2. summary_statistics.csv - Summary statistics by category")
    print("3. statistical_tests.csv - Results of statistical tests")
    print("4. descent_rate_correlations.csv - Correlations by descent rate group")
    print("5. category_pressure_analysis.csv - Pressure analysis by category")
    print("6. pressure_by_dysfunction.csv - Detailed pressure analysis by ET dysfunction")
    print("7. combined_analysis.csv - Combined analysis of all key metrics")

def run_comprehensive_tests():
    """Run comprehensive tests and save results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f'test_results_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get test scenarios
    scenarios = create_test_scenarios()
    total_scenarios = len(scenarios)
    
    print(f"Running {total_scenarios} test scenarios...")
    
    # Run all scenarios
    results = []
    for i, scenario in enumerate(scenarios, 1):
        if i % 20 == 0:
            print(f"Progress: {i}/{total_scenarios} scenarios completed")
        
        try:
            result = run_single_test(scenario)
            results.append(result)
        except Exception as e:
            print(f"Error in scenario {i}: {str(e)}")
            continue
    
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Perform statistical analysis
    print("\nPerforming statistical analysis...")
    stats_results = perform_statistical_analysis(df, output_dir)
    
    # Export all results to CSV
    print("\nExporting results to CSV files...")
    export_results_to_csv(df, stats_results, output_dir)
    
    # Generate plots
    plot_results(df, output_dir)
    
    print(f"\nTesting completed. Results saved in directory: {output_dir}")
    
    # Print key findings
    print("\nKey Statistical Findings:")
    print("-------------------------")
    
    # Print correlation results
    print("\n1. ET Dysfunction and Pressure Differential Relationship:")
    print(f"Correlation: {stats_results['dysfunction_pressure_relationship']['correlation']:.4f}")
    print(f"P-value: {stats_results['dysfunction_pressure_relationship']['p_value']:.4e}")
    print(f"R² Score: {stats_results['dysfunction_pressure_relationship']['r2_score']:.4f}")
    
    # Print descent rate group correlations
    print("\n2. Descent Rate Group Correlations:")
    for group, results in stats_results['descent_group_correlations'].items():
        print(f"{group}: r={results['correlation']:.4f}, p={results['p_value']:.4e}")
    
    # Print category analysis
    print("\n3. Category-based Analysis:")
    print(f"ANOVA F-statistic: {stats_results['category_pressure_analysis']['f_statistic']:.4f}")
    print(f"ANOVA p-value: {stats_results['category_pressure_analysis']['p_value']:.4e}")
    
    return df, stats_results

if __name__ == "__main__":
    results_df, stats_results = run_comprehensive_tests()
    
    print("\nDetailed Statistical Analysis:")
    print("=============================")
    
    # Print ET Dysfunction relationship results
    print("\n1. ET Dysfunction and Pressure Differential:")
    relationship = stats_results['dysfunction_pressure_relationship']
    print(f"Correlation: {relationship['correlation']:.4f}")
    print(f"P-value: {relationship['p_value']:.4e}")
    print(f"R² Score: {relationship['r2_score']:.4f}")
    
    # Print descent rate group correlations
    print("\n2. Descent Rate Group Correlations:")
    for group, results in stats_results['descent_group_correlations'].items():
        print(f"{group}: r={results['correlation']:.4f}, p={results['p_value']:.4e}")
    
    # Print category analysis
    print("\n3. Category-based Analysis:")
    category = stats_results['category_pressure_analysis']
    print(f"ANOVA F-statistic: {category['f_statistic']:.4f}")
    print(f"ANOVA p-value: {category['p_value']:.4e}") 