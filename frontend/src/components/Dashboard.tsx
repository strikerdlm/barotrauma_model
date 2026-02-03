/**
 * Barotrauma Safety Management Dashboard
 * 
 * Main dashboard component integrating all visualization and control elements
 * for publication-ready barotrauma risk assessment.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Gauge, 
  TrendingDown, 
  AlertTriangle, 
  Settings, 
  BarChart3,
  Layers3,
  LineChart,
  Grid3X3,
  Clock,
  Wind,
  Download,
  RefreshCw
} from 'lucide-react';

import { MetricCard, Slider, TabGroup, ReferencesPanel } from './ui';
import {
  RiskGauge,
  PressureDynamics,
  RiskHeatmap,
  RiskSurface3D,
  SensitivityAnalysis,
  EqualizationChart,
  AltitudeProfile,
} from './charts';

import {
  simulateDescent,
  createDefaultScenario,
  riskVsDescentRate,
  generateRiskHeatmap,
  generateRiskSurface,
  ET_SEVERITY_TO_DYSFUNCTION,
  ET_LOCK_THRESHOLD,
  MEMBRANE_RUPTURE_THRESHOLD,
} from '../lib/simulation';

import type { ChamberScenario, ETSeverity, SimulationResult } from '../types/simulation';

const tabs = [
  { id: 'overview', label: 'Overview', icon: <Gauge className="w-4 h-4" /> },
  { id: 'pressure', label: 'Pressure Dynamics', icon: <LineChart className="w-4 h-4" /> },
  { id: 'equalization', label: 'Equalization', icon: <Activity className="w-4 h-4" /> },
  { id: 'sensitivity', label: 'Sensitivity', icon: <BarChart3 className="w-4 h-4" /> },
  { id: '3d', label: '3D Surface', icon: <Layers3 className="w-4 h-4" /> },
  { id: 'heatmap', label: 'Risk Matrix', icon: <Grid3X3 className="w-4 h-4" /> },
];

export const Dashboard: React.FC = () => {
  // State
  const [scenario, setScenario] = useState<ChamberScenario>(createDefaultScenario());
  const [activeTab, setActiveTab] = useState('overview');
  const [showReferences, setShowReferences] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

  // Run simulation
  const result = useMemo<SimulationResult>(() => {
    setIsSimulating(true);
    try {
      const res = simulateDescent(scenario);
      return res;
    } finally {
      setIsSimulating(false);
    }
  }, [scenario]);

  // Sensitivity data
  const sensitivityData = useMemo(() => {
    const rates = Array.from({ length: 19 }, (_, i) => 1000 + i * 500);
    return riskVsDescentRate(scenario, rates);
  }, [scenario]);

  // Heatmap data
  const heatmapData = useMemo(() => {
    const rates = Array.from({ length: 19 }, (_, i) => 1000 + i * 500);
    return generateRiskHeatmap(scenario, rates);
  }, [scenario]);

  // 3D Surface data
  const surfaceData = useMemo(() => {
    const etRange = Array.from({ length: 15 }, (_, i) => i * (1 / 14));
    const rateRange = Array.from({ length: 15 }, (_, i) => 1000 + i * 643);
    return generateRiskSurface(scenario, etRange, rateRange);
  }, [scenario]);

  // Handlers
  const updateScenario = useCallback((updates: Partial<ChamberScenario>) => {
    setScenario(prev => ({ ...prev, ...updates }));
  }, []);

  const handleExportData = useCallback(() => {
    const dataStr = JSON.stringify({
      scenario,
      result: {
        riskScore: result.riskScore,
        riskCategory: result.riskCategory,
        metrics: result.metrics,
        timeSeriesLength: result.timeS.length,
      },
      generatedAt: new Date().toISOString(),
    }, null, 2);
    
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `barotrauma-analysis-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [scenario, result]);

  const resetScenario = useCallback(() => {
    setScenario(createDefaultScenario());
  }, []);

  // Risk color helpers
  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'risk-low';
    if (score < 0.6) return 'risk-moderate';
    return 'risk-high';
  };

  const getVariant = (score: number): 'success' | 'warning' | 'danger' => {
    if (score < 0.3) return 'success';
    if (score < 0.6) return 'warning';
    return 'danger';
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-dark-300/80 border-b border-white/5">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', bounce: 0.5 }}
                className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center shadow-lg shadow-primary-500/30"
              >
                <Activity className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-display font-bold text-white">
                  Barotrauma Risk Assessment
                </h1>
                <p className="text-sm text-gray-400">
                  Safety Management Dashboard for Hypobaric Chamber Operations
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleExportData}
                className="btn-secondary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
              <button
                onClick={resetScenario}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-[1800px] mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar Controls */}
          <aside className="col-span-3 space-y-6">
            {/* Configuration Panel */}
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Settings className="w-5 h-5 text-primary-400" />
                <h2 className="font-display font-semibold text-white">Configuration</h2>
              </div>

              <div className="space-y-5">
                {/* ET Severity Selection */}
                <div>
                  <label className="text-sm font-medium text-gray-300 mb-2 block">
                    ET Dysfunction Severity
                  </label>
                  <div className="flex gap-2">
                    {(['mild', 'moderate', 'severe'] as ETSeverity[]).map((sev) => (
                      <button
                        key={sev}
                        onClick={() => updateScenario({ etSeverity: sev })}
                        className={`
                          flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all
                          ${scenario.etSeverity === sev
                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/40'
                            : 'bg-dark-100 text-gray-400 border border-transparent hover:bg-dark-100/80'
                          }
                        `}
                      >
                        {sev.charAt(0).toUpperCase() + sev.slice(1)}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Dysfunction: {(ET_SEVERITY_TO_DYSFUNCTION[scenario.etSeverity] * 100).toFixed(0)}%
                  </p>
                </div>

                {/* Altitude Slider */}
                <Slider
                  label="Starting Altitude"
                  value={scenario.startAltitudeFt}
                  onChange={(v) => updateScenario({ startAltitudeFt: v })}
                  min={8000}
                  max={40000}
                  step={1000}
                  unit="ft"
                />

                {/* Descent Rate Slider */}
                <Slider
                  label="Descent Rate"
                  value={scenario.descentRateFtMin}
                  onChange={(v) => updateScenario({ descentRateFtMin: v })}
                  min={1000}
                  max={10000}
                  step={250}
                  unit="ft/min"
                />

                {/* Valsalva Toggle */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-300">Enable Valsalva</span>
                  <button
                    onClick={() => updateScenario({ enableValsalva: !scenario.enableValsalva })}
                    className={`
                      relative w-12 h-6 rounded-full transition-colors
                      ${scenario.enableValsalva ? 'bg-primary-500' : 'bg-dark-100'}
                    `}
                  >
                    <motion.div
                      animate={{ x: scenario.enableValsalva ? 24 : 2 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-md"
                    />
                  </button>
                </div>

                {scenario.enableValsalva && (
                  <Slider
                    label="Valsalva Interval"
                    value={scenario.valsalvaIntervalS}
                    onChange={(v) => updateScenario({ valsalvaIntervalS: v })}
                    min={30}
                    max={300}
                    step={15}
                    unit="sec"
                  />
                )}
              </div>
            </div>

            {/* Risk Summary */}
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-primary-400" />
                <h2 className="font-display font-semibold text-white">Risk Summary</h2>
              </div>

              <div className="space-y-3">
                {/* Risk Category Badge */}
                <div className="flex items-center justify-between p-3 bg-dark-100/50 rounded-xl">
                  <span className="text-sm text-gray-400">Category</span>
                  <span className={`badge badge-${getRiskColor(result.riskScore).replace('risk-', '')}`}>
                    {result.riskCategory}
                  </span>
                </div>

                {/* Clinical Recommendations */}
                <div className={`
                  p-3 rounded-xl border-l-4
                  ${result.riskScore >= 0.6 
                    ? 'bg-risk-high/10 border-risk-high' 
                    : result.riskScore >= 0.3 
                      ? 'bg-risk-moderate/10 border-risk-moderate'
                      : 'bg-risk-low/10 border-risk-low'
                  }
                `}>
                  <p className="text-sm font-medium mb-2">
                    {result.riskScore >= 0.6 ? '⚠️ High Risk - Action Required'
                      : result.riskScore >= 0.3 ? '⚡ Moderate Risk - Caution'
                      : '✓ Low Risk - Safe'}
                  </p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    {result.riskScore >= 0.6 ? (
                      <>
                        <li>• Reduce descent rate immediately</li>
                        <li>• Increase Valsalva frequency</li>
                        <li>• Monitor for symptoms</li>
                      </>
                    ) : result.riskScore >= 0.3 ? (
                      <>
                        <li>• Consider reducing descent rate</li>
                        <li>• Maintain regular Valsalva</li>
                        <li>• Stay alert for symptoms</li>
                      </>
                    ) : (
                      <>
                        <li>• Continue standard protocol</li>
                        <li>• Standard monitoring sufficient</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
            </div>

            {/* References Panel */}
            <ReferencesPanel 
              isOpen={showReferences} 
              onToggle={() => setShowReferences(!showReferences)} 
            />
          </aside>

          {/* Main Content Area */}
          <main className="col-span-9 space-y-6">
            {/* Key Metrics Row */}
            <div className="grid grid-cols-5 gap-4">
              <MetricCard
                label="Risk Score"
                value={(result.riskScore * 100).toFixed(1)}
                unit="%"
                variant={getVariant(result.riskScore)}
                icon={<Gauge className="w-4 h-4" />}
              />
              <MetricCard
                label="Max |ΔP|"
                value={result.metrics.maxAbsDeltaPMmHg.toFixed(1)}
                unit="mmHg"
                delta={result.metrics.maxAbsDeltaPMmHg - ET_LOCK_THRESHOLD}
                deltaLabel="vs Lock"
                variant={result.metrics.maxAbsDeltaPMmHg > ET_LOCK_THRESHOLD ? 'danger' : 'default'}
                icon={<TrendingDown className="w-4 h-4" />}
              />
              <MetricCard
                label="Time > ET Lock"
                value={(result.metrics.fractionTimeAboveLock * 100).toFixed(1)}
                unit="%"
                variant={result.metrics.fractionTimeAboveLock > 0.1 ? 'warning' : 'default'}
                icon={<Clock className="w-4 h-4" />}
              />
              <MetricCard
                label="Peak TM Displacement"
                value={(result.metrics.peakTMDisplacementMl * 1000).toFixed(1)}
                unit="µL"
                icon={<Activity className="w-4 h-4" />}
              />
              <MetricCard
                label="Mean Eq. Speed"
                value={result.metrics.meanEqualizationSpeedMmHgS.toFixed(3)}
                unit="mmHg/s"
                icon={<Wind className="w-4 h-4" />}
              />
            </div>

            {/* Tab Navigation */}
            <TabGroup
              tabs={tabs}
              activeTab={activeTab}
              onChange={setActiveTab}
            />

            {/* Tab Content */}
            <div className="card min-h-[500px]">
              {activeTab === 'overview' && (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <RiskGauge
                      riskScore={result.riskScore}
                      riskCategory={result.riskCategory}
                      height={320}
                    />
                  </div>
                  <div>
                    <AltitudeProfile result={result} height={320} />
                  </div>
                </div>
              )}

              {activeTab === 'pressure' && (
                <PressureDynamics result={result} height={480} />
              )}

              {activeTab === 'equalization' && (
                <div className="space-y-6">
                  <EqualizationChart result={result} height={380} mode="both" />
                </div>
              )}

              {activeTab === 'sensitivity' && (
                <SensitivityAnalysis
                  data={sensitivityData}
                  currentRate={scenario.descentRateFtMin}
                  currentRisk={result.riskScore}
                  height={480}
                />
              )}

              {activeTab === '3d' && (
                <RiskSurface3D
                  surfaceData={surfaceData}
                  height={500}
                  currentPoint={{
                    et: ET_SEVERITY_TO_DYSFUNCTION[scenario.etSeverity],
                    rate: scenario.descentRateFtMin,
                    risk: result.riskScore,
                  }}
                />
              )}

              {activeTab === 'heatmap' && (
                <RiskHeatmap
                  data={heatmapData}
                  height={400}
                  currentPoint={{
                    x: scenario.descentRateFtMin,
                    y: scenario.etSeverity,
                  }}
                />
              )}
            </div>

            {/* Footer */}
            <footer className="text-center text-xs text-gray-500 py-4">
              <p>
                Barotrauma Risk Assessment System • Based on validated physiological models
              </p>
              <p className="mt-1">
                Primary references: Kanick & Doyle (2005), Ryan et al. (2018), Bayoumy et al. (2021)
              </p>
            </footer>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
