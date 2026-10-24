import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import Textarea from '../../../components/ui/Textarea.jsx';
import Button from '../../../components/ui/Button.jsx';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { apiPost } from '../../../services/apiClient.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function CreateRequestPage() {
  const navigate = useNavigate();
  const { t } = useLang();
  const [form, setForm] = useState({ blood_group: '', required_units: 1, location: '', description: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const change = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const result = await apiPost(API_ENDPOINTS.requests, { ...form, required_units: Number(form.required_units) });
      navigate(`/requests/${result.id || ''}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return <div className="page-enter mx-auto max-w-3xl space-y-5">
    <Link to="/requests" className="inline-flex items-center gap-2 text-sm font-bold text-muted hover:text-brand"><ArrowLeft size={16} />{t('backToRequests')}</Link>
    <h1 className="text-3xl font-extrabold text-brand-dark">{t('createBloodRequest')}</h1>
    <Card><form className="space-y-5" onSubmit={submit}>{error && <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      <div className="grid gap-5 sm:grid-cols-2"><Select id="blood_group" name="blood_group" label={t('bloodGroupNeeded')} required value={form.blood_group} onChange={change}><option value="">{t('selectBloodGroup')}</option>{BLOOD_GROUPS.map((group) => <option key={group}>{group}</option>)}</Select><Input id="required_units" name="required_units" type="number" label={t('unitsNeeded')} min="1" required value={form.required_units} onChange={change} /></div>
      <Input id="location" name="location" label={t('hospitalArea')} required placeholder={t('hospitalCityHint')} value={form.location} onChange={change} />
      <Textarea id="description" name="description" label={t('additionalDetails')} rows="5" placeholder={t('requestContextHint')} value={form.description} onChange={change} />
      <p className="text-xs leading-5 text-muted">{t('patientPrivacyNote')}</p>
      <div className="flex justify-end"><Button type="submit" variant="primary" loading={busy}><Send size={16} />{t('publishRequest')}</Button></div>
    </form></Card>
  </div>;
}
