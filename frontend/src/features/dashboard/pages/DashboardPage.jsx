import { useEffect, useState } from 'react';
import { Activity, ArrowRight, Droplet, MapPin, Phone, Plus, Search, UserRound } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card from '../../../components/ui/Card.jsx';
import Avatar from '../../../components/ui/Avatar.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { useAuthCtx } from '../../../contexts/AuthContext.jsx';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import { apiGet } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';

export default function DashboardPage() {
  const { user } = useAuthCtx();
  const { t } = useLang();
  const [profile, setProfile] = useState(null);
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState({ total: null, active: null, fulfilled: null });
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let alive = true;
    Promise.allSettled([
      apiGet(API_ENDPOINTS.profile),
      apiGet(API_ENDPOINTS.myRequestSummary),
    ]).then(([profileResult, summaryResult]) => {
      if (!alive) return;
      setLoadError([profileResult, summaryResult].some((result) => result.status === 'rejected'));
      if (profileResult.status === 'fulfilled') setProfile(profileResult.value);

      const summary = summaryResult.status === 'fulfilled' ? summaryResult.value : null;
      setRequests(summary?.recent_requests || []);
      setStats({
        total: summary?.total ?? null,
        active: summary?.active ?? null,
        fulfilled: summary?.fulfilled ?? null,
      });
    }).finally(() => alive && setLoading(false));

    return () => { alive = false; };
  }, []);

  const name = profile?.name || user?.name || 'Community member';
  const role = user?.role === 'ADMIN' ? 'Admin' : 'User';
  const profileFields = [profile?.name, profile?.phone, profile?.blood_group, profile?.location];
  const completion = Math.round((profileFields.filter(Boolean).length / profileFields.length) * 100);

  return (
    <div className="page-enter space-y-5 sm:space-y-6">
      <h1 className="font-heading text-3xl font-extrabold tracking-tight text-brand-dark sm:text-4xl">{t('dashboard')}</h1>
      {loadError && <p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{t('connection')} {t('retry')}</p>}
      <Card className="!p-5 sm:!p-6">
        {loading && !profile ? (
          <div className="flex min-h-28 items-center justify-center"><Spinner label="Loading dashboard…" /></div>
        ) : (
          <div className="flex items-start gap-4 sm:items-center sm:gap-6">
            <Avatar name={name} size="lg" className="!h-14 !w-14 self-start !text-sm sm:!h-[76px] sm:!w-[76px] sm:!text-base" />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <h2 className="font-heading text-xl font-extrabold tracking-tight text-brand-dark sm:text-2xl">{name}</h2>
                <span className="rounded-full bg-brand-soft px-2.5 py-1 text-[11px] font-bold text-brand">{role}</span>
              </div>
              <div className="mt-3 grid gap-x-6 gap-y-2 text-sm text-muted sm:grid-cols-2">
                <Contact icon={<span className="font-bold">@</span>} value={profile?.email || user?.email} />
                <Contact icon={<Phone size={15} />} value={profile?.phone} />
                <Contact icon={<MapPin size={15} />} value={profile?.location} />
                <Contact icon={<Droplet size={15} />} value={profile?.blood_group} />
              </div>
            </div>
          </div>
        )}
      </Card>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4" aria-label="Your dashboard analytics">
        <MetricCard to="/requests" icon={<Activity size={20} />} label="Active requests" value={stats.active} loading={loading} />
        <MetricCard to="/requests" icon={<Droplet size={20} />} label="Your requests" value={stats.total} loading={loading} />
        <MetricCard to="/profile" icon={<UserRound size={20} />} label="Profile complete" value={`${completion}%`} loading={loading && !profile} />
        <MetricCard to="/profile" icon={<Search size={20} />} label="Donor status" value={profile?.is_available_for_donation ? 'Available' : 'Unavailable'} loading={loading && !profile} />
      </section>

      <div className="grid items-start gap-5 2xl:grid-cols-[1.35fr_.65fr]">
        <Card className="!p-5 sm:!p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="font-heading text-lg font-extrabold text-brand-dark">Your recent requests</h2>
            <Link to="/requests" className="inline-flex items-center gap-1 text-sm font-bold text-brand hover:underline">All requests <ArrowRight size={15} /></Link>
          </div>
          {loading ? <div className="py-8"><Spinner label="Loading requests…" /></div> : requests.length ? (
            <div className="divide-y divide-brand-dark/10">
              {requests.map((request) => (
                <Link key={request.id} to={`/requests/${request.id}`} className="flex items-center gap-3 py-3 first:pt-1 hover:bg-white/40">
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand"><Droplet size={18} /></span>
                  <span className="min-w-0 flex-1"><span className="block truncate text-sm font-bold text-brand-dark">{request.blood_group} · {request.required_units} unit{request.required_units === 1 ? '' : 's'}</span><span className="mt-0.5 block truncate text-xs text-muted">{request.location}</span></span>
                  <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${request.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700' : request.status === 'FULFILLED' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>{request.status}</span>
                </Link>
              ))}
            </div>
          ) : <div className="py-8 text-center"><p className="text-sm font-semibold text-muted">No requests yet</p><Link to="/requests/new" className="mt-3 inline-flex items-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-bold text-white"><Plus size={16} /> Create request</Link></div>}
        </Card>

        <Card className="!p-5 sm:!p-6">
          <h2 className="font-heading text-lg font-extrabold text-brand-dark">Quick actions</h2>
          <div className="mt-4 grid gap-3">
            <QuickAction to="/requests/new" icon={<Plus size={17} />} label="Request blood" />
            <QuickAction to="/donors" icon={<Search size={17} />} label="Find a donor" />
            <QuickAction to="/profile" icon={<UserRound size={17} />} label="Update profile" />
          </div>
          {stats.fulfilled > 0 && <p className="mt-4 text-xs font-semibold text-muted">Requests fulfilled: {stats.fulfilled}</p>}
        </Card>
      </div>
    </div>
  );
}

function Contact({ icon, value }) {
  return <p className="flex min-w-0 items-center gap-2"><span className="shrink-0 text-brand/80">{icon}</span><span className="truncate">{value || 'Not added'}</span></p>;
}

function MetricCard({ to, icon, label, value, loading }) {
  return <Link to={to} className="group block rounded-2xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"><Card className="h-full !p-5 transition-transform group-hover:-translate-y-0.5 sm:!p-6"><div className="flex items-center gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand">{icon}</span><div className="min-w-0"><p className="text-xs font-semibold text-muted sm:text-sm">{label}</p><p className="mt-1 truncate text-2xl font-extrabold leading-none text-brand-dark">{loading ? '…' : value ?? '—'}</p></div></div></Card></Link>;
}

function QuickAction({ to, icon, label }) {
  return <Link to={to} className="flex min-h-12 items-center gap-3 rounded-xl bg-brand-soft/70 px-3.5 text-sm font-bold text-brand-dark transition-colors hover:bg-brand-soft"><span className="text-brand">{icon}</span>{label}<ArrowRight className="ml-auto" size={16} /></Link>;
}
