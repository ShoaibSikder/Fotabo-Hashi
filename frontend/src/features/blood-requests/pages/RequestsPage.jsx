import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Droplet, MapPin, Plus, Search } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Button from '../../../components/ui/Button.jsx';
import Badge from '../../../components/ui/Badge.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import EmptyState from '../../../components/ui/EmptyState.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import FilterMenu from '../../../components/ui/FilterMenu.jsx';
import Select from '../../../components/ui/Select.jsx';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiGet } from '../../../services/apiClient.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import { BLOOD_GROUPS } from '../../../utils/constants.js';

const PAGE_SIZE = 20;

export default function RequestsPage() {
  const { t } = useLang();
  const [searchTerm, setSearchTerm] = useState('');
  const [appliedSearch, setAppliedSearch] = useState('');
  const [bloodGroup, setBloodGroup] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setBusy(true);
    setError('');
    const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
    if (appliedSearch) query.set('search', appliedSearch);
    if (bloodGroup) query.set('blood_group', bloodGroup);
    if (status) query.set('status', status);
    try {
      const data = await apiGet(`${API_ENDPOINTS.requests}?${query}`);
      setRows(Array.isArray(data) ? data : data?.results || []);
      setCount(data?.count ?? 0);
    } catch (err) {
      setError(err.message);
      setRows([]);
      setCount(0);
    } finally {
      setBusy(false);
    }
  }, [appliedSearch, bloodGroup, page, status]);

  useEffect(() => { load(); }, [load]);

  function submitFilters(event) {
    event.preventDefault();
    setAppliedSearch(searchTerm.trim());
    setPage(1);
  }

  return <div className="page-enter space-y-6">
    <div className="flex flex-wrap items-center justify-between gap-3"><h1 className="text-2xl font-extrabold text-brand-dark sm:text-3xl">{t('bloodRequests')}</h1><Link to="/requests/new" aria-label={t('createRequest')}><Button variant="primary" className="!min-h-10 !px-3 sm:!px-4"><Plus size={17} /><span className="sr-only sm:not-sr-only">{t('createRequest')}</span></Button></Link></div>
    <Card className="!p-4 sm:!p-5"><form className="flex w-full items-center gap-2" onSubmit={submitFilters}>
      <div className="relative min-w-0 flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input id="request-search" aria-label={t('requestSearchLabel')} className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-800 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/10" placeholder={t('searchRequestsPlaceholder')} value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} /></div>
      <Button type="submit" variant="secondary" aria-label={t('search')} className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !px-0 sm:!w-auto sm:!px-4"><Search size={17} aria-hidden="true" /><span className="sr-only sm:not-sr-only">{t('search')}</span></Button>
      <FilterMenu activeCount={[bloodGroup, status].filter(Boolean).length} onClear={() => { setBloodGroup(''); setStatus(''); setPage(1); }}>
        <Select id="request-filter-group" label={t('bloodGroup')} value={bloodGroup} onChange={(event) => { setBloodGroup(event.target.value); setPage(1); }}><option value="">{t('allBloodGroups')}</option>{BLOOD_GROUPS.map((group) => <option key={group}>{group}</option>)}</Select>
        <Select id="request-filter-status" label={t('status')} value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}><option value="">{t('allStatuses')}</option><option value="ACTIVE">{t('active')}</option><option value="FULFILLED">{t('fulfilled')}</option><option value="CANCELLED">{t('cancelled')}</option></Select>
      </FilterMenu>
    </form></Card>
    {error && <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</div>}
    {busy ? <div className="py-12 text-center"><Spinner label={t('loadingRequests')} /></div> : rows.length ? <>
      <div className="grid gap-4 md:grid-cols-2">{rows.map((request) => <Card key={request.id}><div className="flex items-start justify-between gap-3"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-brand-soft text-brand"><Droplet /></span><div><h2 className="font-extrabold text-brand-dark">{request.blood_group} {t('bloodNeeded')}</h2><p className="text-sm text-muted">{t('unitsRequested', { count: request.required_units || 1 })}</p></div></div><Badge tone={request.status === 'ACTIVE' ? 'red' : request.status === 'FULFILLED' ? 'green' : 'neutral'}>{t(request.status === 'ACTIVE' ? 'active' : request.status === 'FULFILLED' ? 'fulfilled' : 'cancelled')}</Badge></div><p className="mt-4 flex items-center gap-2 text-sm text-muted"><MapPin size={16} />{request.location || t('locationNotListed')}</p>{request.description && <p className="mt-3 line-clamp-3 text-sm leading-6 text-ink">{request.description}</p>}<div className="mt-5 flex justify-end"><Link className="inline-flex items-center gap-2 text-sm font-extrabold text-brand" to={`/requests/${request.id}`}>{t('viewDetails')} <ArrowRight size={16} /></Link></div></Card>)}</div>
      <Pagination page={page} pages={Math.max(1, Math.ceil(count / PAGE_SIZE))} onChange={setPage} />
    </> : <EmptyState title={t('noRequestsFound')} description={appliedSearch ? t('changeFilters') : t('requestWillAppear')} action={<Link to="/requests/new"><Button variant="primary"><Plus size={16} />{t('createRequest')}</Button></Link>} />}
  </div>;
}
