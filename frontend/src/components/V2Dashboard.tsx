/**
 * V2Dashboard — composes the Python-backed v2 simulator into a working
 * clinical-decision-support page. State lives in ``useSimulation``; the
 * physics never leaves ``barotrauma.v2`` on the Python side.
 *
 * Layout: full-width two-column grid on ≥lg, stacked on narrow screens.
 *  - Left column: patient + profile editors (tall).
 *  - Right column: simulate controls + CDS panel + probability trio.
 */

import { motion } from 'framer-motion';
import { Activity, ExternalLink, Gauge } from 'lucide-react';

import { ClinicalDecisionSupport } from './v2/ClinicalDecisionSupport';
import { PatientBuilder } from './v2/PatientBuilder';
import { ProbabilityTrio } from './v2/ProbabilityTrio';
import { ProfilePicker } from './v2/ProfilePicker';
import { SimulateControls } from './v2/SimulateControls';
import { TrajectoryChart } from './v2/TrajectoryChart';
import { useSimulation } from '../lib/useSimulation';

interface V2DashboardProps {
  onShowLegacy?: () => void;
}

export function V2Dashboard({ onShowLegacy }: V2DashboardProps) {
  const {
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
  } = useSimulation();

  const maxDp = result?.risk.max_abs_delta_p_mmHg ?? null;
  const peakTm = result
    ? result.trace.tm_displacement_ml.reduce(
        (m, v) => Math.max(m, Math.abs(v)),
        0,
      )
    : null;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 backdrop-blur-md bg-dark-300/80 border-b border-white/5">
        <div className="max-w-[1800px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', bounce: 0.5 }}
              className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-500 grid place-items-center shadow-lg shadow-primary-500/30"
            >
              <Activity className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-display font-bold text-white">
                Barotrauma Risk Assessment — v2
              </h1>
              <p className="text-sm text-gray-400">
                Kanick-Doyle + URI/PET state machine · Python-backed,
                single source of truth
              </p>
            </div>
          </div>

          {onShowLegacy && (
            <button
              type="button"
              onClick={onShowLegacy}
              className="btn-secondary inline-flex items-center gap-2"
            >
              <ExternalLink size={14} />
              View v1 legacy
            </button>
          )}
        </div>
      </header>

      <main className="max-w-[1800px] mx-auto px-6 py-6 space-y-6">
        {/* Summary metrics strip */}
        <section className="grid gap-3 grid-cols-2 lg:grid-cols-4">
          <SummaryTile
            label="Risk category"
            value={
              result?.risk.risk_category
                ? result.risk.risk_category.replace('_', ' ')
                : '—'
            }
          />
          <SummaryTile
            label="p_barotitis"
            value={
              result ? `${(result.risk.p_barotitis * 100).toFixed(1)}%` : '—'
            }
            accent
          />
          <SummaryTile
            label="max |ΔP|"
            value={maxDp !== null ? `${maxDp.toFixed(0)} mmHg` : '—'}
          />
          <SummaryTile
            label="peak TM disp."
            value={peakTm !== null ? `${(peakTm * 1000).toFixed(1)} µL` : '—'}
          />
        </section>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <div className="space-y-6">
            <PatientBuilder patient={patient} onChange={setPatient} />
            <ProfilePicker value={preset} onChange={setPreset} />
          </div>
          <div className="space-y-6">
            <SimulateControls
              options={options}
              onOptionsChange={setOptions}
              onRun={run}
              running={running}
              error={error}
            />
            <ProbabilityTrio risk={result?.risk ?? null} loading={running} />
            <ClinicalDecisionSupport
              risk={result?.risk ?? null}
              notes={result?.notes ?? []}
              loading={running}
            />
          </div>
        </div>

        <TrajectoryChart trace={result?.trace ?? null} loading={running} />

        <footer className="pt-4 pb-8 text-center text-xs text-gray-500">
          <p className="inline-flex items-center gap-1">
            <Gauge size={12} />
            Physics engine: <code className="font-mono">barotrauma.v2</code>{' '}
            · API: <code className="font-mono">FastAPI /api/simulate</code>
          </p>
          <p className="mt-1">
            Calibrated to the Colombian Aerospace Force 10-year cohort;
            externally validated against three Italian Air Force cohorts
            (Morgagni 2010/2012, Landolfi 2009).
          </p>
        </footer>
      </main>
    </div>
  );
}

function SummaryTile({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <p
        className={`mt-1.5 font-mono text-xl font-semibold ${
          accent ? 'text-primary-400' : 'text-white'
        }`}
      >
        {value}
      </p>
    </div>
  );
}

export default V2Dashboard;
