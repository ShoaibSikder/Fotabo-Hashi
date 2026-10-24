
const tones = {
  red: 'bg-brand text-white',
  soft: 'bg-brand-soft text-brand-dark',
  green: 'bg-emerald-50 text-emerald-800',
  amber: 'bg-amber-50 text-amber-900',
  neutral: 'bg-slate-100 text-slate-700',
};

export default function Badge({ children, tone = 'red', className = '' }) {
  return <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-extrabold ${tones[tone] || tones.red} ${className}`}>{children}</span>;
}
