import Skeleton from './Skeleton.jsx';

const rows = [0, 1, 2, 3, 4];

export function TableLoadingSkeleton({ columns = 5, rows: rowCount = 6 }) {
  return (
    <div role="status" aria-label="Loading results" aria-live="polite" className="overflow-hidden rounded-xl border border-slate-100 bg-white">
      <div className="flex gap-4 border-b border-slate-100 bg-slate-50 px-4 py-3">
        {Array.from({ length: columns }, (_, index) => <Skeleton key={index} className="h-3 flex-1" />)}
      </div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rowCount }, (_, row) => (
          <div key={row} className="flex items-center gap-4 px-4 py-4">
            {Array.from({ length: columns }, (_, column) => <Skeleton key={column} className={`h-4 ${column === 0 ? 'w-32' : 'flex-1'}`} />)}
          </div>
        ))}
      </div>
    </div>
  );
}

export function CardGridLoadingSkeleton({ count = 4 }) {
  return (
    <div role="status" aria-label="Loading results" aria-live="polite" className="grid gap-4 md:grid-cols-2">
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="space-y-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3"><Skeleton className="h-11 w-11 shrink-0 rounded-xl" /><div className="flex-1 space-y-2"><Skeleton className="h-4 w-2/3" /><Skeleton className="h-3 w-1/3" /></div><Skeleton className="h-6 w-16 rounded-full" /></div>
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-full" />
          <div className="flex justify-end"><Skeleton className="h-8 w-24" /></div>
        </div>
      ))}
    </div>
  );
}

export function ListLoadingSkeleton({ count = 5, className = '' }) {
  return (
    <div role="status" aria-label="Loading results" aria-live="polite" className={`space-y-3 ${className}`}>
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3">
          <Skeleton className="h-10 w-10 shrink-0 rounded-xl" />
          <div className="min-w-0 flex-1 space-y-2"><Skeleton className="h-4 w-2/3" /><Skeleton className="h-3 w-1/3" /></div>
          <Skeleton className="h-8 w-20 shrink-0" />
        </div>
      ))}
    </div>
  );
}

export function ProfileLoadingSkeleton() {
  return (
    <div role="status" aria-label="Loading profile" aria-live="polite" className="space-y-5 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm sm:p-7">
      <div className="flex items-center gap-4"><Skeleton className="h-16 w-16 rounded-full" /><div className="flex-1 space-y-2"><Skeleton className="h-5 w-40" /><Skeleton className="h-4 w-52 max-w-full" /></div></div>
      <div className="grid gap-5 sm:grid-cols-2">{rows.slice(0, 4).map((row) => <div key={row} className="space-y-2"><Skeleton className="h-3 w-24" /><Skeleton className="h-11 w-full rounded-xl" /></div>)}</div>
      <Skeleton className="h-11 w-full rounded-xl" />
      <div className="flex justify-end"><Skeleton className="h-11 w-28 rounded-xl" /></div>
    </div>
  );
}

export function PanelLoadingSkeleton({ count = 4 }) {
  return (
    <div role="status" aria-label="Loading content" aria-live="polite" className="space-y-3">
      {Array.from({ length: count }, (_, index) => <div key={index} className="flex items-center gap-3 py-3"><Skeleton className="h-10 w-10 shrink-0 rounded-xl" /><div className="flex-1 space-y-2"><Skeleton className="h-4 w-2/3" /><Skeleton className="h-3 w-1/3" /></div></div>)}
    </div>
  );
}
