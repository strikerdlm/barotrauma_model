/**
 * Barotrauma Risk Simulation Engine
 * 
 * TypeScript implementation of the physics-informed, physiology-constrained
 * simulator for middle-ear barotrauma risk during hypobaric chamber training.
 * 
 * Based on validated models from:
 * - Kanick & Doyle (2005): Barotrauma during air travel predictions
 * - Boyle's Law: P₁V₁ = P₂V₂ for gas pressure-volume relationships
 * - Clinical thresholds from aerospace medicine literature
 */

import type {
  ChamberScenario,
  SimulationResult,
  SimulationMetrics,
  ETSeverity,
  RiskCategory,
  SensitivityPoint,
  HeatmapData,
} from '../types/simulation';

// ============================================================================
// Physical Constants and Clinical Thresholds
// ============================================================================

/** ET dysfunction levels mapped to numerical dysfunction factor (0-1) */
export const ET_SEVERITY_TO_DYSFUNCTION: Record<ETSeverity, number> = {
  mild: 0.35,
  moderate: 0.60,
  severe: 0.85,
};

/** Safe descent rates by severity (ft/min) */
export const SAFE_DESCENT_RATES: Record<ETSeverity, number> = {
  mild: 2500.0,
  moderate: 1500.0,
  severe: 1000.0,
};

/** Critical descent rates by severity (ft/min) */
export const CRITICAL_DESCENT_RATES: Record<ETSeverity, number> = {
  mild: 8000.0,
  moderate: 4000.0,
  severe: 2500.0,
};

/** Passive ET opening pressure threshold (mmHg) */
export const PASSIVE_OPENING_THRESHOLD = 15.0;

/** ET locking risk threshold (mmHg) */
export const ET_LOCK_THRESHOLD = 90.0;

/** Membrane rupture risk threshold (mmHg) */
export const MEMBRANE_RUPTURE_THRESHOLD = 150.0;

/** Maximum tympanic membrane displacement (mL) */
export const TM_MAX_DISPLACEMENT_ML = 0.30;

/** TM compliance coefficient (mL/mmHg) */
export const TM_COMPLIANCE_ML_PER_MMHG = TM_MAX_DISPLACEMENT_ML / 100.0;

/** Standard atmospheric pressure at sea level (mmHg) */
export const P0_MMHG = 760.0;

/** Legacy scale height for the old isothermal barometric approximation (ft) */
export const SCALE_HEIGHT_FT = 29921.0;

/** Feet-to-meter conversion */
export const FT_TO_M = 0.3048;

/** ISA sea-level temperature (K) */
export const ISA_SEA_LEVEL_TEMP_K = 288.15;

/** ISA tropospheric lapse rate (K/m) */
export const ISA_TROPOSPHERIC_LAPSE_K_PER_M = 0.0065;

/** ISA tropopause pressure-altitude boundary (m) */
export const ISA_TROPOPAUSE_ALT_M = 11000.0;

/** Standard gravity (m/s^2) */
export const ACCEL_G_M_S2 = 9.80665;

/** Dry-air molar mass (kg/mol) */
export const ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL = 0.0289644;

/** Universal gas constant (J/mol/K) */
export const ISA_GAS_CONSTANT_J_PER_MOL_K = 8.3144598;

const ISA_TROPOSPHERE_EXPONENT =
  (ACCEL_G_M_S2 * ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL) /
  (ISA_GAS_CONSTANT_J_PER_MOL_K * ISA_TROPOSPHERIC_LAPSE_K_PER_M);

const ISA_TROPOPAUSE_TEMP_K =
  ISA_SEA_LEVEL_TEMP_K - ISA_TROPOSPHERIC_LAPSE_K_PER_M * ISA_TROPOPAUSE_ALT_M;

const ISA_TROPOPAUSE_PRESSURE_MMHG =
  P0_MMHG *
  Math.pow(ISA_TROPOPAUSE_TEMP_K / ISA_SEA_LEVEL_TEMP_K, ISA_TROPOSPHERE_EXPONENT);

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Convert pressure altitude to pressure using the U.S. Standard Atmosphere.
 */
export function altitudeToPressureMmHg(altitudeFt: number): number {
  const altitudeM = altitudeFt * FT_TO_M;
  if (altitudeM <= ISA_TROPOPAUSE_ALT_M) {
    return (
      P0_MMHG *
      Math.pow(
        1.0 - (ISA_TROPOSPHERIC_LAPSE_K_PER_M * altitudeM) / ISA_SEA_LEVEL_TEMP_K,
        ISA_TROPOSPHERE_EXPONENT
      )
    );
  }

  return (
    ISA_TROPOPAUSE_PRESSURE_MMHG *
    Math.exp(
      (-ACCEL_G_M_S2 *
        ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL *
        (altitudeM - ISA_TROPOPAUSE_ALT_M)) /
        (ISA_GAS_CONSTANT_J_PER_MOL_K * ISA_TROPOPAUSE_TEMP_K)
    )
  );
}

/**
 * Calculate risk factor from descent rate vs severity-specific envelope
 * Uses logarithmic scaling between safe and critical rates
 */
function riskFactorFromDescent(severity: ETSeverity, descentRate: number): number {
  const safe = SAFE_DESCENT_RATES[severity];
  const critical = CRITICAL_DESCENT_RATES[severity];
  
  if (descentRate <= safe) {
    return 0.0;
  }
  
  // Logarithmic growth up to 1.0 at critical threshold
  const ratio = Math.min(Math.max(descentRate / safe, 1.0), critical / safe);
  return Math.log(ratio) / Math.log(critical / safe);
}

/**
 * Calculate effective equalization speed (mmHg/s)
 * Factors: baseline capability, dysfunction level, descent risk, pressure differential, Valsalva
 */
function equalizationSpeedMmHgS(
  dysfunction: number,
  riskFactor: number,
  deltaPMmHg: number,
  valsalvaBoost: number
): number {
  const baseSpeed = 1.0; // mmHg/s baseline equalization capability
  
  // Dysfunction reduces capability: 1.0 → 0.4 as dysfunction 0 → 1
  const dysfunctionScale = 1.0 - 0.6 * dysfunction;
  
  // Fast descent impairs equalization: down to 0.3 at high risk
  const descentPenalty = 1.0 - 0.7 * riskFactor;
  
  // Higher pressure differential increases passive opening above threshold
  let pressureFactor = 0.0;
  if (Math.abs(deltaPMmHg) > PASSIVE_OPENING_THRESHOLD) {
    pressureFactor = 0.5 * ((Math.abs(deltaPMmHg) / PASSIVE_OPENING_THRESHOLD) - 1.0);
  }
  
  const speed = baseSpeed * dysfunctionScale * descentPenalty * (1.0 + pressureFactor);
  return Math.max(0.0, speed * (1.0 + valsalvaBoost));
}

/**
 * Calculate TM displacement using linear compliance model
 * Capped at physiological maximum
 */
function tmDisplacementMl(deltaPMmHg: number): number {
  const displacement = deltaPMmHg * TM_COMPLIANCE_ML_PER_MMHG;
  return Math.min(Math.max(displacement, -TM_MAX_DISPLACEMENT_ML), TM_MAX_DISPLACEMENT_ML);
}

/**
 * Categorize risk score into clinical category
 */
function categorizeRisk(score: number): RiskCategory {
  if (score < 0.3) return 'Low';
  if (score < 0.6) return 'Moderate';
  return 'High';
}

// ============================================================================
// Main Simulation Function
// ============================================================================

/**
 * Simulate hypobaric chamber descent and calculate barotrauma risk
 * 
 * Physics:
 * - Ambient pressure rises during descent (ISA pressure altitude)
 * - Middle ear attempts to equalize via Eustachian tube
 * - Negative ΔP indicates tympanic membrane pulled inward
 * - ET dysfunction reduces equalization rate
 * - Valsalva maneuvers temporarily boost equalization
 * 
 * @param scenario - Chamber descent configuration
 * @returns Complete simulation results with risk assessment
 */
export function simulateDescent(scenario: ChamberScenario): SimulationResult {
  // Validate input parameters
  if (scenario.descentRateFtMin < 1000 || scenario.descentRateFtMin > 10000) {
    throw new Error('Descent rate must be between 1000 and 10000 ft/min');
  }
  if (scenario.startAltitudeFt <= 0) {
    throw new Error('Starting altitude must be positive');
  }
  
  const dysfunction = ET_SEVERITY_TO_DYSFUNCTION[scenario.etSeverity];
  const riskFactor = riskFactorFromDescent(scenario.etSeverity, scenario.descentRateFtMin);
  
  // Time grid: simulate descent from start_altitude to sea level
  const descentRateFtS = scenario.descentRateFtMin / 60.0;
  const totalSeconds = Math.ceil(scenario.startAltitudeFt / descentRateFtS);
  
  // Pre-allocate arrays
  const timeS: number[] = [];
  const altitudeFt: number[] = [];
  const pAmbMmHg: number[] = [];
  const pMeMmHg: number[] = [];
  const eqRateSeries: number[] = [];
  const tmDisp: number[] = [];
  
  // Generate time array
  for (let t = 0; t <= totalSeconds; t++) {
    timeS.push(t);
  }
  
  // Calculate altitude and ambient pressure profiles
  for (let i = 0; i < timeS.length; i++) {
    const alt = Math.max(0, scenario.startAltitudeFt - descentRateFtS * timeS[i]);
    altitudeFt.push(alt);
    pAmbMmHg.push(altitudeToPressureMmHg(alt));
  }
  
  // Initialize middle ear pressure (equalized at start)
  pMeMmHg.push(pAmbMmHg[0]);
  eqRateSeries.push(0);
  tmDisp.push(0);
  
  let lastValsalvaTime = -1e9;
  const valsalvaActiveWindowS = 5.0;
  
  // Main simulation loop
  for (let i = 1; i < timeS.length; i++) {
    const dt = timeS[i] - timeS[i - 1];
    const deltaP = pMeMmHg[i - 1] - pAmbMmHg[i]; // Negative during descent
    
    // Valsalva scheduling
    let valsalvaBoost = 0.0;
    if (scenario.enableValsalva) {
      if ((timeS[i] - lastValsalvaTime) >= scenario.valsalvaIntervalS) {
        lastValsalvaTime = timeS[i];
      }
      if ((timeS[i] - lastValsalvaTime) <= valsalvaActiveWindowS) {
        valsalvaBoost = 3.0; // 4× speed during active Valsalva
      }
    }
    
    // ET lock condition dramatically reduces equalization
    const locked = Math.abs(deltaP) > (ET_LOCK_THRESHOLD / (1.0 + riskFactor));
    const lockPenalty = locked ? 0.15 : 1.0;
    
    // Calculate equalization speed
    const speed = equalizationSpeedMmHgS(
      dysfunction,
      riskFactor,
      deltaP,
      valsalvaBoost
    ) * lockPenalty;
    
    // Move P_ME toward P_amb by at most `speed × dt`
    const correction = Math.min(Math.max(pAmbMmHg[i] - pMeMmHg[i - 1], -speed * dt), speed * dt);
    pMeMmHg.push(pMeMmHg[i - 1] + correction);
    eqRateSeries.push(speed);
    tmDisp.push(tmDisplacementMl(pMeMmHg[i] - pAmbMmHg[i]));
  }
  
  // Calculate pressure differential array
  const deltaPMmHg: number[] = [];
  for (let i = 0; i < timeS.length; i++) {
    deltaPMmHg.push(pMeMmHg[i] - pAmbMmHg[i]);
  }
  
  // Calculate metrics
  const maxAbsDeltaP = Math.max(...deltaPMmHg.map(Math.abs));
  const meanAbsDeltaP = deltaPMmHg.reduce((sum, dp) => sum + Math.abs(dp), 0) / deltaPMmHg.length;
  
  const timeAboveLock = deltaPMmHg.filter(dp => Math.abs(dp) > ET_LOCK_THRESHOLD).length / deltaPMmHg.length;
  const timeAboveRupture = deltaPMmHg.filter(dp => Math.abs(dp) > MEMBRANE_RUPTURE_THRESHOLD).length / deltaPMmHg.length;
  const meanEqSpeed = eqRateSeries.reduce((sum, r) => sum + r, 0) / eqRateSeries.length;
  
  // Calculate risk score
  // Component 1: Peak ΔP (soft cap at rupture threshold)
  const peakComponent = Math.min(maxAbsDeltaP / MEMBRANE_RUPTURE_THRESHOLD, 1.0);
  // Component 2: Time above ET lock
  const lockComponent = Math.min(timeAboveLock * 2.0, 1.0);
  // Component 3: Descent risk factor
  const descentComponent = riskFactor;
  // Mitigation: Equalization speed (higher is better)
  const mitigation = Math.min(meanEqSpeed / 2.0, 1.0);
  
  const rawScore = 0.45 * peakComponent + 0.30 * lockComponent + 0.25 * descentComponent;
  const riskScore = Math.min(Math.max(rawScore * (1.0 - 0.5 * mitigation), 0.0), 1.0);
  const riskCategory = categorizeRisk(riskScore);
  
  const metrics: SimulationMetrics = {
    maxAbsDeltaPMmHg: maxAbsDeltaP,
    meanAbsDeltaPMmHg: meanAbsDeltaP,
    fractionTimeAboveLock: timeAboveLock,
    fractionTimeAboveRupture: timeAboveRupture,
    meanEqualizationSpeedMmHgS: meanEqSpeed,
    descentRiskFactor: descentComponent,
    timeAtETLock: timeAboveLock * totalSeconds,
    peakTMDisplacementMl: Math.max(...tmDisp.map(Math.abs)),
  };
  
  return {
    timeS,
    altitudeFt,
    pAmbMmHg,
    pMeMmHg,
    deltaPMmHg,
    tmDisplacementMl: tmDisp,
    equalizationRateMmHgS: eqRateSeries,
    riskScore,
    riskCategory,
    metrics,
  };
}

// ============================================================================
// Analysis Functions
// ============================================================================

/**
 * Generate risk vs descent rate sensitivity analysis
 */
export function riskVsDescentRate(
  scenario: ChamberScenario,
  rates: number[]
): SensitivityPoint[] {
  const results: SensitivityPoint[] = [];
  
  for (const rate of rates) {
    const testScenario: ChamberScenario = {
      ...scenario,
      descentRateFtMin: rate,
    };
    
    const result = simulateDescent(testScenario);
    results.push({
      parameterValue: rate,
      riskScore: result.riskScore,
      maxDeltaP: result.metrics.maxAbsDeltaPMmHg,
    });
  }
  
  return results;
}

/**
 * Generate risk heatmap data for ET severity × descent rate
 */
export function generateRiskHeatmap(
  baseScenario: ChamberScenario,
  rates: number[]
): HeatmapData {
  const severities: ETSeverity[] = ['mild', 'moderate', 'severe'];
  const values: number[][] = [];
  
  for (const severity of severities) {
    const row: number[] = [];
    for (const rate of rates) {
      const testScenario: ChamberScenario = {
        ...baseScenario,
        etSeverity: severity,
        descentRateFtMin: rate,
      };
      
      const result = simulateDescent(testScenario);
      row.push(result.riskScore);
    }
    values.push(row);
  }
  
  return {
    xLabels: rates,
    yLabels: severities.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
    values,
  };
}

/**
 * Generate 3D risk surface data
 */
export function generateRiskSurface(
  baseScenario: ChamberScenario,
  etRange: number[],
  rateRange: number[]
): { x: number[]; y: number[]; z: number[][] } {
  const z: number[][] = [];
  
  for (const rate of rateRange) {
    const row: number[] = [];
    for (const et of etRange) {
      // Map ET value to severity
      let severity: ETSeverity;
      if (et < 0.35) severity = 'mild';
      else if (et < 0.60) severity = 'moderate';
      else severity = 'severe';
      
      const testScenario: ChamberScenario = {
        ...baseScenario,
        etSeverity: severity,
        descentRateFtMin: rate,
      };
      
      const result = simulateDescent(testScenario);
      row.push(result.riskScore);
    }
    z.push(row);
  }
  
  return { x: etRange, y: rateRange, z };
}

/**
 * Default scenario configuration
 */
export function createDefaultScenario(): ChamberScenario {
  return {
    startAltitudeFt: 25000,
    descentRateFtMin: 3000,
    etSeverity: 'moderate',
    enableValsalva: true,
    valsalvaIntervalS: 60,
    tympanumVolumeMl: 1.0,
    mastoidVolumeMl: 7.75,
  };
}
