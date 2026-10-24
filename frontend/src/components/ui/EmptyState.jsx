
import { SearchX } from 'lucide-react';

export default function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
      <span className="mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-white/60 text-brand"><SearchX size={25} /></span>
      <h3 className="text-lg font-extrabold text-ink">{title}</h3>
      {description && <p className="mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
