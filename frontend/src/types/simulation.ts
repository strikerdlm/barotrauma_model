/**
 * Barotrauma Risk Assessment - Type Definitions
 * 
 * Based on physiological models from:
 * - Kanick & Doyle (2005) - Barotrauma during air travel: mathematical model
 * - Ryan et al. (2018) - Prevention of otic barotrauma in aviation
 * - Bayoumy et al. (2021) - Management of tympanic membrane retractions
 */

/** Clinical severity levels for Eustachian tube dysfunction */
export type ETSeverity = 'mild' | 'moderate' | 'severe';

/** Risk categories for clinical decision support */
export type RiskCategory = 'Low' | 'Moderate' | 'High';

/** Scenario type selection */
export type ScenarioType = 'hypobaric_chamber' | 'flight_simulation' | 'custom';

/**
 * Configuration for a hypobaric chamber descent simulation
 */
export interface ChamberScenario {
  /** Starting altitude in feet (8,000 - 40,000 ft typical) */
  startAltitudeFt: number;
  /** Descent rate in feet per minute (1,000 - 10,000 ft/min) */
  descentRateFtMin: number;
  /** Eustachian tube dysfunction severity level */
  etSeverity: ETSeverity;
  /** Whether Valsalva maneuvers are enabled */
  enableValsalva: boolean;
  /** Time between Valsalva maneuvers in seconds */
  valsalvaIntervalS: number;
  /** Tympanic cavity volume in mL (default: 1.0) */
  tympanumVolumeMl: number;
  /** Mastoid air cell volume in mL (default: 7.75) */
  mastoidVolumeMl: number;
}

/**
 * Result of a chamber descent simulation
 */
export interface SimulationResult {
  /** Time array in seconds */
  timeS: number[];
  /** Altitude profile in feet */
  altitudeFt: number[];
  /** Ambient pressure in mmHg */
  pAmbMmHg: number[];
  /** Middle ear pressure in mmHg */
  pMeMmHg: number[];
  /** Pressure differential (P_ME - P_amb) in mmHg */
  deltaPMmHg: number[];
  /** Tympanic membrane displacement in mL */
  tmDisplacementMl: number[];
  /** Equalization rate over time in mmHg/s */
  equalizationRateMmHgS: number[];
  /** Integrated risk score (0-1) */
  riskScore: number;
  /** Clinical risk category */
  riskCategory: RiskCategory;
  /** Detailed metrics */
  metrics: SimulationMetrics;
}

/**
 * Detailed simulation metrics
 */
export interface SimulationMetrics {
  /** Maximum absolute pressure differential */
  maxAbsDeltaPMmHg: number;
  /** Mean absolute pressure differential */
  meanAbsDeltaPMmHg: number;
  /** Fraction of time with |ΔP| > ET lock threshold */
  fractionTimeAboveLock: number;
  /** Fraction of time with |ΔP| > rupture threshold */
  fractionTimeAboveRupture: number;
  /** Mean equalization speed */
  meanEqualizationSpeedMmHgS: number;
  /** Descent risk factor (0-1) */
  descentRiskFactor: number;
  /** Time at ET lock threshold */
  timeAtETLock: number;
  /** Peak TM displacement */
  peakTMDisplacementMl: number;
}

/**
 * Reference data point for validation
 */
export interface ValidationDataPoint {
  timeS: number;
  pressureMmH2O: number;
  source: string;
}

/**
 * Scientific reference/citation
 */
export interface ScientificReference {
  id: string;
  authors: string[];
  year: number;
  title: string;
  journal: string;
  volume?: string;
  pages?: string;
  doi?: string;
  pmid?: string;
  relevance: string;
}

/**
 * Risk analysis for sensitivity studies
 */
export interface SensitivityPoint {
  parameterValue: number;
  riskScore: number;
  maxDeltaP: number;
}

/**
 * 3D surface data for visualization
 */
export interface SurfaceData {
  x: number[];
  y: number[];
  z: number[][];
}

/**
 * Heatmap data structure
 */
export interface HeatmapData {
  xLabels: string[] | number[];
  yLabels: string[];
  values: number[][];
}

/**
 * Chart theme configuration
 */
export interface ChartTheme {
  backgroundColor: string;
  textColor: string;
  axisLineColor: string;
  gridColor: string;
  primaryColor: string;
  successColor: string;
  warningColor: string;
  dangerColor: string;
  gradients: {
    risk: string[];
    pressure: string[];
    altitude: string[];
  };
}

/**
 * Dashboard state
 */
export interface DashboardState {
  scenario: ChamberScenario;
  result: SimulationResult | null;
  isLoading: boolean;
  activeTab: string;
  showReferences: boolean;
}

// Type guards
export function isValidSeverity(value: string): value is ETSeverity {
  return ['mild', 'moderate', 'severe'].includes(value);
}

export function isValidRiskCategory(value: string): value is RiskCategory {
  return ['Low', 'Moderate', 'High'].includes(value);
}
