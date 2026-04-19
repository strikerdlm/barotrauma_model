/**
 * AnatomyBuilder — adjust the two anatomy variables that matter
 * clinically: mastoid air-cell volume (dominant inter-subject variance
 * per Alper 2011, ~10× range 2–15 mL) and tympanum volume. Other
 * PatientAnatomy fields stay at v2 defaults.
 */

import { Slider } from '../ui/Slider';
import type { PatientAnatomyV2 } from '../../types/v2';

interface AnatomyBuilderProps {
  value: PatientAnatomyV2;
  onChange: (next: PatientAnatomyV2) => void;
}

export function AnatomyBuilder({ value, onChange }: AnatomyBuilderProps) {
  return (
    <div className="space-y-4">
      <Slider
        label="Mastoid air-cell volume"
        description="Dominant inter-subject variance in ME buffering. Alper 2011 prior: log-normal, median 7.0 mL, 95% interval 2.9–16.9 mL."
        value={value.mastoid_volume_ml}
        onChange={(v) => onChange({ ...value, mastoid_volume_ml: v })}
        min={2}
        max={15}
        step={0.25}
        unit="mL"
        showTicks
        tickLabels={['2', '5', '8', '11', '15']}
      />
      <Slider
        label="Tympanum volume"
        description="Kanick-Doyle 2005 adult mean 1.0 mL. Small individual variance."
        value={value.tympanum_volume_ml}
        onChange={(v) => onChange({ ...value, tympanum_volume_ml: v })}
        min={0.5}
        max={2.0}
        step={0.05}
        unit="mL"
      />
      <Slider
        label="Age"
        value={value.age_years}
        onChange={(v) => onChange({ ...value, age_years: Math.round(v) })}
        min={18}
        max={65}
        step={1}
        unit="yr"
      />
    </div>
  );
}

export default AnatomyBuilder;
