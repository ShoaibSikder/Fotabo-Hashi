import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, CalendarDays, Check, Droplet, MapPin, Pencil, Save, X } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import Badge from '../../../components/ui/Badge.jsx';
import Spinner from '../../../components/ui/Spinner.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import Textarea from '../../../components/ui/Textarea.jsx';
import Button from '../../../components/ui/Button.jsx';
import { apiGet, apiPatch, apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function RequestDetailsPage() {
  const { t } = useLang();
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);
  const [working, setWorking] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    let active = true;
    apiGet(API_ENDPOINTS.requestDetail(id))
      .then((data) => {
        if (!active) return;
        setItem(data);
        setForm({
          blood_group: data.blood_group,
          required_units: data.required_units,
          location: data.location,
          description: data.description || '',
        });
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setBusy(false));
    return () => { active = false; };
  }, [id]);

  function change(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function save(event) {
    event.preventDefault();
    setWorking(true);
    setError('');
    try {
      const result = await apiPatch(API_ENDPOINTS.requestDetail(id), {
        ...form,
        required_units: Number(form.required_units),
      });
      setItem(result);
      setEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setWorking(false);
    }
  }

  async function action(name) {
    const label = t(name === 'cancel' ? 'cancel' : 'markFulfilled');
    if (!window.confirm(t('confirmAction', { action: label }))) return;
    setWorking(true);
    setError('');
    try {
      const endpoint = name === 'cancel'
        ? API_ENDPOINTS.requestCancel(id)
        : API_ENDPOINTS.requestFulfill(id);
      setItem(await apiPost(endpoint, {}));
    } catch (err) {
      setError(err.message);
    } finally {
      setWorking(false);
    }
  }

  return (
    <div className="page-enter mx-auto max-w-3xl space-y-5">
      <Link to="/requests" className="inline-flex items-center gap-2 text-sm font-bold text-muted hover:text-brand">
        <ArrowLeft size={16} /> {t('allRequests')}
      </Link>
      {busy ? (
        <div className="py-12 text-center"><Spinner label="Loading request…" /></div>
      ) : error && !item ? (
        <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</div>
      ) : item && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h1 className="text-3xl font-extrabold text-brand-dark">Request details</h1>
            {item.is_owner && item.status === 'ACTIVE' && !editing && (
              <Button onClick={() => setEditing(true)}><Pencil size={16} /> Edit request</Button>
            )}
          </div>
          {error && <p role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">{error}</p>}
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Badge tone={item.status === 'ACTIVE' ? 'red' : item.status === 'FULFILLED' ? 'green' : 'neutral'}>{item.status}</Badge>
              <span className="text-sm text-muted">Request #{item.id}</span>
            </div>
            {editing ? (
              <form onSubmit={save} className="mt-6 space-y-5">
                <div className="grid gap-5 sm:grid-cols-2">
                  <Select id="edit-group" name="blood_group" label="Blood group" required value={form.blood_group} onChange={change}>
                    {BLOOD_GROUPS.map((group) => <option key={group}>{group}</option>)}
                  </Select>
                  <Input id="edit-units" name="required_units" type="number" min="1" label="Units needed" required value={form.required_units} onChange={change} />
                </div>
                <Input id="edit-location" name="location" label="Hospital / area" required value={form.location} onChange={change} />
                <Textarea id="edit-description" name="description" label="Additional details" rows="4" value={form.description} onChange={change} />
                <div className="flex justify-end gap-2">
                  <Button onClick={() => setEditing(false)}><X size={16} /> Cancel</Button>
                  <Button type="submit" variant="primary" loading={working}><Save size={16} /> Save changes</Button>
                </div>
              </form>
            ) : (
              <>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <Detail icon={<Droplet />} label="Blood group" value={item.blood_group} />
                  <Detail icon={<Droplet />} label="Units needed" value={item.required_units || 1} />
                  <Detail icon={<MapPin />} label="Location" value={item.location || 'Not listed'} />
                  {item.created_at && <Detail icon={<CalendarDays />} label="Posted" value={new Date(item.created_at).toLocaleDateString()} />}
                </div>
                {item.description && (
                  <div className="mt-6 border-t border-brand-dark/10 pt-5">
                    <h2 className="font-extrabold text-brand-dark">Additional details</h2>
                    <p className="mt-2 whitespace-pre-wrap leading-7 text-muted">{item.description}</p>
                  </div>
                )}
                <p className="mt-6 rounded-xl bg-brand-soft p-4 text-sm leading-6 text-brand-dark">
                  The app does not display contact information or provide an in-app contact request. Use the hospital or care team’s coordination channel.
                </p>
                {item.is_owner && item.status === 'ACTIVE' && (
                  <div className="mt-5 flex flex-wrap justify-end gap-3 border-t border-brand-dark/10 pt-5">
                    <Button onClick={() => action('cancel')} disabled={working}><X size={16} /> Cancel request</Button>
                    <Button variant="primary" onClick={() => action('fulfill')} loading={working}><Check size={16} /> Mark fulfilled</Button>
                  </div>
                )}
              </>
            )}
          </Card>
        </>
      )}
    </div>
  );
}

function Detail({ icon, label, value }) {
  return (
    <div className="rounded-xl bg-white/45 p-4">
      <div className="flex items-center gap-2 text-brand">{icon}<span className="text-xs font-bold uppercase tracking-wide text-muted">{label}</span></div>
      <p className="mt-2 font-extrabold text-ink">{value}</p>
    </div>
  );
}
