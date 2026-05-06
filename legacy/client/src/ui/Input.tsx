import React from 'react';
import Tooltip from '@/ui/Tooltip';

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  error?: string;
  tooltip?: string;
};

export default function Input({ label, hint, error, tooltip, id, ...rest }: Props) {
  const inputId = id || React.useId();
  return (
    <div className="field">
      {label && (
        <div className="inline">
          <label htmlFor={inputId}>{label}</label>
          {tooltip ? <Tooltip text={tooltip} /> : null}
        </div>
      )}
      <input id={inputId} {...rest} />
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}
