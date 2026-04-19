/**
 * ProbabilityTrio — horizontal bar display of the three v2 risk
 * outcomes (p_barotitis, p_baromyringitis, p_rupture) with optional
 * 95% CI whiskers from ``score_with_uncertainty``. Color-coded per
 * outcome severity: barotitis (green-ish amber), baromyringitis
 * (moderate amber), rupture (high red).
 */

import { motion } from 'framer-motion';
import type { RiskResultV2 } from '../../types/v2';

interface ProbabilityTrioProps {
  risk: RiskResultV2 | null;
  loading?: boolean;
}

type OutcomeKey = 'p_barotitis' | 'p_baromyringitis' | 'p_rupture';

interface OutcomeSpec {
  key: OutcomeKey;
  label: string;
  rule: string;
  threshold: string;
  tone: 'low' | 'moderate' | 'high';
  ciKey: 'ci95_barotitis' | 'ci95_baromyringitis' | 'ci95_rupture';
}

const OUTCOMES: readonly OutcomeSpec[] = [
  {
    key: 'p_barotitis',
    label: 'Barotitis (Teed I+)',
    rule: 'onset at |ΔP| ≳ 18 mmHg',
    threshold: 'most common clinical endpoint',
    tone: 'low',
    ciKey: 'ci95_barotitis',
  },
  {
    key: 'p_baromyringitis',
    label: 'Baromyringitis (Teed III–IV)',
    rule: 'hemorrhage at |ΔP| ≳ 96 mmHg',
    threshold: 'grounding-level severity',
    tone: 'moderate',
    ciKey: 'ci95_baromyringitis',
  },
  {
    key: 'p_rupture',
    label: 'TM rupture (Teed V)',
    rule: 'conservative threshold 150 mmHg',
    threshold: 'imminent perforation',
    tone: 'high',
    ciKey: 'ci95_rupture',
  },
];

const TONE_CLASS: Record<OutcomeSpec['tone'], string> = {
  low: 'bg-risk-low',
  moderate: 'bg-risk-moderate',
  high: 'bg-risk-high',
};

const TONE_TEXT: Record<OutcomeSpec['tone'], string> = {
  low: 'text-risk-low',
  moderate: 'text-risk-moderate',
  high: 'text-risk-high',
};

function formatPct(p: number): string {
  if (!Number.isFinite(p)) return '—';
  if (p < 0.001) return '<0.1%';
  if (p < 0.1) return `${(p * 100).toFixed(2)}%`;
  return `${(p * 100).toFixed(1)}%`;
}

export function ProbabilityTrio({ risk, loading = false }: ProbabilityTrioProps) {
  return (
    <section className="card space-y-4">
      <header className="flex items-baseline justify-between">
        <div>
          <h2 className="section-title !mb-0">Outcome probabilities</h2>
          <p className="text-xs text-gray-500">
            Three-threshold cumulative hazard with 95% CI from Monte-Carlo
            RR sampling.
          </p>
        </div>
        {risk?.ci95_barotitis && (
          <span className="badge badge-low !py-0.5">95% CI shown</span>
        )}
      </header>

      <div className="space-y-5">
        {OUTCOMES.map((o) => {
          const p = risk?.[o.key] ?? 0;
          const ci = risk?.[o.ciKey] ?? null;
          const widthPct = Math.max(0.5, Math.min(100, p * 100));
          const ciLoPct = ci ? Math.max(0, ci[0] * 100) : null;
          const ciHiPct = ci ? Math.min(100, ci[1] * 100) : null;

          return (
            <div key={o.key} className="space-y-1.5">
              <div className="flex items-baseline justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-200 truncate">
                    {o.label}
                  </p>
                  <p className="text-[11px] text-gray-500 truncate">
                    {o.rule} · {o.threshold}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <p className={`font-mono text-lg font-semibold ${TONE_TEXT[o.tone]}`}>
                    {loading ? '—' : formatPct(p)}
                  </p>
                  {ci && (
                    <p className="font-mono text-[10px] text-gray-500">
                      [{formatPct(ci[0])}, {formatPct(ci[1])}]
                    </p>
                  )}
                </div>
              </div>
              <div className="relative h-2.5 rounded-full bg-dark-100 overflow-hidden">
                {/* CI whisker */}
                {ciLoPct !== null && ciHiPct !== null && (
                  <div
                    className="absolute inset-y-0 bg-white/10 rounded-full"
                    style={{
                      left: `${ciLoPct}%`,
                      width: `${Math.max(0.5, ciHiPct - ciLoPct)}%`,
                    }}
                  />
                )}
                {/* point estimate bar */}
                <motion.div
                  className={`absolute inset-y-0 left-0 ${TONE_CLASS[o.tone]} rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${widthPct}%` }}
                  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {!risk && !loading && (
        <p className="text-xs text-gray-500 italic">
          Run a simulation to populate the probability trio.
        </p>
      )}
    </section>
  );
}

export default ProbabilityTrio;
