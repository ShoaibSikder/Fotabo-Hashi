import { useEffect, useState } from 'react';
import Card from '../../../components/ui/Card.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import { apiGet } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function AdministrationPage() {
  const { t, lang } = useLang();
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    setBusy(true);
    apiGet(`${API_ENDPOINTS.adminAudit}?page=${page}`)
      .then((data) => {
        if (!mounted) return;
        setRows(data?.results || []);
        setCount(data?.count || 0);
      })
      .catch((err) => mounted && setError(err.message))
      .finally(() => mounted && setBusy(false));
    return () => { mounted = false; };
  }, [page]);

  return <div className="space-y-6">
    <div><h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('adminAudit')}</h1></div>
    {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
    <Card className="!border-slate-200 !bg-white !shadow-sm">
      <h2 className="font-heading text-lg font-extrabold text-slate-900">{t('recentActivity')}</h2>
      {busy ? <div className="py-10"><Spinner label={t('loadingSystemActivity')} /></div> : rows.length ? <>
        <div className="mt-4 overflow-x-auto rounded-xl border border-slate-100" role="region" aria-label={t('adminAudit')} tabIndex="0"><table className="w-full min-w-[780px] whitespace-nowrap text-left text-sm"><thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100"><th scope="col" className="px-3 py-3">{t('when')}</th><th scope="col" className="px-3 py-3">{t('actor')}</th><th scope="col" className="px-3 py-3">{t('action')}</th><th scope="col" className="px-3 py-3">{t('resource')}</th><th scope="col" className="px-3 py-3">{t('details')}</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/70"><td className="px-3 py-3 text-xs text-slate-500">{new Intl.DateTimeFormat(lang === 'bn' ? 'bn-BD' : 'en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(row.created_at))}</td><td className="px-3 py-3">{row.actor_email ? t('admin') : t('system')}</td><td className="px-3 py-3 font-bold text-brand">{row.action}</td><td className="px-3 py-3">{row.resource_type} {row.resource_id}</td><td className="max-w-[360px] truncate px-3 py-3 text-slate-600" title={row.description || ''}>{row.description || '—'}</td></tr>)}</tbody></table></div>
        <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
      </> : <p className="mt-5 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">{t('noAuditEvents')}</p>}
    </Card>
  </div>;
}
