import { useCallback, useEffect, useState } from 'react';
import { MapPin, Phone, Search } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Button from '../../../components/ui/Button.jsx';
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

export default function DonorSearchPage() {
  const { t } = useLang();
  const [searchTerm, setSearchTerm] = useState('');
  const [appliedSearch, setAppliedSearch] = useState('');
  const [bloodGroup, setBloodGroup] = useState('');
  const [page, setPage] = useState(1);
  const [donors, setDonors] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
    if (appliedSearch) query.set('search', appliedSearch);
    if (bloodGroup) query.set('blood_group', bloodGroup);
    try {
      const data = await apiGet(`${API_ENDPOINTS.donors}?${query}`);
      setDonors(Array.isArray(data) ? data : data?.results || []);
      setCount(data?.count ?? 0);
    } catch (err) {
      setError(err.message);
      setDonors([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, [appliedSearch, bloodGroup, page]);

  useEffect(() => { load(); }, [load]);

  function search(event) {
    event.preventDefault();
    setAppliedSearch(searchTerm.trim());
    setPage(1);
  }

  return <div className="page-enter space-y-6">
    <h1 className="text-2xl font-extrabold text-brand-dark sm:text-3xl">{t('findDonorsTitle')}</h1>
    <Card className="!p-4 sm:!p-5"><form className="flex w-full items-center gap-2" onSubmit={search}>
      <div className="relative min-w-0 flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input id="donor-search" aria-label={t('donorSearchLabel')} className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-800 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/10" placeholder={t('searchDonorsPlaceholder')} value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} /></div>
      <Button type="submit" variant="secondary" aria-label={t('search')} className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !px-0 sm:!w-auto sm:!px-4"><Search size={17} aria-hidden="true" /><span className="sr-only sm:not-sr-only">{t('search')}</span></Button>
      <FilterMenu activeCount={[bloodGroup].filter(Boolean).length} onClear={() => { setBloodGroup(''); setPage(1); }}>
        <Select id="donor-filter-group" label={t('bloodGroup')} value={bloodGroup} onChange={(event) => { setBloodGroup(event.target.value); setPage(1); }}><option value="">{t('allBloodGroups')}</option>{BLOOD_GROUPS.map((group) => <option key={group}>{group}</option>)}</Select>
      </FilterMenu>
    </form></Card>

    <div className="flex items-center justify-between"><h2 className="text-lg font-extrabold text-brand-dark">{t('availableDonors')}</h2>{!loading && <span className="text-sm text-muted">{t('foundCount', { count })}</span>}</div>
    {error && <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</div>}
    {loading ? <div className="py-12 text-center"><Spinner label={t('searchingDonors')} /></div> : donors.length ? <>
      <Card className="!p-0">
        <div className="overflow-x-auto rounded-2xl" role="region" aria-label={t('availableDonors')} tabIndex="0">
          <table className="w-full min-w-[940px] whitespace-nowrap text-left text-sm">
            <thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100">
              <th scope="col" className="px-4 py-3">{t('fullName')}</th><th scope="col" className="px-4 py-3">{t('bloodGroup')}</th><th scope="col" className="px-4 py-3">{t('phoneNumber')}</th><th scope="col" className="px-4 py-3">{t('areaCity')}</th><th scope="col" className="px-4 py-3">{t('status')}</th><th scope="col" className="px-4 py-3">{t('actions')}</th>
            </tr></thead>
            <tbody>{donors.map((donor) => <tr key={donor.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/70">
              <td className="px-4 py-3 font-bold text-slate-800">{donor.name || t('communityDonor')}</td>
              <td className="px-4 py-3"><span className="inline-flex items-center rounded-full bg-rose-50 px-2.5 py-1 text-xs font-extrabold text-brand">{donor.blood_group || t('bloodGroupNotListed')}</span></td>
              <td className="px-4 py-3 text-slate-600">{donor.phone || '—'}</td>
              <td className="px-4 py-3"><span className="inline-flex items-center gap-1.5 text-slate-600"><MapPin size={14} className="text-slate-400" />{donor.location || t('locationNotListed')}</span></td>
              <td className="px-4 py-3"><span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-700">{t('available')}</span></td>
              <td className="px-4 py-3">{donor.phone ? <a href={`tel:${donor.phone}`} className="inline-flex min-h-9 items-center gap-2 rounded-lg bg-brand px-3 text-xs font-bold text-white transition-colors hover:bg-brand-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"><Phone size={14} />{t('callDonor')}</a> : <span className="text-slate-400">—</span>}</td>
            </tr>)}</tbody>
          </table>
        </div>
      </Card>
      <Pagination page={page} pages={Math.max(1, Math.ceil(count / PAGE_SIZE))} onChange={setPage} />
    </> : !error && <EmptyState title={t('noDonorsFound')} description={t('broadenSearch')} />}
  </div>;
}
