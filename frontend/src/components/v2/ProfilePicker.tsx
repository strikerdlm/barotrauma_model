/**
 * ProfilePicker — preset chamber-profile selector with inline segment
 * preview. Fetches ``/api/scenarios`` once on mount.
 */

import { useEffect, useState } from 'react';
import { Mountain, Clock } from 'lucide-react';

import { listScenarios } from '../../lib/v2api';
import type {
  ProfilePresetInfo,
  ProfilePresetKey,
} from '../../types/v2';

interface ProfilePickerProps {
  value: ProfilePresetKey;
  onChange: (next: ProfilePresetKey) => void;
}

export function ProfilePicker({ value, onChange }: ProfilePickerProps) {
  const [presets, setPresets] = useState<ProfilePresetInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listScenarios()
      .then(setPresets)
      .catch((e: Error) => setError(e.message));
  }, []);

  const current = presets.find((p) => p.key === value);

  return (
    <section className="card space-y-4">
      <header className="flex items-center gap-3">
        <span className="grid place-items-center w-9 h-9 rounded-xl bg-primary-500/15 text-primary-400">
          <Mountain size={18} />
        </span>
        <div>
          <h2 className="section-title !mb-0">Chamber profile</h2>
          <p className="text-xs text-gray-500">
            Pre-calibrated presets from ``barotrauma.v2.scenarios``.
          </p>
        </div>
      </header>

      {error && (
        <p className="text-xs text-risk-high border border-risk-high/30 bg-risk-high/10 rounded-lg px-3 py-2">
          Failed to load presets: {error}
        </p>
      )}

      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value as ProfilePresetKey)}
          className="
            w-full appearance-none
            bg-dark-200/60 border border-white/10 rounded-xl
            px-3 py-2.5 pr-9 text-sm text-gray-100
            hover:border-primary-500/40
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400/70
          "
        >
          {presets.length === 0 && (
            <option value={value} className="bg-dark-200">
              Loading presets…
            </option>
          )}
          {presets.map((p) => (
            <option key={p.key} value={p.key} className="bg-dark-200 text-gray-100">
              {p.name}
            </option>
          ))}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-500">
          ▾
        </span>
      </div>

      {current && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-1.5">
              <Mountain size={12} />
              start {current.start_altitude_ft.toLocaleString()} ft
            </span>
            <span className="flex items-center gap-1.5">
              <Clock size={12} />
              {(current.total_duration_s / 60).toFixed(1)} min total
            </span>
          </div>
          <ul className="divide-y divide-white/5 rounded-xl border border-white/5 bg-dark-200/40">
            {current.segments.map((seg, i) => (
              <li
                key={i}
                className="flex items-center justify-between gap-3 px-3 py-2 text-xs"
              >
                <span className="truncate text-gray-300">
                  {seg.label || `segment ${i + 1}`}
                </span>
                <span className="font-mono text-gray-500 shrink-0">
                  {seg.duration_s}s → {seg.end_altitude_ft.toLocaleString()} ft
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default ProfilePicker;
