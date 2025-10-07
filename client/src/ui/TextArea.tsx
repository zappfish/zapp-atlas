import React from 'react';
import Tooltip from '@/ui/Tooltip';

type Props = React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  hint?: string;
  error?: string;
  tooltip?: string;
};

export default function TextArea({ label, hint, error, tooltip, id, ...rest }: Props) {
  const taId = id || React.useId();
  return (
    <div className="field">
      {label && (
        <div className="inline">
          <label htmlFor={taId}>{label}</label>
          {tooltip ? <Tooltip text={tooltip} /> : null}
        </div>
      )}
      <textarea id={taId} rows={rest.rows ?? 3} {...rest} />
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}
