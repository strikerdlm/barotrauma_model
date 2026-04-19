/**
 * App — top-level shell. Defaults to the v2 (Python-backed) dashboard.
 * The v1 legacy dashboard remains accessible for reproducibility against
 * the pre-2026 single-risk model.
 */

import { useState } from 'react';

import { Dashboard } from './components/Dashboard';
import { V2Dashboard } from './components/V2Dashboard';

type View = 'v2' | 'v1';

export default function App() {
  const [view, setView] = useState<View>('v2');

  return (
    <div className="App">
      {view === 'v2' ? (
        <V2Dashboard onShowLegacy={() => setView('v1')} />
      ) : (
        <div>
          <div className="max-w-[1800px] mx-auto px-6 pt-4">
            <button
              type="button"
              onClick={() => setView('v2')}
              className="btn-secondary inline-flex items-center gap-2"
            >
              ← Back to v2 (current model)
            </button>
          </div>
          <Dashboard />
        </div>
      )}
    </div>
  );
}
