import { useState } from 'react';
import { ArrowRight, Eye, EyeOff } from 'lucide-react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import Card from '../../../components/ui/Card.jsx';
import Button from '../../../components/ui/Button.jsx';
import Input from '../../../components/ui/Input.jsx';
import Select from '../../../components/ui/Select.jsx';
import { useAuthCtx } from '../../../contexts/AuthContext.jsx';
import { BLOOD_GROUPS } from '../../../utils/constants.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import { warmCsrfToken } from '../../../services/apiClient.js';

export default function RegisterPage() {
  const { register, user } = useAuthCtx();
  const { t } = useLang();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', phone: '', blood_group: '', password: '', confirmPassword: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  function change(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) {
      setError(t('passwordMismatch'));
      return;
    }

    setBusy(true);
    try {
      // The API accepts name, email, and password. Confirmation is client-side only.
      await register({
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        blood_group: form.blood_group,
        password: form.password,
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell grid min-h-[68vh] place-items-center py-12">
      <Card className="w-full max-w-xl p-7 sm:p-9">
        <p className="eyebrow">Fotabo Hashi</p>
        <h1 className="mt-2 text-3xl font-extrabold text-brand-dark">{t('createYourAccount')}</h1>

        <form onSubmit={submit} className="mt-7 space-y-5">
          {error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}
          <Input
            id="name"
            name="name"
            label={`${t('fullName')} *`}
            autoComplete="name"
            required
            maxLength={150}
            placeholder="e.g. Shoaib Sikder"
            value={form.name}
            onFocus={warmCsrfToken}
            onChange={change}
          />
          <Input
            id="email"
            name="email"
            label={`${t('emailAddress')} *`}
            type="email"
            autoComplete="email"
            required
            placeholder="e.g. name@example.com"
            value={form.email}
            onChange={change}
          />
          <Input
            id="phone"
            name="phone"
            label={`${t('phoneNumber')} *`}
            type="tel"
            autoComplete="tel"
            required
            maxLength={30}
            placeholder="e.g. +880 1712-345678"
            value={form.phone}
            onChange={change}
          />
          <Select
            id="blood_group"
            name="blood_group"
            label={`${t('bloodGroup')} *`}
            autoComplete="off"
            required
            value={form.blood_group}
            onChange={change}
          >
            <option value="" disabled>{t('selectBloodGroup')}</option>
            {BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}
          </Select>
          <div className="relative">
            <Input
              id="password"
              name="password"
              label={`${t('password')} *`}
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              minLength={8}
              placeholder="At least 8 characters"
              inputClassName="pr-12"
              value={form.password}
              onChange={change}
            />
            <button type="button" onClick={() => setShowPassword((shown) => !shown)} aria-label={t(showPassword ? 'hidePassword' : 'showPassword')} aria-pressed={showPassword} className="absolute right-2 top-[1.95rem] grid h-9 w-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand"><span className="sr-only">{t(showPassword ? 'hidePassword' : 'showPassword')}</span>{showPassword ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}</button>
          </div>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              label={t('confirmPassword')}
              type={showConfirmPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              placeholder="Re-enter your password"
              inputClassName="pr-12"
              value={form.confirmPassword}
              onChange={change}
            />
            <button type="button" onClick={() => setShowConfirmPassword((shown) => !shown)} aria-label={t(showConfirmPassword ? 'hidePassword' : 'showPassword')} aria-pressed={showConfirmPassword} className="absolute right-2 top-[1.95rem] grid h-9 w-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand"><span className="sr-only">{t(showConfirmPassword ? 'hidePassword' : 'showPassword')}</span>{showConfirmPassword ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}</button>
          </div>
          <Button type="submit" variant="primary" loading={busy} className="w-full !rounded-full">
            {t('register')} <ArrowRight size={17} />
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already registered? <Link className="font-extrabold text-brand hover:underline" to="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
