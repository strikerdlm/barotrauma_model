/**
 * SimulateControls — run button + simulation options (dt, with_ci,
 * ci_n_samples, gas_exchange_full, rng_seed). Collapsed options panel
 * reduces visual weight since defaults are sensible.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Loader2, Play, Sparkles } from 'lucide-react';

import type { SimulateOptions } from '../../types/v2';

interface SimulateControlsProps {
  options: SimulateOptions;
  onOptionsChange: (next: SimulateOptions) => void;
  onRun: () => void;
  running: boolean;
  error: string | null;
}

export function SimulateControls({
  options,
  onOptionsChange,
  onRun,
  running,
  error,
}: SimulateControlsProps) {
  const [expanded, setExpanded] = useState(false);

  const set = <K extends keyof SimulateOptions>(
    key: K,
    value: SimulateOptions[K],
  ) => onOptionsChange({ ...options, [key]: value });

  return (
    <section className="card space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onRun}
          disabled={running}
          className="btn-primary inline-flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {running ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Play size={16} />
          )}
          {running ? 'Simulating…' : 'Run simulation'}
        </button>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="btn-secondary inline-flex items-center gap-2 !px-4 !py-2"
          aria-expanded={expanded}
        >
          <Sparkles size={14} />
          Options
          <ChevronDown
            size={14}
            className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="options"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="grid gap-4 sm:grid-cols-2 pt-2 pb-1">
              <label className="flex items-center justify-between gap-3 text-sm text-gray-300">
                <span>Monte-Carlo CIs</span>
                <input
                  type="checkbox"
                  checked={options.with_ci ?? false}
                  onChange={(e) => set('with_ci', e.target.checked)}
                  className="h-4 w-4 rounded accent-primary-500"
                />
              </label>
              <label className="flex items-center justify-between gap-3 text-sm text-gray-300">
                <span>Full gas exchange (Doyle 2017)</span>
                <input
                  type="checkbox"
                  checked={options.gas_exchange_full ?? false}
                  onChange={(e) =>
                    set('gas_exchange_full', e.target.checked)
                  }
                  className="h-4 w-4 rounded accent-primary-500"
                />
              </label>
              <label className="flex items-center justify-between gap-3 text-sm text-gray-300">
                <span>
                  dt <span className="text-gray-500 font-mono">(s)</span>
                </span>
                <input
                  type="number"
                  min={0.01}
                  max={1.0}
                  step={0.05}
                  value={options.dt_s ?? 0.1}
                  onChange={(e) =>
                    set('dt_s', parseFloat(e.target.value) || 0.1)
                  }
                  className="w-20 bg-dark-200/60 border border-white/10 rounded-lg px-2 py-1 text-right font-mono text-xs text-gray-100"
                />
              </label>
              <label className="flex items-center justify-between gap-3 text-sm text-gray-300">
                <span>MC samples</span>
                <input
                  type="number"
                  min={10}
                  max={2000}
                  step={50}
                  disabled={!options.with_ci}
                  value={options.ci_n_samples ?? 200}
                  onChange={(e) =>
                    set('ci_n_samples', parseInt(e.target.value, 10) || 200)
                  }
                  className="w-20 bg-dark-200/60 border border-white/10 rounded-lg px-2 py-1 text-right font-mono text-xs text-gray-100 disabled:opacity-50"
                />
              </label>
              <label className="sm:col-span-2 flex items-center justify-between gap-3 text-sm text-gray-300">
                <span>
                  RNG seed{' '}
                  <span className="text-gray-500">(blank = random)</span>
                </span>
                <input
                  type="number"
                  value={options.rng_seed ?? ''}
                  onChange={(e) => {
                    const raw = e.target.value.trim();
                    set('rng_seed', raw === '' ? null : parseInt(raw, 10));
                  }}
                  className="w-28 bg-dark-200/60 border border-white/10 rounded-lg px-2 py-1 text-right font-mono text-xs text-gray-100"
                />
              </label>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <p className="text-xs text-risk-high border border-risk-high/30 bg-risk-high/10 rounded-lg px-3 py-2">
          {error}
        </p>
      )}
    </section>
  );
}

export default SimulateControls;
