/**
 * ToggleRow — accessible switch for boolean patient-state fields
 * (habitual_sniffer, previous_meb, enable_valsalva).
 */

import { motion } from 'framer-motion';
import { useId } from 'react';

interface ToggleRowProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}

export function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: ToggleRowProps) {
  const id = useId();
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-labelledby={`${id}-label`}
      aria-describedby={description ? `${id}-desc` : undefined}
      onClick={() => onChange(!checked)}
      className="
        w-full flex items-start justify-between gap-3
        rounded-xl border border-white/5 bg-dark-200/40
        px-3 py-2.5 text-left
        transition-colors duration-200
        hover:border-primary-500/30
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400/70
      "
    >
      <span className="min-w-0">
        <span
          id={`${id}-label`}
          className="block text-sm font-medium text-gray-200"
        >
          {label}
        </span>
        {description && (
          <span id={`${id}-desc`} className="block text-xs text-gray-500 mt-0.5">
            {description}
          </span>
        )}
      </span>
      <span
        className={`
          relative shrink-0 mt-0.5 h-5 w-9 rounded-full
          transition-colors duration-200
          ${checked ? 'bg-primary-500/80' : 'bg-dark-100 border border-white/10'}
        `}
      >
        <motion.span
          layout
          transition={{ type: 'spring', bounce: 0.25, duration: 0.35 }}
          className={`
            absolute top-0.5 h-4 w-4 rounded-full bg-white shadow-lg
            ${checked ? 'left-[18px]' : 'left-0.5'}
          `}
        />
      </span>
    </button>
  );
}

export default ToggleRow;
