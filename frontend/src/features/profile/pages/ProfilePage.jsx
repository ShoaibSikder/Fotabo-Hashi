import { useEffect, useState } from 'react';
import { Save, UserRound } from 'lucide-react';
import { useAuthCtx } from '../../../contexts/AuthContext.jsx';
import Avatar from '../../../components/ui/Avatar.jsx';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import Button from '../../../components/ui/Button.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiGet, apiPatch } from '../../../services/apiClient.js';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function ProfilePage() {
  const { user } = useAuthCtx();
  const { t } = useLang();
  const [form, setForm] = useState({});
  const [busy, setBusy] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet(API_ENDPOINTS.profile)
      .then((data) => setForm(data || {}))
      .catch((err) => setError(err.message))
      .finally(() => setBusy(false));
  }, []);

  function change(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true); setMessage(''); setError('');
    try {
      const payload = {};
      ['name', 'phone', 'blood_group', 'location', 'is_available_for_donation', 'self_reported_donation_count'].forEach((key) => {
        const value = form[key];
        if (value !== undefined && value !== null) payload[key] = value;
      });
      const result = await apiPatch(API_ENDPOINTS.profile, payload);
      setForm(result || form); setMessage(t('profileUpdated'));
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  }

  return <div className="page-enter mx-auto max-w-3xl space-y-6">
    <div><h1 className="text-3xl font-extrabold text-brand-dark">{t('profile')}</h1></div>
    {busy ? <div className="py-10 text-center"><Spinner label="Loading your profile…" /></div> : <Card>
      <div className="mb-6 flex items-center gap-4"><Avatar name={form.name || user?.email} size="lg"/><div><h2 className="font-extrabold text-brand-dark">{form.name || user?.email}</h2><p className="text-sm text-muted">{user?.email}</p></div></div>
      <form onSubmit={submit} className="space-y-5">
        {message && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{message}</p>}
        {error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}
        <div className="grid gap-5 sm:grid-cols-2"><Input id="name" name="name" label={t('fullName')} value={form.name || ''} onChange={change} autoComplete="name"/><Input id="phone" name="phone" label={t('phoneNumber')} type="tel" value={form.phone || ''} onChange={change} autoComplete="tel"/></div>
        <div className="grid gap-5 sm:grid-cols-2"><Select id="blood_group" name="blood_group" label={t('bloodGroup')} value={form.blood_group || ''} onChange={change}><option value="">{t('selectBloodGroup')}</option>{BLOOD_GROUPS.map((group) => <option key={group}>{group}</option>)}</Select><Input id="location" name="location" label={t('areaCity')} value={form.location || ''} onChange={change} autoComplete="address-level2"/></div>
        <Input id="self_reported_donation_count" name="self_reported_donation_count" label={t('selfReportedDonationCount')} type="number" min="0" step="1" inputMode="numeric" value={form.self_reported_donation_count ?? 0} onChange={change} hint={t('selfReportedDonationHint')} />
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm">
          <span className="font-semibold text-slate-600">{t('approvedLeaderboardCount')}</span>
          <span className="font-extrabold text-brand-dark">{form.approved_donation_count ?? 0}</span>
          {form.donation_count_review_status === 'PENDING' && <span className="w-full text-xs font-semibold text-amber-700">{t('donationCountPending')}</span>}
          {form.donation_count_review_status === 'REJECTED' && <span className="w-full text-xs font-semibold text-red-700">{t('donationCountRejected')}</span>}
        </div>
        <label className="flex items-start gap-3 rounded-xl bg-white/45 p-4"><input className="mt-1 accent-red-700" type="checkbox" name="is_available_for_donation" checked={Boolean(form.is_available_for_donation)} onChange={(event) => setForm((current) => ({ ...current, is_available_for_donation: event.target.checked }))}/><span><span className="block font-bold text-ink">Available to donate</span><span className="mt-1 block text-sm text-muted">Let the donor directory know you may be available.</span></span></label>
        <div className="flex justify-end"><Button type="submit" variant="primary" loading={saving}><Save size={16}/> {t('save')}</Button></div>
      </form>
    </Card>}
  </div>;
}
