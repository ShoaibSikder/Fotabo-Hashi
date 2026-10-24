
export default function Select({ id, label, children, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <select id={id} className="field-control cursor-pointer" {...props}>{children}</select>
    </div>
  );
}
