/**
 * ``useSimulation`` — local state hook for the v2 patient + profile +
 * options + latest simulation result. Calls ``/api/simulate`` via the
 * typed v2api client and tracks loading / error state.
 *
 * Deliberately not a global store; the Dashboard composes everything.
 * Lift to Zustand/Redux only if multiple disjoint pages need this state.
 */

import { useCallback, useState } from 'react';

import { simulate as simulateApi, ApiError } from './v2api';
import type {
  ChamberProfileInput,
  PatientStateV2,
  ProfilePresetKey,
  SimulateOptions,
  SimulateResponse,
} from '../types/v2';

export const DEFAULT_PRESET: ProfilePresetKey = 'fac_bogota_default';

export const DEFAULT_PATIENT: PatientStateV2 = {
  anatomy: {
    tympanum_volume_ml: 1.0,
    mastoid_volume_ml: 7.75,
    tm_area_cm2: 0.6,
    tm_stiffness_mmHg_per_ml: 179.0,
    tm_max_displacement_ml: 0.025,
    age_years: 30,
    sex: 'unspecified',
  },
  et: {
    severity: 'normal',
    passive_opening_mmHg_me: 25.7,
    passive_opening_mmHg_np: 44.1,
    closing_mmHg: 7.35,
    active_resistance_mmHg_ml_min: 2.0,
    active_open_duration_s: 0.25,
    swallow_freq_per_hr_cruise: 5.2,
    swallow_freq_per_hr_descent: 60.0,
    fge_controls: 0.32,
  },
  uri: 'none',
  pet: 'normal',
  rhinitis: 'none',
  previous_meb: false,
  medication: 'none',
  enable_valsalva: true,
  valsalva_interval_s: 60.0,
  habitual_sniffer: false,
  // v2.3.0 covariates (defaults preserve v2.2.1 behavior)
  sensory_neuropathy: false,
  impaired_volitional_equalization: false,
  glp1_exposure: false,
  bdet_treated: false,
};

export const DEFAULT_OPTIONS: SimulateOptions = {
  dt_s: 0.1,
  with_ci: false,
  ci_n_samples: 200,
  gas_exchange_full: false,
  rng_seed: 42,
};

export interface UseSimulationState {
  patient: PatientStateV2;
  setPatient: (p: PatientStateV2) => void;
  preset: ProfilePresetKey;
  setPreset: (p: ProfilePresetKey) => void;
  options: SimulateOptions;
  setOptions: (o: SimulateOptions) => void;
  result: SimulateResponse | null;
  error: string | null;
  running: boolean;
  run: () => Promise<void>;
}

export function useSimulation(): UseSimulationState {
  const [patient, setPatient] = useState<PatientStateV2>(DEFAULT_PATIENT);
  const [preset, setPreset] = useState<ProfilePresetKey>(DEFAULT_PRESET);
  const [options, setOptions] = useState<SimulateOptions>(DEFAULT_OPTIONS);
  const [result, setResult] = useState<SimulateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const run = useCallback(async () => {
    setRunning(true);
    setError(null);
    const profile: ChamberProfileInput = { preset };
    try {
      const res = await simulateApi({ patient, profile, options });
      setResult(res);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : `Unexpected error: ${(err as Error).message}`;
      setError(message);
    } finally {
      setRunning(false);
    }
  }, [patient, preset, options]);

  return {
    patient,
    setPatient,
    preset,
    setPreset,
    options,
    setOptions,
    result,
    error,
    running,
    run,
  };
}
