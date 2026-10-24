import { useEffect, useState } from 'react';
import { ArrowDown, ArrowUp, Check, ClipboardCheck, Search, X } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Button from '../../../components/ui/Button.jsx';
import Select from '../../../components/ui/Select.jsx';
import FilterMenu from '../../../components/ui/FilterMenu.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { apiGet, apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function DonationReviewsPage() {
  const { t } = useLang();
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState('');
  const [search, setSearch] = useState('');
  const [change, setChange] = useState('');
  const [busy, setBusy] = useState(true);
  const [reviewingId, setReviewingId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({ page: String(page), role: 'USER', sort: 'self_reported_count' });
    if (search) params.set('search', search);
    if (change) params.set('donation_count_change', change);
    setBusy(true);
    apiGet(`${API_ENDPOINTS.adminUsers}?${params}`)
      .then((data) => {
        if (!active) return;
        const results = Array.isArray(data) ? data : data?.results || [];
        setRows(results);
        setCount(Array.isArray(data) ? data.length : data?.count || 0);
        setError('');
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setBusy(false));
    return () => { active = false; };
  }, [page, search, change]);

  async function review(user, action) {
    const reviewId = user.pending_donation_count_review_id;
    if (!reviewId) return;
    const confirmKey = action === 'approve' ? 'confirmApproveDonationCount' : 'confirmRejectDonationCount';
    if (!window.confirm(t(confirmKey))) return;
    setReviewingId(reviewId);
    setError('');
    setNotice('');
    try {
      await apiPost(API_ENDPOINTS.adminDonationCountReviewAction(reviewId, action), {});
      setRows((current) => current.map((row) => row.id === user.id ? {
        ...row,
        donation_count: action === 'approve' ? row.self_reported_donation_count : row.donation_count,
        pending_donation_count_review_id: null,
        donation_count_review_status: action === 'approve' ? 'APPROVED' : 'REJECTED',
      } : row));
      setNotice(t(action === 'approve' ? 'donationCountApproved' : 'donationCountRejectedNotice'));
    } catch (err) {
      setError(err.message);
    } finally {
      setReviewingId(null);
    }
  }

  return <div className="space-y-5">
    <h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('adminDonationReviews')}</h1>
    {notice && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
    {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
    <Card className="!border-slate-200 !bg-white !p-4 !shadow-sm">
      <form onSubmit={(event) => { event.preventDefault(); setPage(1); setSearch(query.trim()); }} className="flex items-center gap-2">
        <div className="relative min-w-0 flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input aria-label={t('searchPeopleHint')} value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('searchPeopleHint')} className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/10" /></div>
        <Button type="submit" aria-label={t('search')} className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !px-0 sm:!w-auto sm:!px-4"><Search size={17} /><span className="sr-only sm:not-sr-only">{t('search')}</span></Button>
        <FilterMenu activeCount={change ? 1 : 0} onClear={() => { setChange(''); setPage(1); }}>
          <Select id="donation-count-change" label={t('changeDirection')} value={change} onChange={(event) => { setChange(event.target.value); setPage(1); }}><option value="">{t('allChanges')}</option><option value="increase">{t('increase')}</option><option value="decrease">{t('decrease')}</option></Select>
        </FilterMenu>
      </form>
      {busy ? <div className="py-12"><Spinner label={t('loading')} /></div> : rows.length ? <>
        <div className="mt-4 overflow-x-auto rounded-xl border border-slate-100" role="region" aria-label={t('adminDonationReviews')} tabIndex="0">
          <table className="w-full min-w-[980px] whitespace-nowrap text-left text-sm">
            <thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100">
              <th scope="col" className="px-3 py-3">{t('fullName')}</th><th scope="col" className="px-3 py-3">{t('bloodGroup')}</th><th scope="col" className="px-3 py-3">{t('phoneNumber')}</th><th scope="col" className="px-3 py-3">{t('reportedDonationCount')}</th><th scope="col" className="px-3 py-3">{t('approvedLeaderboardCount')}</th><th scope="col" className="px-3 py-3">{t('changeDirection')}</th><th scope="col" className="px-3 py-3">{t('status')}</th><th scope="col" className="px-3 py-3">{t('actions')}</th>
            </tr></thead>
            <tbody>{rows.map((row) => {
              const delta = (row.self_reported_donation_count || 0) - (row.donation_count || 0);
              const pending = Boolean(row.pending_donation_count_review_id);
              const statusKey = row.donation_count_review_status ? `reviewStatus${row.donation_count_review_status}` : 'reviewStatusNone';
              return <tr key={row.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/70">
                <td className="px-3 py-3 font-bold text-slate-800">{row.name || t('communityDonor')}</td><td className="px-3 py-3 text-slate-600">{row.blood_group || '—'}</td><td className="px-3 py-3 text-slate-600">{row.phone || '—'}</td>
                <td className="px-3 py-3 font-extrabold text-slate-700">{row.self_reported_donation_count || 0}</td><td className="px-3 py-3 font-extrabold text-brand">{row.donation_count || 0}</td>
                <td className="px-3 py-3">{delta ? <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${delta > 0 ? 'bg-amber-50 text-amber-800' : 'bg-blue-50 text-blue-800'}`}>{delta > 0 ? <ArrowUp size={13} /> : <ArrowDown size={13} />}{t('countChangeBy', { direction: t(delta > 0 ? 'increase' : 'decrease'), count: Math.abs(delta) })}</span> : '—'}</td>
                <td className="px-3 py-3"><span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold ${pending ? 'bg-amber-50 text-amber-800' : 'bg-slate-100 text-slate-600'}`}><ClipboardCheck size={13} />{t(statusKey)}</span></td>
                <td className="px-3 py-3">{pending ? <div className="flex items-center gap-2"><Button type="button" variant="secondary" loading={reviewingId === row.pending_donation_count_review_id} onClick={() => review(row, 'reject')} className="!min-h-9 !rounded-lg !px-3"><X size={14} />{t('rejectCount')}</Button><Button type="button" variant="primary" loading={reviewingId === row.pending_donation_count_review_id} onClick={() => review(row, 'approve')} className="!min-h-9 !rounded-lg !px-3"><Check size={14} />{t('approveCount')}</Button></div> : '—'}</td>
              </tr>;
            })}</tbody>
          </table>
        </div>
        <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
      </> : <div className="py-12 text-center"><ClipboardCheck className="mx-auto text-slate-300" size={28} /><p className="mt-3 text-sm font-bold text-slate-700">{t('noDonationReviewUsers')}</p></div>}
    </Card>
  </div>;
}
