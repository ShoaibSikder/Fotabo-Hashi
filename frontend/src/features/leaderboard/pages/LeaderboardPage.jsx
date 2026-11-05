import { useEffect, useState } from 'react';
import { Trophy } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import { TableLoadingSkeleton } from '../../../components/ui/DataLoadingSkeleton.jsx';
import EmptyState from '../../../components/ui/EmptyState.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiGet } from '../../../services/apiClient.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function LeaderboardPage() {
  const { t } = useLang();
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setBusy(true);
    setError('');
    apiGet(`${API_ENDPOINTS.leaderboard}?page=${page}&page_size=20`)
      .then((value) => {
        if (!active) return;
        setRows(Array.isArray(value) ? value : value?.results || []);
        setCount(Array.isArray(value) ? value.length : value?.count || 0);
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setBusy(false));
    return () => { active = false; };
  }, [page]);

  return (
    <div className="page-enter space-y-6">
      <h1 className="text-3xl font-extrabold text-brand-dark">{t('leaderboard')}</h1>
      <Card className="overflow-hidden !border-0 !bg-gradient-to-br !from-[#7f1d1d] !to-[#b91c1c] !text-white">
        <div className="flex items-center gap-5">
          <span className="grid h-16 w-16 place-items-center rounded-2xl bg-white/15"><Trophy size={34} /></span>
          <div><h2 className="text-2xl font-extrabold text-white">{t('leaderboard')}</h2><p className="mt-1 text-sm text-white/80">{t('verifiedDonationRanking')}</p></div>
        </div>
      </Card>
      {error && <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      {busy ? (
        <TableLoadingSkeleton columns={4} />
      ) : rows.length ? (
        <>
          <Card className="!p-0">
            <div className="data-scroll-region data-table-scroll rounded-2xl" role="region" aria-label={t('leaderboard')} tabIndex="0">
              <table className="w-full min-w-[560px] whitespace-nowrap text-left text-sm">
                <thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100"><th scope="col" className="px-4 py-3">#</th><th scope="col" className="px-4 py-3">{t('fullName')}</th><th scope="col" className="px-4 py-3">{t('approvedLeaderboardCount')}</th><th scope="col" className="px-4 py-3">{t('rank')}</th></tr></thead>
                <tbody>{rows.map((person, index) => <tr key={person.user_id || index} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/70"><td className="px-4 py-3"><span className="grid h-8 w-8 place-items-center rounded-full bg-brand-soft font-extrabold text-brand">{person.rank || index + 1}</span></td><td className="px-4 py-3 font-extrabold text-brand-dark">{person.name || t('communityDonor')}</td><td className="px-4 py-3 font-bold text-slate-700">{person.donation_count || 0}</td><td className="px-4 py-3"><Trophy aria-label={t('leaderboard')} className={index === 0 ? 'text-amber-500' : 'text-muted'} size={18} /></td></tr>)}</tbody>
              </table>
            </div>
          </Card>
          <Pagination page={page} count={count} onChange={setPage} />
        </>
      ) : !error && (
        <EmptyState title={t('leaderboardEmptyTitle')} description={t('leaderboardEmptyDescription')} />
      )}
    </div>
  );
}
