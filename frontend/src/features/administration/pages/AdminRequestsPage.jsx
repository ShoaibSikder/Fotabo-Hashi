import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Check, Droplet, HeartPulse, Search, Trash2, X } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import Button from '../../../components/ui/Button.jsx';
import FilterMenu from '../../../components/ui/FilterMenu.jsx';
import ResponsiveDetailPanel from '../../../components/ui/ResponsiveDetailPanel.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { apiDelete, apiGet, apiPatch } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

const emptyForm = { blood_group: '', required_units: 1, location: '', description: '', status: 'ACTIVE' };

export default function AdminRequestsPage() {
  const { t } = useLang();
  const [searchParams] = useSearchParams();
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [groupFilter, setGroupFilter] = useState('');
  const [searchText, setSearchText] = useState(() => searchParams.get('search') || '');
  const [search, setSearch] = useState(() => searchParams.get('search') || '');
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    let mounted = true;
    const params = new URLSearchParams({ page: String(page) });
    if (statusFilter) params.set('status', statusFilter);
    if (groupFilter) params.set('blood_group', groupFilter);
    if (search) params.set('search', search);
    setLoading(true);
    apiGet(`${API_ENDPOINTS.adminBloodRequests}?${params}`)
      .then((data) => {
        if (!mounted) return;
        const results = Array.isArray(data) ? data : data?.results || [];
        setRows(results);
        setCount(Array.isArray(data) ? data.length : data?.count || 0);
        setSelected((current) => current ? results.find((row) => row.id === current.id) || current : null);
      })
      .catch((err) => mounted && setError(err.message))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, [page, statusFilter, groupFilter, search]);

  useEffect(() => {
    setForm(selected ? {
      blood_group: selected.blood_group || '',
      required_units: selected.required_units || 1,
      location: selected.location || '',
      description: selected.description || '',
      status: selected.status || 'ACTIVE',
    } : emptyForm);
  }, [selected]);

  async function saveRequest(event) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true); setError(''); setNotice('');
    try {
      const updated = await apiPatch(API_ENDPOINTS.adminBloodRequestDetail(selected.id), {
        ...form,
        required_units: Number(form.required_units),
      });
      setRows((current) => current.map((row) => row.id === updated.id ? updated : row));
      setSelected(updated);
      setNotice(t('requestSaved'));
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  }

  async function deleteRequest() {
    if (!selected || !window.confirm(t('confirmDeleteRequest'))) return;
    try {
      await apiDelete(API_ENDPOINTS.adminBloodRequestDetail(selected.id));
      setRows((current) => current.filter((row) => row.id !== selected.id));
      setCount((current) => Math.max(0, current - 1));
      setSelected(null);
      setNotice(t('requestDeleted'));
    } catch (err) { setError(err.message); }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('bloodRequests')}</h1></div>
      {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {notice && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}

      <div className="grid items-start gap-5 2xl:grid-cols-[1.15fr_.85fr]">
        <Card className="!border-slate-200 !bg-white !p-4 !shadow-sm sm:!p-5">
          <form onSubmit={(event) => { event.preventDefault(); setPage(1); setSearch(searchText.trim()); }} className="flex w-full items-center gap-2">
            <div className="relative min-w-0 flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input aria-label={t('searchRequestHint')} value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder={t('searchRequestHint')} className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-800 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/10" /></div>
            <Button type="submit" aria-label={t('search')} className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !bg-slate-50 !px-0 !shadow-none sm:!w-auto sm:!px-4"><Search size={17} aria-hidden="true" /><span className="sr-only sm:not-sr-only">{t('search')}</span></Button>
            <FilterMenu
              activeCount={[statusFilter, groupFilter].filter(Boolean).length}
              onClear={() => { setStatusFilter(''); setGroupFilter(''); setPage(1); }}
            >
              <Select id="admin-request-status" label={t('status')} value={statusFilter} onChange={(event) => { setStatusFilter(event.target.value); setPage(1); }}><option value="">{t('allStatuses')}</option><option value="ACTIVE">{t('active')}</option><option value="FULFILLED">{t('fulfilled')}</option><option value="CANCELLED">{t('cancelled')}</option></Select>
              <Select id="admin-request-group" label={t('bloodGroup')} value={groupFilter} onChange={(event) => { setGroupFilter(event.target.value); setPage(1); }}><option value="">{t('allBloodGroups')}</option>{BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}</Select>
            </FilterMenu>
          </form>
          {loading ? <div className="py-12"><Spinner label="Loading blood requests…" /></div> : rows.length ? <>
            <div className="mt-4 overflow-x-auto rounded-xl border border-slate-100" role="region" aria-label={t('bloodRequests')} tabIndex="0"><table className="w-full min-w-[1120px] whitespace-nowrap text-left text-sm"><thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100"><th scope="col" className="px-3 py-3">{t('requestedBy')}</th><th scope="col" className="px-3 py-3">{t('bloodGroup')}</th><th scope="col" className="px-3 py-3">{t('phoneNumber')}</th><th scope="col" className="px-3 py-3">{t('bloodGroupNeeded')}</th><th scope="col" className="px-3 py-3">{t('units')}</th><th scope="col" className="px-3 py-3">{t('hospitalArea')}</th><th scope="col" className="px-3 py-3">{t('status')}</th><th scope="col" className="px-3 py-3">{t('actions')}</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id} className={`border-b border-slate-100 last:border-0 hover:bg-slate-50/70 ${selected?.id === row.id ? 'bg-rose-50/70' : ''}`}><td className="px-3 py-3 font-semibold text-slate-700">{row.requester_name || t('communityDonor')}</td><td className="px-3 py-3 text-slate-600">{row.requester_blood_group || '—'}</td><td className="px-3 py-3 text-slate-600">{row.requester_phone || '—'}</td><td className="px-3 py-3 font-extrabold text-brand">{row.blood_group}</td><td className="px-3 py-3">{row.required_units}</td><td className="max-w-[240px] truncate px-3 py-3 text-slate-600" title={row.location || ''}>{row.location || '—'}</td><td className="px-3 py-3"><span className={`rounded-full px-2.5 py-1 text-[11px] font-extrabold ${row.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700' : row.status === 'FULFILLED' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500'}`}>{t(row.status === 'ACTIVE' ? 'active' : row.status === 'FULFILLED' ? 'fulfilled' : 'cancelled')}</span></td><td className="px-3 py-3"><Button type="button" variant="secondary" onClick={() => { setSelected(row); setNotice(''); }} className="!min-h-9 !rounded-lg !px-3">{t('viewDetails')}</Button></td></tr>)}</tbody></table></div>
            <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
          </> : <div className="py-12 text-center"><HeartPulse className="mx-auto text-slate-300" size={28} /><p className="mt-3 text-sm font-bold text-slate-700">No blood requests found</p><p className="mt-1 text-xs text-slate-500">Try clearing or changing the filters.</p></div>}
        </Card>

        <ResponsiveDetailPanel open={Boolean(selected)} onClose={() => setSelected(null)} label={t('requestDetails')}>
        <Card className="!border-0 !bg-white !p-0 !shadow-none 2xl:!border-slate-200 2xl:!p-5 2xl:!shadow-sm">
          <div className="mb-5 flex items-start justify-between gap-4"><h2 className="font-heading text-lg font-extrabold text-slate-900">{t('requestDetails')}</h2>{selected && <button type="button" onClick={() => setSelected(null)} className="grid h-8 w-8 cursor-pointer place-items-center rounded-lg text-slate-400 hover:bg-slate-100" aria-label={t('clearSelectedRequest')}><X size={17} /></button>}</div>
          {selected ? <form className="space-y-4" onSubmit={saveRequest}>
            <div className="rounded-xl bg-slate-50 p-3"><p className="text-[10px] font-extrabold uppercase tracking-wide text-slate-400">{t('requestedBy')}</p><p className="mt-1 text-sm font-bold text-slate-800">{selected.requester_name || t('communityDonor')}</p><p className="text-xs text-slate-600">{selected.requester_blood_group || '—'} · {selected.requester_phone || '—'}</p></div>
            <div className="grid gap-4 sm:grid-cols-2"><Select id="admin-request-edit-group" label="Blood group" value={form.blood_group} onChange={(event) => setForm((current) => ({ ...current, blood_group: event.target.value }))}>{BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}</Select><Input id="admin-request-edit-units" label="Units" type="number" min="1" value={form.required_units} onChange={(event) => setForm((current) => ({ ...current, required_units: event.target.value }))} /></div>
            <Input id="admin-request-edit-location" label={t('hospitalArea')} value={form.location} onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))} />
            <Select id="admin-request-edit-status" label={t('requestStatus')} value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value }))}><option value="ACTIVE">{t('active')}</option><option value="FULFILLED">{t('fulfilled')}</option><option value="CANCELLED">{t('cancelled')}</option></Select>
            <label htmlFor="admin-request-edit-description" className="field-label">{t('details')}</label><textarea id="admin-request-edit-description" rows="4" value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} className="field-control min-h-24 w-full resize-y" />
            <div className="flex flex-wrap justify-between gap-3"><Button type="button" onClick={deleteRequest} className="!rounded-xl !text-red-700"><Trash2 size={16} /> {t('deleteRequest')}</Button><Button type="submit" variant="primary" loading={saving} className="!rounded-xl"><Check size={16} /> {t('save')}</Button></div>
          </form> : <div className="grid min-h-64 place-items-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center"><div><HeartPulse className="mx-auto text-slate-300" size={30} /><p className="mt-3 text-sm font-bold text-slate-700">{t('selectRequest')}</p></div></div>}
        </Card>
        </ResponsiveDetailPanel>
      </div>
    </div>
  );
}
