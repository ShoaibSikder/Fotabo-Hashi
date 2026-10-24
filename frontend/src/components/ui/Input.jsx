
export default function Input({ id, label, hint, error, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <input id={id} className="field-control" aria-invalid={Boolean(error)} aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined} {...props} />
      {hint && !error && <p id={`${id}-hint`} className="mt-1.5 text-xs text-muted">{hint}</p>}
      {error && <p id={`${id}-error`} className="mt-1.5 text-xs font-semibold text-red-800">{error}</p>}
    </div>
  );
}
