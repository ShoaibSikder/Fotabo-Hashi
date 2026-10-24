import { useLocation } from 'react-router-dom';
import Skeleton from './Skeleton.jsx';

function AuthSkeleton() {
  return (
    <main className="page-shell grid min-h-[70vh] place-items-center py-10">
      <div className="neu w-full max-w-lg space-y-5 p-6 sm:p-8" aria-hidden="true">
        <Skeleton className="h-14 w-14 rounded-2xl" />
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full rounded-full" />
      </div>
    </main>
  );
}

export function PublicContentSkeleton() {
  return (
    <div aria-hidden="true">
      <div className="page-shell space-y-8 py-6 sm:py-8">
        <Skeleton className="h-[300px] rounded-3xl sm:h-[380px] lg:h-[440px]" />
        <div className="mx-auto max-w-2xl space-y-4 py-4">
          <Skeleton className="mx-auto h-4 w-28" />
          <Skeleton className="mx-auto h-9 w-2/3" />
          <Skeleton className="mx-auto h-4 w-full" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((item) => <Skeleton key={item} className="h-36" />)}
        </div>
      </div>
    </div>
  );
}

function PublicSkeleton() {
  return (
    <>
      <div className="page-shell flex h-[72px] items-center justify-between" aria-hidden="true">
        <Skeleton className="h-10 w-44" />
        <Skeleton className="hidden h-9 w-72 lg:block" />
        <Skeleton className="h-10 w-28 rounded-full" />
      </div>
      <PublicContentSkeleton />
    </>
  );
}

function DashboardSkeleton() {
  return (
    <main className="min-h-screen bg-surface" aria-hidden="true">
      <div className="page-shell grid min-h-screen gap-5 py-5 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="neu hidden space-y-7 p-5 lg:block">
          <Skeleton className="h-11 w-full" />
          {[0, 1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-10 w-full" />)}
        </aside>
        <section className="min-w-0 space-y-6">
          <div className="neu flex h-[72px] items-center justify-between p-4">
            <Skeleton className="h-8 w-36" />
            <Skeleton className="h-10 w-10 rounded-full" />
          </div>
          <div className="space-y-3">
            <Skeleton className="h-8 w-52" />
            <Skeleton className="h-4 w-72 max-w-full" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[0, 1, 2, 3].map((item) => <Skeleton key={item} className="h-28" />)}
          </div>
          <div className="grid gap-5 xl:grid-cols-2">
            {[0, 1].map((item) => <Skeleton key={item} className="h-64" />)}
          </div>
        </section>
      </div>
    </main>
  );
}

export function DashboardContentSkeleton() {
  const { pathname } = useLocation();
  const isAdmin = pathname.startsWith('/admin');

  return (
    <section className="min-w-0 space-y-6" aria-hidden="true">
      <div className="space-y-3">
        <Skeleton className="h-8 w-56 max-w-full" />
        <Skeleton className="h-4 w-72 max-w-full" />
      </div>
      {isAdmin ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
            {[0, 1, 2, 3].map((item) => <Skeleton key={item} className="h-28" />)}
          </div>
          <Skeleton className="h-12 w-full rounded-xl" />
          <div className="space-y-3">
            {[0, 1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-[72px] rounded-xl" />)}
          </div>
        </>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[0, 1, 2, 3].map((item) => <Skeleton key={item} className="h-28" />)}
          </div>
          <div className="grid gap-5 xl:grid-cols-2">
            {[0, 1].map((item) => <Skeleton key={item} className="h-64" />)}
          </div>
        </>
      )}
    </section>
  );
}

export default function RouteLoadingSkeleton() {
  const { pathname } = useLocation();
  let page = <PublicSkeleton />;

  if (/^\/(login|register|forgot-password|reset-password)/.test(pathname)) {
    page = <AuthSkeleton />;
  } else if (pathname.startsWith('/admin') || pathname.startsWith('/dashboard') || pathname.startsWith('/profile') || pathname.startsWith('/settings') || pathname.startsWith('/donors') || pathname.startsWith('/requests') || pathname.startsWith('/leaderboard')) {
    page = <DashboardSkeleton />;
  }

  return <div role="status" aria-label="Loading page" aria-live="polite">{page}</div>;
}
