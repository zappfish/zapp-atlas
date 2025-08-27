import React from 'react';

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  error?: string;
};

export default function Input({ label, hint, error, id, ...rest }: Props) {
  const inputId = id || React.useId();
  return (
    <div className="field">
      {label && <label htmlFor={inputId}>{label}</label>}
      <input id={inputId} {...rest} />
      {hint && <small className="hint">{hint}</small>}
      {error && <small className="error">{error}</small>}
    </div>
  );
}

