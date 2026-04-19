/**
 * v2 API types — mirror of ``barotrauma.v2`` dataclasses as exposed by
 * the FastAPI sidecar in ``api/schemas.py``. Keep in sync.
 *
 * Source of truth: the Python engine. These TS types exist only so the
 * dashboard can type requests and responses — do not re-implement the
 * physics here.
 */

// --------------------------------------------------------------- enums
export type UriState =
  | 'none'
  | 'day_1_3'
  | 'day_4_7'
  | 'day_8_14'
  | 'day_15_21'
  | 'day_22_28';

export type PetState = 'normal' | 's1' | 's2' | 's3' | 's4';

export type EtSeverityV2 = 'normal' | 'mild' | 'moderate' | 'severe';

export type ChronicRhinitis = 'none' | 'allergic' | 'chronic_rhinosinusitis';

export type MedicationEffect =
  | 'none'
  | 'pseudoephedrine_oral'
  | 'oxymetazoline_topical'
  | 'intranasal_steroid'
  | 'antihistamine_spray';

export type RiskCategoryV2 = 'low' | 'moderate' | 'high' | 'very_high';

export type Sex = 'male' | 'female' | 'unspecified';

// ------------------------------------------------------ patient state
export interface PatientAnatomyV2 {
  tympanum_volume_ml: number;
  mastoid_volume_ml: number;
  tm_area_cm2: number;
  tm_stiffness_mmHg_per_ml: number;
  tm_max_displacement_ml: number;
  age_years: number;
  sex: Sex;
}

export interface EtFunctionV2 {
  severity: EtSeverityV2;
  passive_opening_mmHg_me: number;
  passive_opening_mmHg_np: number;
  closing_mmHg: number;
  active_resistance_mmHg_ml_min: number;
  active_open_duration_s: number;
  swallow_freq_per_hr_cruise: number;
  swallow_freq_per_hr_descent: number;
  fge_controls: number;
}

export interface PatientStateV2 {
  anatomy: PatientAnatomyV2;
  et: EtFunctionV2;
  uri: UriState;
  pet: PetState;
  rhinitis: ChronicRhinitis;
  previous_meb: boolean;
  medication: MedicationEffect;
  enable_valsalva: boolean;
  valsalva_interval_s: number;
  habitual_sniffer: boolean;
  // v2.3.0 categorical covariates
  sensory_neuropathy: boolean;
  impaired_volitional_equalization: boolean;
  glp1_exposure: boolean;
  bdet_treated: boolean;
}

/**
 * Partial patient state — everything optional so the UI can build a
 * request incrementally without having to re-send unchanged defaults.
 * The backend fills missing fields from the same defaults as the v2
 * Python dataclasses.
 */
export type PatientStateInput = {
  anatomy?: Partial<PatientAnatomyV2>;
  et?: Partial<EtFunctionV2>;
  uri?: UriState;
  pet?: PetState;
  rhinitis?: ChronicRhinitis;
  previous_meb?: boolean;
  medication?: MedicationEffect;
  enable_valsalva?: boolean;
  valsalva_interval_s?: number;
  habitual_sniffer?: boolean;
  // v2.3.0 categorical covariates
  sensory_neuropathy?: boolean;
  impaired_volitional_equalization?: boolean;
  glp1_exposure?: boolean;
  bdet_treated?: boolean;
};

// --------------------------------------------------- chamber profile
export interface ChamberSegmentV2 {
  duration_s: number;
  end_altitude_ft: number;
  label?: string;
}

export interface ChamberProfileCustom {
  preset?: never;
  name: string;
  start_altitude_ft: number;
  segments: ChamberSegmentV2[];
}

export interface ChamberProfilePreset {
  preset: ProfilePresetKey;
  name?: never;
  start_altitude_ft?: never;
  segments?: never;
}

export type ChamberProfileInput = ChamberProfilePreset | ChamberProfileCustom;

export type ProfilePresetKey =
  | 'usafsam_type_i'
  | 'usafsam_type_ii_rd'
  | 'israeli_af_post_2022'
  | 'italian_af_25k'
  | 'italian_af_35k'
  | 'fac_bogota_default'
  | 'commercial_cabin_descent'
  | 'rapid_descent_10k'
  | 'slow_descent_1k'
  | 'groth_1986';

export interface ProfilePresetInfo {
  key: ProfilePresetKey;
  name: string;
  start_altitude_ft: number;
  total_duration_s: number;
  segments: ChamberSegmentV2[];
}

// ------------------------------------------------------ simulate I/O
export interface SimulateOptions {
  dt_s?: number;
  rng_seed?: number | null;
  gas_exchange_full?: boolean;
  with_ci?: boolean;
  ci_n_samples?: number;
}

export interface SimulateRequest {
  patient?: PatientStateInput;
  profile: ChamberProfileInput;
  options?: SimulateOptions;
}

export interface SimulationTraceV2 {
  t_s: number[];
  altitude_ft: number[];
  p_ambient_mmHg: number[];
  p_me_mmHg: number[];
  delta_p_mmHg: number[];
  tm_displacement_ml: number[];
  et_open: boolean[];
  swallow_events_s: number[];
  valsalva_events_s: number[];
}

export interface RiskResultV2 {
  p_barotitis: number;
  p_baromyringitis: number;
  p_rupture: number;
  max_abs_delta_p_mmHg: number;
  auc_mmHg_s_barotitis: number;
  auc_mmHg_s_baromyringitis: number;
  dominant_risk_factor: string;
  recommended_max_descent_ft_min: number;
  risk_category: RiskCategoryV2;
  ci95_barotitis: [number, number] | null;
  ci95_baromyringitis: [number, number] | null;
  ci95_rupture: [number, number] | null;
}

export interface SimulateResponse {
  trace: SimulationTraceV2;
  risk: RiskResultV2;
  notes: string[];
  profile_name: string;
  total_duration_s: number;
}

// --------------------------------------------------------- human labels
/** Human-readable labels for UI widgets. */
export const URI_LABELS: Record<UriState, string> = {
  none: 'None',
  day_1_3: 'URI day 1–3 (onset)',
  day_4_7: 'URI day 4–7 (peak dysfunction)',
  day_8_14: 'URI day 8–14 (resolving)',
  day_15_21: 'URI day 15–21 (late recovery)',
  day_22_28: 'URI day 22–28 (near-baseline)',
};

export const PET_LABELS: Record<PetState, string> = {
  normal: 'Normal',
  s1: 'S1 — Baseline patent (dry mucosa)',
  s2: 'S2 — PET + URI/inflammation',
  s3: 'S3 — Habitual sniffer',
  s4: 'S4 — Post-plug / cartilage augmentation',
};

export const RHINITIS_LABELS: Record<ChronicRhinitis, string> = {
  none: 'None',
  allergic: 'Allergic rhinitis',
  chronic_rhinosinusitis: 'Chronic rhinosinusitis',
};

export const MEDICATION_LABELS: Record<MedicationEffect, string> = {
  none: 'None',
  pseudoephedrine_oral: 'Pseudoephedrine (oral)',
  oxymetazoline_topical: 'Oxymetazoline (topical)',
  intranasal_steroid: 'Intranasal steroid',
  antihistamine_spray: 'Antihistamine (nasal spray)',
};

export const SEVERITY_LABELS: Record<EtSeverityV2, string> = {
  normal: 'Normal',
  mild: 'Mild',
  moderate: 'Moderate',
  severe: 'Severe',
};

export const RISK_CATEGORY_LABELS: Record<RiskCategoryV2, string> = {
  low: 'Low',
  moderate: 'Moderate',
  high: 'High',
  very_high: 'Very high',
};
