import React from 'react';

type Props = React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  hint?: string;
  error?: string;
};

export default function TextArea({ label, hint, error, id, ...rest }: Props) {
  const taId = id || React.useId();
  return (
    <div className="field">
      {label && <label htmlFor={taId}>{label}</label>}
      <textarea id={taId} rows={rest.rows ?? 3} {...rest} />
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}

