import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import Card from '../../../components/ui/Card.jsx';
import Button from '../../../components/ui/Button.jsx';
import Input from '../../../components/ui/Input.jsx';
import { useAuthCtx } from '../../../contexts/AuthContext.jsx';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function LoginPage() {
  const { login, user } = useAuthCtx();
  const { t } = useLang();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (user) return <Navigate to={user.role === 'ADMIN' ? '/admin/dashboard' : location.state?.from || '/dashboard'} replace />;

  async function submit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await login({ email, password, remember_me: rememberMe });
    } catch (err) {
      setError(err.message || 'Sign-in failed. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell grid min-h-[68vh] place-items-center py-12">
      <Card className="w-full max-w-md p-7 sm:p-9">
        <p className="eyebrow">Fotabo Hashi</p>
        <h1 className="mt-2 text-3xl font-extrabold text-brand-dark">{t('login')}</h1>
        <form onSubmit={submit} className="mt-7 space-y-5">
          {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-800">{error}</div>}
          <Input id="email" label={t('emailAddress')} type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <Input id="password" label={t('password')} type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
            <label htmlFor="remember-me" className="inline-flex cursor-pointer items-center gap-2 font-medium text-muted">
              <input
                id="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
                className="h-4 w-4 cursor-pointer accent-brand focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
              />
              {t('rememberMe')}
            </label>
            <Link className="font-bold text-brand hover:underline" to="/forgot-password">{t('forgotPassword')}</Link>
          </div>
          <Button type="submit" variant="primary" loading={busy} className="w-full !rounded-full">{t('login')} <ArrowRight size={17} /></Button>
        </form>
        <p className="mt-6 text-center text-sm text-muted">
          Don’t have an account? <Link className="font-extrabold text-brand hover:underline" to="/register">Register</Link>
        </p>
      </Card>
    </div>
  );
}
