/**
 * SegmentedPicker — accessible radiogroup for bounded enum state
 * (URI 6-state, PET 5-state, Severity 4-state, Rhinitis 3-state).
 *
 * Reuses the TabGroup visual language (layoutId active indicator via
 * framer-motion) but denser and optionally two-line per option.
 */

import { motion } from 'framer-motion';
import { useId } from 'react';

export interface SegmentedOption<T extends string> {
  value: T;
  label: string;
  sublabel?: string;
}

interface SegmentedPickerProps<T extends string> {
  label: string;
  description?: string;
  options: readonly SegmentedOption<T>[];
  value: T;
  onChange: (next: T) => void;
  /** Fold options into multiple rows on narrow layouts. */
  compact?: boolean;
}

export function SegmentedPicker<T extends string>({
  label,
  description,
  options,
  value,
  onChange,
  compact = false,
}: SegmentedPickerProps<T>) {
  const groupId = useId();
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-medium text-gray-300">{label}</span>
        {description && (
          <span className="text-xs text-gray-500">{description}</span>
        )}
      </div>
      <div
        role="radiogroup"
        aria-label={label}
        className={
          compact
            ? 'grid grid-cols-2 gap-1 p-1 bg-dark-200/60 rounded-xl border border-white/5 backdrop-blur-sm'
            : 'flex flex-wrap gap-1 p-1 bg-dark-200/60 rounded-xl border border-white/5 backdrop-blur-sm'
        }
      >
        {options.map((opt) => {
          const active = opt.value === value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => onChange(opt.value)}
              className={`
                relative flex-1 min-w-0 rounded-lg px-3 py-2 text-left
                transition-colors duration-200
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400/70
                ${active ? 'text-white' : 'text-gray-400 hover:text-gray-200'}
              `}
            >
              {active && (
                <motion.div
                  layoutId={`segmented-active-${groupId}`}
                  className="absolute inset-0 bg-primary-500/20 border border-primary-500/40 rounded-lg"
                  transition={{ type: 'spring', bounce: 0.18, duration: 0.45 }}
                />
              )}
              <span className="relative block text-sm font-medium truncate">
                {opt.label}
              </span>
              {opt.sublabel && (
                <span className="relative block text-[10px] text-gray-500 truncate">
                  {opt.sublabel}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default SegmentedPicker;
