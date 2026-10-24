
export default function Textarea({ id, label, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <textarea id={id} className="field-control min-h-32 resize-y" {...props} />
    </div>
  );
}
