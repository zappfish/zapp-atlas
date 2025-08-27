import React from 'react';

type Props = React.SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  hint?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
};

export default function Select({ label, hint, error, options, id, ...rest }: Props) {
  const selectId = id || React.useId();
  return (
    <div className="field">
      {label && <label htmlFor={selectId}>{label}</label>}
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

