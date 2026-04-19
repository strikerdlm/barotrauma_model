/**
 * PatientBuilder — composes the full v2 PatientState editor. Controlled
 * component: parent holds state via ``useSimulation``. Layout is two
 * columns on wide screens (≥1024 px), single column below.
 */

import { User, Activity, Droplets, Waves } from 'lucide-react';

import { SegmentedPicker, type SegmentedOption } from './SegmentedPicker';
import { MedicationPicker } from './MedicationPicker';
import { ToggleRow } from './ToggleRow';
import { AnatomyBuilder } from './AnatomyBuilder';

import type {
  PatientStateV2,
  UriState,
  PetState,
  EtSeverityV2,
  ChronicRhinitis,
} from '../../types/v2';

const URI_OPTIONS: readonly SegmentedOption<UriState>[] = [
  { value: 'none', label: 'No URI', sublabel: 'healthy baseline' },
  { value: 'day_1_3', label: 'Day 1–3', sublabel: 'URI onset' },
  { value: 'day_4_7', label: 'Day 4–7', sublabel: 'peak dysfunction' },
  { value: 'day_8_14', label: 'Day 8–14', sublabel: 'resolving' },
  { value: 'day_15_21', label: 'Day 15–21', sublabel: 'late recovery' },
  { value: 'day_22_28', label: 'Day 22–28', sublabel: 'near-baseline' },
];

const PET_OPTIONS: readonly SegmentedOption<PetState>[] = [
  { value: 'normal', label: 'Normal' },
  { value: 's1', label: 'S1', sublabel: 'patent, dry' },
  { value: 's2', label: 'S2', sublabel: 'PET + URI' },
  { value: 's3', label: 'S3', sublabel: 'sniffer' },
  { value: 's4', label: 'S4', sublabel: 'post-plug' },
];

const SEVERITY_OPTIONS: readonly SegmentedOption<EtSeverityV2>[] = [
  { value: 'normal', label: 'Normal' },
  { value: 'mild', label: 'Mild' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'severe', label: 'Severe' },
];

const RHINITIS_OPTIONS: readonly SegmentedOption<ChronicRhinitis>[] = [
  { value: 'none', label: 'None' },
  { value: 'allergic', label: 'Allergic' },
  { value: 'chronic_rhinosinusitis', label: 'CRS' },
];

interface PatientBuilderProps {
  patient: PatientStateV2;
  onChange: (next: PatientStateV2) => void;
}

export function PatientBuilder({ patient, onChange }: PatientBuilderProps) {
  const set = <K extends keyof PatientStateV2>(
    key: K,
    value: PatientStateV2[K],
  ) => onChange({ ...patient, [key]: value });

  const setEtSeverity = (severity: EtSeverityV2) =>
    onChange({ ...patient, et: { ...patient.et, severity } });

  return (
    <section className="card space-y-6">
      <header className="flex items-center gap-3">
        <span className="grid place-items-center w-9 h-9 rounded-xl bg-primary-500/15 text-primary-400">
          <User size={18} />
        </span>
        <div>
          <h2 className="section-title !mb-0">Patient</h2>
          <p className="text-xs text-gray-500">
            URI × PET × rhinitis × medication × anatomy. All fields have
            v2 defaults — edit only what you want to vary.
          </p>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-4">
          <SegmentedPicker
            label="Acute URI state"
            description="Buchman 1994 / Doyle 1999 rhinovirus-challenge windows"
            options={URI_OPTIONS}
            value={patient.uri}
            onChange={(v) => set('uri', v)}
            compact
          />
          <SegmentedPicker
            label="Patulous ET state"
            description="Ikeda 2020, Shindo 2025, Oshima 2025"
            options={PET_OPTIONS}
            value={patient.pet}
            onChange={(v) => set('pet', v)}
          />
          <SegmentedPicker
            label="Obstructive ET severity"
            description="Kanick-Doyle 2005 R_A scale"
            options={SEVERITY_OPTIONS}
            value={patient.et.severity}
            onChange={setEtSeverity}
          />
          <SegmentedPicker
            label="Chronic rhinitis"
            description="Chen 2022 meta-analysis"
            options={RHINITIS_OPTIONS}
            value={patient.rhinitis}
            onChange={(v) => set('rhinitis', v)}
          />
          <MedicationPicker
            value={patient.medication}
            onChange={(v) => set('medication', v)}
          />
        </div>

        <div className="space-y-4">
          <div className="space-y-3">
            <span className="flex items-center gap-2 text-sm font-medium text-gray-300">
              <Activity size={14} className="text-primary-400" />
              Anatomy
            </span>
            <AnatomyBuilder
              value={patient.anatomy}
              onChange={(v) => set('anatomy', v)}
            />
          </div>

          <div className="space-y-2">
            <span className="flex items-center gap-2 text-sm font-medium text-gray-300">
              <Waves size={14} className="text-primary-400" />
              Behavior &amp; history
            </span>
            <ToggleRow
              label="Enable Valsalva during descent"
              description="Scheduled pulse every valsalva_interval_s. Trained aircrew default = on."
              checked={patient.enable_valsalva}
              onChange={(v) => set('enable_valsalva', v)}
            />
            <ToggleRow
              label="Habitual sniffer"
              description="Oshima 2025: sniffing OR 8.18 for PET; feeds into PET-S3 RR."
              checked={patient.habitual_sniffer}
              onChange={(v) => set('habitual_sniffer', v)}
            />
            <ToggleRow
              label="Previous MEB"
              description="Historic Teed I+ event. Amplifies per-descent RR."
              checked={patient.previous_meb}
              onChange={(v) => set('previous_meb', v)}
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Droplets size={12} />
            Allergic rhinitis + URI day 4–7 is the classic pre-flight
            exclusion pattern.
          </div>
        </div>
      </div>
    </section>
  );
}

export default PatientBuilder;
