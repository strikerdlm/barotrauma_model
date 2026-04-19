/**
 * MedicationPicker — compact select for `MedicationEffect`. Labels are
 * medication-agnostic; the underlying pharmacology modifier is applied
 * server-side by `barotrauma.v2.pathophysiology`.
 */

import { Pill } from 'lucide-react';
import { MEDICATION_LABELS, type MedicationEffect } from '../../types/v2';

interface MedicationPickerProps {
  value: MedicationEffect;
  onChange: (next: MedicationEffect) => void;
}

const ORDER: MedicationEffect[] = [
  'none',
  'pseudoephedrine_oral',
  'oxymetazoline_topical',
  'intranasal_steroid',
  'antihistamine_spray',
];

export function MedicationPicker({ value, onChange }: MedicationPickerProps) {
  return (
    <div className="space-y-2">
      <span className="flex items-center gap-2 text-sm font-medium text-gray-300">
        <Pill size={14} className="text-primary-400" />
        Medication (pre-exposure)
      </span>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value as MedicationEffect)}
          className="
            w-full appearance-none
            bg-dark-200/60 border border-white/10 rounded-xl
            px-3 py-2 pr-9 text-sm text-gray-100
            hover:border-primary-500/40
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400/70
          "
        >
          {ORDER.map((key) => (
            <option key={key} value={key} className="bg-dark-200 text-gray-100">
              {MEDICATION_LABELS[key]}
            </option>
          ))}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-500">
          ▾
        </span>
      </div>
      <p className="text-xs text-gray-500">
        Oral pseudoephedrine RR 0.90 (healthy) / 1.40 (PET). Moayedi 2025
        HBOT RCT softened the preventive signal.
      </p>
    </div>
  );
}

export default MedicationPicker;
