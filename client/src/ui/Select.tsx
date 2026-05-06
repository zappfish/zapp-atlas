import React from 'react';
import Tooltip from '@/ui/Tooltip';

type Props = React.SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  hint?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
  tooltip?: string;
};

export default function Select({ label, hint, error, options, tooltip, id, ...rest }: Props) {
  const selectId = id || React.useId();
  return (
    <div className="field">
      {label && (
        <div className="inline">
          <label htmlFor={selectId}>{label}</label>
          {tooltip ? <Tooltip text={tooltip} /> : null}
        </div>
      )}
      <select id={selectId} {...rest}>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}
