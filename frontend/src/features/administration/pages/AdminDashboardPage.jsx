import { useEffect, useState } from 'react';
import { Activity, ArrowRight, HeartPulse, UsersRound, Droplet, ShieldCheck, ClipboardCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import Card from '../../../components/ui/Card.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { apiGet } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

const shortcuts = [
  { to: '/admin/users', key: 'adminUsers', Icon: UsersRound },
  { to: '/admin/donation-reviews', key: 'adminDonationReviews', Icon: ClipboardCheck },
  { to: '/admin/requests', key: 'adminRequests', Icon: HeartPulse },
  { to: '/admin/audit', key: 'adminAudit', Icon: Activity },
];

export default function AdminDashboardPage() {
  const { t } = useLang();
  const [overview, setOverview] = useState(null);
  const [activity, setActivity] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.allSettled([
      apiGet(API_ENDPOINTS.adminOverview),
      apiGet(`${API_ENDPOINTS.adminAudit}?recent=6`),
    ]).then(([overviewResult, activityResult]) => {
      if (!active) return;
      setLoadError([overviewResult, activityResult].some((result) => result.status === 'rejected'));
      if (overviewResult.status === 'fulfilled') setOverview(overviewResult.value);
      if (activityResult.status === 'fulfilled') {
        const rows = activityResult.value?.results || activityResult.value || [];
        setActivity(Array.isArray(rows) ? rows.slice(0, 6) : []);
      }
    }).finally(() => active && setLoading(false));

    // Readiness checks include remote PostgreSQL, Redis, and storage probes.
    // Keep that slower status request off the dashboard's initial render path.
    apiGet(API_ENDPOINTS.health)
      .then((result) => active && setHealth(result))
      .catch(() => active && setHealth({ status: 'error' }));

    return () => { active = false; };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('adminOverview')}</h1></div>
        <span className={`inline-flex items-center gap-2 rounded-full px-3 py-2 text-xs font-bold ${health?.status === 'ok' ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-800'}`}><span className={`h-2 w-2 rounded-full ${health?.status === 'ok' ? 'bg-emerald-500' : 'bg-amber-500'}`} />System {health?.status || 'checking'}</span>
      </div>
      {loadError && <p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{t('connection')} {t('retry')}</p>}

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4" aria-label="Platform metrics">
        <MetricCard label={t('totalAccounts')} value={overview?.users} detail={`${overview?.active_users ?? '—'} active`} Icon={UsersRound} />
        <MetricCard label={t('availableDonorCount')} value={overview?.donors} detail="" Icon={Droplet} />
        <MetricCard label={t('bloodRequests')} value={overview?.blood_requests} detail={`${overview?.active_blood_requests ?? '—'} active`} Icon={HeartPulse} />
        <MetricCard label={t('auditEvents')} value={overview?.audit_events} detail="" Icon={Activity} />
      </section>

      <div className="grid gap-5 2xl:grid-cols-[1.1fr_.9fr]">
        <Card className="!border-slate-200 !bg-white !shadow-sm">
          <div className="flex items-center justify-between gap-3"><h2 className="font-heading text-lg font-extrabold text-slate-900">Manage</h2><ShieldCheck className="text-brand" size={21} /></div>
          <div className="mt-4 divide-y divide-slate-100">
            {shortcuts.map(({ to, key, Icon }) => <Link key={to} to={to} className="group flex items-center gap-3 py-4 first:pt-1 last:pb-1"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-rose-50 text-brand"><Icon size={18} /></span><span className="min-w-0 flex-1"><span className="block text-sm font-bold text-slate-800">{t(key)}</span></span><ArrowRight size={17} className="shrink-0 text-slate-400 transition-transform group-hover:translate-x-1 group-hover:text-brand" /></Link>)}
          </div>
        </Card>

        <Card className="!border-slate-200 !bg-white !shadow-sm">
          <div className="flex items-center justify-between gap-3"><h2 className="font-heading text-lg font-extrabold text-slate-900">Recent activity</h2><Link to="/admin/audit" className="inline-flex items-center gap-1 text-xs font-bold text-brand hover:underline">View all <ArrowRight size={14} /></Link></div>
          {loading ? <div className="py-10"><Spinner label="Loading system activity…" /></div> : activity.length ? <ul className="mt-4 divide-y divide-slate-100">{activity.map((row) => <li key={row.id} className="py-3 first:pt-1"><div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate text-sm font-bold text-slate-800">{row.description || `${row.action} ${row.resource_type}`}</p><p className="mt-1 truncate text-xs text-slate-500">{row.actor_email || 'System'} · {row.resource_type}</p></div><time className="shrink-0 text-[11px] text-slate-400" dateTime={row.created_at}>{new Date(row.created_at).toLocaleDateString()}</time></div></li>)}</ul> : <p className="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No audit events are available yet.</p>}
        </Card>
      </div>

      <Card className="!border-slate-200 !bg-white !shadow-sm">
        <h2 className="font-heading text-lg font-extrabold text-slate-900">{t('last7Days')}</h2>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">{[['New accounts', overview?.users_last_7_days], ['New requests', overview?.requests_last_7_days], ['Active accounts', overview?.active_users], ['Available donors', overview?.donors]].map(([label, value]) => <div key={label} className="rounded-xl bg-slate-50 p-3"><p className="text-[11px] font-semibold text-slate-600">{label}</p><p className="mt-1 text-lg font-extrabold text-slate-900">{loading ? '…' : value ?? '—'}</p></div>)}</div>
      </Card>
    </div>
  );
}

function MetricCard({ label, value, detail, Icon }) {
  return <Card className="!border-slate-200 !bg-white !p-5 !shadow-sm"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-semibold text-slate-500">{label}</p><p className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950">{value ?? '—'}</p><p className="mt-1 text-[11px] text-slate-500">{detail}</p></div><span className="grid h-10 w-10 place-items-center rounded-xl bg-rose-50 text-brand"><Icon size={19} /></span></div></Card>;
}
