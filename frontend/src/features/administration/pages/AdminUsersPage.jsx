import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CalendarDays, Check, Droplet, Plus, Search, Shield, Trash2, UserRound, X } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import Button from '../../../components/ui/Button.jsx';
import FilterMenu from '../../../components/ui/FilterMenu.jsx';
import ResponsiveDetailPanel from '../../../components/ui/ResponsiveDetailPanel.jsx';
import Pagination from '../../../components/ui/Pagination.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { apiDelete, apiGet, apiPatch, apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

const emptyForm = { email: '', role: 'USER', is_active: true, name: '', phone: '', blood_group: '', location: '', is_available_for_donation: false };
const newAccountForm = { email: '', role: 'USER', name: '', phone: '', blood_group: '', location: '' };

export default function AdminUsersPage() {
  const { t } = useLang();
  const [searchParams] = useSearchParams();
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [searchText, setSearchText] = useState(() => searchParams.get('search') || '');
  const [search, setSearch] = useState(() => searchParams.get('search') || '');
  const [role, setRole] = useState('');
  const [active, setActive] = useState('');
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState(newAccountForm);
  const [createSaving, setCreateSaving] = useState(false);
  const [bloodGroup, setBloodGroup] = useState('');
  const [donationRecords, setDonationRecords] = useState([]);
  const [donationsLoading, setDonationsLoading] = useState(false);
  const [donationSaving, setDonationSaving] = useState(false);
  const [donationError, setDonationError] = useState('');
  const [donationForm, setDonationForm] = useState({ donated_on: new Date().toISOString().slice(0, 10), notes: '' });

  useEffect(() => {
    let mounted = true;
    const params = new URLSearchParams({ page: String(page) });
    if (search) params.set('search', search);
    if (role) params.set('role', role);
    if (active) params.set('active', active);
    if (bloodGroup) params.set('blood_group', bloodGroup);
    setLoading(true);
    apiGet(`${API_ENDPOINTS.adminUsers}?${params}`)
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
  }, [page, search, role, active, bloodGroup]);

  useEffect(() => {
    setForm(selected ? { ...emptyForm, ...selected } : emptyForm);
  }, [selected]);

  const selectedUserId = selected?.id;
  const selectedUserRole = selected?.role;

  useEffect(() => {
    if (!selectedUserId || selectedUserRole !== 'USER') {
      setDonationRecords([]);
      setDonationError('');
      return undefined;
    }
    let mounted = true;
    setDonationsLoading(true);
    apiGet(API_ENDPOINTS.adminUserDonations(selectedUserId))
      .then((data) => mounted && setDonationRecords(Array.isArray(data) ? data : data?.results || []))
      .catch((err) => mounted && setDonationError(err.message))
      .finally(() => mounted && setDonationsLoading(false));
    return () => { mounted = false; };
  }, [selectedUserId, selectedUserRole]);

  function selectUser(user) {
    setSelected(user);
    setNotice('');
    setError('');
  }

  function updateField(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({ ...current, [name]: type === 'checkbox' ? checked : value }));
  }

  async function saveUser(event) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true);
    setError('');
    setNotice('');
    try {
      const updated = await apiPatch(API_ENDPOINTS.adminUserDetail(selected.id), form);
      setRows((current) => current.map((row) => row.id === updated.id ? updated : row));
      setSelected(updated);
      setNotice(t('accountSaved'));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function createUser(event) {
    event.preventDefault();
    setCreateSaving(true);
    setError('');
    setNotice('');
    try {
      const created = await apiPost(API_ENDPOINTS.adminUsers, createForm);
      setRows((current) => [created, ...current].slice(0, 20));
      setCount((current) => current + 1);
      setCreating(false);
      setCreateForm(newAccountForm);
      setNotice(t(created.password_setup_sent ? 'accountCreatedEmailSent' : 'accountCreatedEmailFailed'));
    } catch (err) {
      setError(err.message);
    } finally {
      setCreateSaving(false);
    }
  }

  async function recordDonation(event) {
    event.preventDefault();
    if (!selected) return;
    setDonationSaving(true);
    setDonationError('');
    try {
      const created = await apiPost(API_ENDPOINTS.adminUserDonations(selected.id), donationForm);
      setDonationRecords((current) => [created, ...current]);
      const updated = { ...selected, donation_count: (selected.donation_count || 0) + 1 };
      setSelected(updated);
      setRows((current) => current.map((row) => row.id === updated.id ? updated : row));
      setDonationForm({ donated_on: new Date().toISOString().slice(0, 10), notes: '' });
      setNotice(t('donationRecorded'));
    } catch (err) {
      setDonationError(err.message);
    } finally {
      setDonationSaving(false);
    }
  }

  async function removeDonation(record) {
    if (!selected || !window.confirm(t('confirmRemoveDonation'))) return;
    setDonationError('');
    try {
      await apiDelete(API_ENDPOINTS.adminUserDonationDetail(selected.id, record.id));
      setDonationRecords((current) => current.filter((item) => item.id !== record.id));
      const updated = { ...selected, donation_count: Math.max(0, (selected.donation_count || 0) - 1) };
      setSelected(updated);
      setRows((current) => current.map((row) => row.id === updated.id ? updated : row));
    } catch (err) {
      setDonationError(err.message);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3"><h1 className="font-heading text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{t('peopleAndDonors')}</h1><Button type="button" variant="primary" className="!rounded-xl" onClick={() => { setCreating(true); setSelected(null); setError(''); setNotice(''); }}><Plus size={16} /> {t('addUser')}</Button></div>
      {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {notice && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}

      <div className="grid items-start gap-5 2xl:grid-cols-[1.15fr_.85fr]">
        <Card className="!border-slate-200 !bg-white !p-4 !shadow-sm sm:!p-5">
          <form onSubmit={(event) => { event.preventDefault(); setPage(1); setSearch(searchText.trim()); }} className="flex w-full items-center gap-2">
            <div className="relative min-w-0 flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input aria-label={t('searchPeopleHint')} value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder={t('searchPeopleHint')} className="min-h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-800 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/10" /></div>
            <Button type="submit" aria-label={t('search')} className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !bg-slate-50 !px-0 !shadow-none sm:!w-auto sm:!px-4"><Search size={17} aria-hidden="true" /><span className="sr-only sm:not-sr-only">{t('search')}</span></Button>
            <FilterMenu
              activeCount={[role, active, bloodGroup].filter(Boolean).length}
              onClear={() => { setRole(''); setActive(''); setBloodGroup(''); setPage(1); }}
            >
              <Select id="admin-user-role" label={t('adminRole')} value={role} onChange={(event) => { setRole(event.target.value); setPage(1); }}><option value="">{t('allRoles')}</option><option value="USER">{t('userRole')}</option><option value="ADMIN">{t('adminRole')}</option></Select>
              <Select id="admin-user-status" label={t('status')} value={active} onChange={(event) => { setActive(event.target.value); setPage(1); }}><option value="">{t('allAccountStatuses')}</option><option value="true">{t('active')}</option><option value="false">{t('disabled')}</option></Select>
              <Select id="admin-user-blood-filter" label={t('bloodGroup')} value={bloodGroup} onChange={(event) => { setBloodGroup(event.target.value); setPage(1); }}><option value="">{t('allGroups')}</option>{BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}</Select>
            </FilterMenu>
          </form>
          {loading ? <div className="py-12"><Spinner label="Loading accounts…" /></div> : rows.length ? <>
            <div className="mt-4 overflow-x-auto rounded-xl border border-slate-100" role="region" aria-label={t('peopleAndDonors')} tabIndex="0"><table className="w-full min-w-[1160px] whitespace-nowrap text-left text-sm"><thead className="bg-slate-50 text-[10px] font-extrabold uppercase tracking-wide text-slate-500"><tr className="border-b border-slate-100"><th scope="col" className="px-3 py-3">{t('fullName')}</th><th scope="col" className="px-3 py-3">{t('bloodGroup')}</th><th scope="col" className="px-3 py-3">{t('phoneNumber')}</th><th scope="col" className="px-3 py-3">{t('adminRole')}</th><th scope="col" className="px-3 py-3">{t('status')}</th><th scope="col" className="px-3 py-3">{t('donor')}</th><th scope="col" className="px-3 py-3">{t('approvedLeaderboardCount')}</th><th scope="col" className="px-3 py-3">{t('actions')}</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id} className={`border-b border-slate-100 last:border-0 hover:bg-slate-50/70 ${selected?.id === row.id ? 'bg-rose-50/70' : ''}`}><td className="px-3 py-3 font-bold text-slate-800">{row.name || t('communityDonor')}</td><td className="px-3 py-3 text-slate-600">{row.blood_group || '—'}</td><td className="px-3 py-3 text-slate-600">{row.phone || '—'}</td><td className="px-3 py-3"><span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-bold text-slate-700">{row.role === 'ADMIN' && <Shield size={12} />}{t(row.role === 'ADMIN' ? 'adminRole' : 'userRole')}</span></td><td className="px-3 py-3"><span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${row.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{t(row.is_active ? 'active' : 'disabled')}</span></td><td className="px-3 py-3 text-xs font-semibold text-slate-600">{t(row.is_available_for_donation ? 'available' : 'notSpecified')}</td><td className="px-3 py-3 text-xs font-extrabold text-brand">{row.donation_count || 0}</td><td className="px-3 py-3"><Button type="button" variant="secondary" onClick={() => selectUser(row)} className="!min-h-9 !rounded-lg !px-3">{t('viewDetails')}</Button></td></tr>)}</tbody></table></div>
            <div className="mt-4"><Pagination page={page} count={count} onChange={setPage} /></div>
          </> : <div className="py-12 text-center"><UserRound className="mx-auto text-slate-300" size={28} /><p className="mt-3 text-sm font-bold text-slate-700">No accounts found</p><p className="mt-1 text-xs text-slate-500">Adjust the search or filters and try again.</p></div>}
        </Card>

        <ResponsiveDetailPanel open={Boolean(selected || creating)} onClose={() => { setSelected(null); setCreating(false); }} label={creating ? t('newAccount') : t('accountDetails')}>
        <Card className="!border-0 !bg-white !p-0 !shadow-none 2xl:!border-slate-200 2xl:!p-5 2xl:!shadow-sm">
          <div className="mb-5 flex items-start justify-between gap-4"><h2 className="font-heading text-lg font-extrabold text-slate-900">{creating ? t('newAccount') : t('accountDetails')}</h2>{(selected || creating) && <button type="button" onClick={() => { setSelected(null); setCreating(false); }} className="grid h-8 w-8 cursor-pointer place-items-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label={t('close')}><X size={17} /></button>}</div>
          {creating ? <form className="space-y-4" onSubmit={createUser}>
            <Input id="admin-new-email" label={t('emailAddress')} type="email" required value={createForm.email} onChange={(event) => setCreateForm((current) => ({ ...current, email: event.target.value }))} />
            <Input id="admin-new-name" label={t('fullName')} required value={createForm.name} onChange={(event) => setCreateForm((current) => ({ ...current, name: event.target.value }))} />
            <div className="grid gap-4 sm:grid-cols-2"><Input id="admin-new-phone" label={t('phoneNumber')} required value={createForm.phone} onChange={(event) => setCreateForm((current) => ({ ...current, phone: event.target.value }))} /><Select id="admin-new-blood" label={t('bloodGroup')} required value={createForm.blood_group} onChange={(event) => setCreateForm((current) => ({ ...current, blood_group: event.target.value }))}><option value="">{t('selectBloodGroup')}</option>{BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}</Select></div>
            <Input id="admin-new-location" label="Location" value={createForm.location} onChange={(event) => setCreateForm((current) => ({ ...current, location: event.target.value }))} />
            <Select id="admin-new-role" label="Role" value={createForm.role} onChange={(event) => setCreateForm((current) => ({ ...current, role: event.target.value }))}><option value="USER">User</option><option value="ADMIN">Admin</option></Select>
            <Button type="submit" variant="primary" loading={createSaving} className="w-full !rounded-xl"><Plus size={16} /> {t('createAccount')}</Button>
          </form> : selected ? <form className="space-y-4" onSubmit={saveUser}>
            <Input id="admin-user-email" name="email" label={t('emailAddress')} type="email" required value={form.email} onChange={updateField} />
            <Input id="admin-user-name" name="name" label={t('fullName')} value={form.name} onChange={updateField} />
            <div className="grid gap-4 sm:grid-cols-2"><Select id="admin-user-role-edit" name="role" label={t('adminRole')} value={form.role} onChange={updateField}><option value="USER">{t('userRole')}</option><option value="ADMIN">{t('adminRole')}</option></Select><Input id="admin-user-phone" name="phone" label={t('phoneNumber')} value={form.phone} onChange={updateField} /></div>
            <div className="grid gap-4 sm:grid-cols-2"><Select id="admin-user-blood" name="blood_group" label={t('bloodGroup')} value={form.blood_group} onChange={updateField}><option value="">{t('notSpecified')}</option>{BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}</Select><Input id="admin-user-location" name="location" label={t('areaCity')} value={form.location} onChange={updateField} /></div>
            <label className="flex cursor-pointer items-center gap-3 rounded-xl bg-slate-50 p-3 text-sm font-semibold text-slate-700"><input type="checkbox" name="is_active" checked={Boolean(form.is_active)} onChange={updateField} className="h-4 w-4 accent-red-700" />Account is active</label>
            <label className="flex cursor-pointer items-center gap-3 rounded-xl bg-slate-50 p-3 text-sm font-semibold text-slate-700"><input type="checkbox" name="is_available_for_donation" checked={Boolean(form.is_available_for_donation)} onChange={updateField} className="h-4 w-4 accent-red-700" />Available for donation</label>
            <Button type="submit" variant="primary" loading={saving} className="w-full !rounded-xl"><Check size={16} /> Save account</Button>
          </form> : <div className="grid min-h-64 place-items-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center"><div><UserRound className="mx-auto text-slate-300" size={30} /><p className="mt-3 text-sm font-bold text-slate-700">Select an account</p></div></div>}
          {selected?.role === 'USER' && <section className="mt-7 border-t border-slate-100 pt-5">
            <div className="mb-4 flex items-center justify-between gap-3"><h3 className="font-heading font-extrabold text-slate-900">{t('verifiedDonations')}</h3><span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-3 py-1.5 text-sm font-extrabold text-brand"><Droplet size={14} />{selected.donation_count || 0}</span></div>
            <p className="mb-3 text-xs text-slate-600">{t('selfReportedDonationCount')}: <strong>{selected.self_reported_donation_count || 0}</strong></p>
            <p className="mb-4 text-xs text-slate-500">{t('verifiedDonationsAdminHelp')}</p>
            {notice && <p role="status" className="mb-3 rounded-lg bg-emerald-50 p-2 text-xs font-semibold text-emerald-800">{notice}</p>}
            {donationError && <p role="alert" className="mb-3 rounded-lg bg-red-50 p-2 text-xs text-red-800">{donationError}</p>}
            <form className="space-y-3 rounded-xl bg-slate-50 p-3" onSubmit={recordDonation}>
              <Input id="donated-on" label={t('donationDate')} type="date" max={new Date().toISOString().slice(0, 10)} required value={donationForm.donated_on} onChange={(event) => setDonationForm((current) => ({ ...current, donated_on: event.target.value }))} />
              <Input id="donation-notes" label={t('notesOptional')} maxLength={500} value={donationForm.notes} onChange={(event) => setDonationForm((current) => ({ ...current, notes: event.target.value }))} />
              <Button type="submit" variant="primary" loading={donationSaving} className="w-full !rounded-xl"><Plus size={15} />{t('recordDonation')}</Button>
            </form>
            <div className="mt-4 space-y-2">
              {donationsLoading ? <Spinner label={t('loadingDonations')} /> : donationRecords.length ? donationRecords.map((record) => <div key={record.id} className="flex items-center gap-3 rounded-xl border border-slate-100 p-3"><CalendarDays size={16} className="shrink-0 text-slate-400" /><div className="min-w-0 flex-1"><p className="text-sm font-bold text-slate-800">{record.donated_on}</p>{record.notes && <p className="mt-0.5 break-words text-xs text-slate-500">{record.notes}</p>}</div><button type="button" onClick={() => removeDonation(record)} className="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-red-600 hover:bg-red-50" aria-label={t('removeDonation')}><Trash2 size={15} /></button></div>) : <p className="py-3 text-center text-xs text-slate-500">{t('noDonationRecords')}</p>}
            </div>
          </section>}
        </Card>
        </ResponsiveDetailPanel>
      </div>
    </div>
  );
}
