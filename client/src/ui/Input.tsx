import React from 'react';
import Tooltip from '@/ui/Tooltip';

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  error?: string;
  tooltip?: string;
  labelAction?: React.ReactNode;
};

export default function Input({ label, hint, error, tooltip, labelAction, id, ...rest }: Props) {
  const inputId = id || React.useId();
  return (
    <div className="field">
      {(label || labelAction) && (
        <div className="inline" style={labelAction ? { justifyContent: 'space-between' } : undefined}>
          <div className="inline">
            {label && <label htmlFor={inputId}>{label}</label>}
            {tooltip ? <Tooltip text={tooltip} /> : null}
          </div>
          {labelAction}
        </div>
      )}
      <input id={inputId} {...rest} />
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}
