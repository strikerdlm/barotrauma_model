/**
 * ClinicalDecisionSupport — plain-language summary panel: risk category
 * badge, dominant_risk_factor, recommended_max_descent_ft_min, pipeline
 * notes. Consumes ``RiskResultV2`` from the v2 API.
 */

import { AlertTriangle, Gauge, Info, Stethoscope } from 'lucide-react';
import type { RiskResultV2, RiskCategoryV2 } from '../../types/v2';
import { RISK_CATEGORY_LABELS } from '../../types/v2';

interface ClinicalDecisionSupportProps {
  risk: RiskResultV2 | null;
  notes: string[];
  loading?: boolean;
}

const BADGE_CLASS: Record<RiskCategoryV2, string> = {
  low: 'badge badge-low',
  moderate: 'badge badge-moderate',
  high: 'badge badge-high',
  very_high: 'badge badge-high !bg-risk-high/30',
};

const ADVICE: Record<RiskCategoryV2, string> = {
  low:
    'Baseline exposure. Proceed per standard protocol. No specific MEB ' +
    'mitigation beyond routine equalization and pre-flight ENT screen.',
  moderate:
    'Elevated exposure. Consider reducing descent rate to the recommended ' +
    'maximum and reinforce active equalization training. Re-screen ENT if ' +
    'symptomatic.',
  high:
    'High exposure. Reduce descent rate and consider postponement if acute ' +
    'URI or PET instability is contributing. Escalate to aeromedical review.',
  very_high:
    'Do not fly / do not expose. Clinical equivalents of ≥ Teed III+ are ' +
    'likely at current parameters. Clear acute URI/inflammation and re-' +
    'screen before reattempt.',
};

export function ClinicalDecisionSupport({
  risk,
  notes,
  loading = false,
}: ClinicalDecisionSupportProps) {
  if (!risk && !loading) {
    return (
      <section className="card space-y-2">
        <header className="flex items-center gap-2">
          <Stethoscope size={16} className="text-primary-400" />
          <h2 className="section-title !mb-0">Clinical decision support</h2>
        </header>
        <p className="text-xs text-gray-500 italic">
          Run a simulation to populate the recommendation panel.
        </p>
      </section>
    );
  }

  const category: RiskCategoryV2 = risk?.risk_category ?? 'low';
  const advice = ADVICE[category];
  const recMaxDescent = risk?.recommended_max_descent_ft_min ?? null;
  const dominant = risk?.dominant_risk_factor ?? '—';
  const maxDp = risk?.max_abs_delta_p_mmHg ?? null;

  return (
    <section className="card space-y-5">
      <header className="flex items-center gap-2">
        <Stethoscope size={16} className="text-primary-400" />
        <h2 className="section-title !mb-0">Clinical decision support</h2>
      </header>

      <div className="flex flex-wrap items-center gap-2">
        <span className={BADGE_CLASS[category]}>
          Risk category: {RISK_CATEGORY_LABELS[category]}
        </span>
        {maxDp !== null && (
          <span className="badge bg-white/5 text-gray-300 border border-white/10">
            max |ΔP| {maxDp.toFixed(0)} mmHg
          </span>
        )}
      </div>

      <p className="text-sm text-gray-300 leading-relaxed">{advice}</p>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl border border-white/5 bg-dark-200/40 p-3">
          <p className="flex items-center gap-1.5 text-xs text-gray-500">
            <AlertTriangle size={12} className="text-primary-400" />
            Dominant risk factor
          </p>
          <p className="mt-1 text-sm font-medium text-gray-100 break-words">
            {dominant}
          </p>
        </div>
        <div className="rounded-xl border border-white/5 bg-dark-200/40 p-3">
          <p className="flex items-center gap-1.5 text-xs text-gray-500">
            <Gauge size={12} className="text-primary-400" />
            Max safe descent
          </p>
          <p className="mt-1 font-mono text-sm text-primary-400">
            {recMaxDescent !== null
              ? `${recMaxDescent.toLocaleString()} ft/min`
              : '—'}
          </p>
        </div>
      </div>

      {notes.length > 0 && (
        <div className="space-y-1.5">
          <p className="flex items-center gap-1.5 text-xs text-gray-500">
            <Info size={12} />
            Pipeline modifiers applied
          </p>
          <ul className="space-y-1">
            {notes.map((n, i) => (
              <li
                key={i}
                className="rounded-lg bg-dark-200/40 border border-white/5 px-3 py-1.5 text-xs text-gray-300 font-mono"
              >
                {n}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default ClinicalDecisionSupport;
