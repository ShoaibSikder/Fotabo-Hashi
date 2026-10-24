import { useState } from 'react';
import { Bell, Globe, ShieldCheck } from 'lucide-react';
import Card from '../../../components/ui/Card.jsx';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import PasswordSettings from '../components/PasswordSettings.jsx';

export default function SettingsPage() {
  const { lang, toggle, t } = useLang();
  const [notifications, setNotifications] = useState(() => localStorage.getItem('fh-notices') !== 'false');

  function updateNotifications(enabled) {
    setNotifications(enabled);
    localStorage.setItem('fh-notices', String(enabled));
    window.dispatchEvent(new Event('fh-notices-changed'));
  }

  return <div className="page-enter space-y-6">
    <div><h1 className="text-3xl font-extrabold text-brand-dark">{t('settings')}</h1></div>
    <Card><div className="flex gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand"><Globe /></span><div className="flex-1"><h2 className="font-extrabold text-brand-dark">{t('language')}</h2><button type="button" onClick={toggle} className="neu-btn mt-4">{lang === 'en' ? t('switchToBangla') : t('switchToEnglish')}</button></div></div></Card>
    <Card><div className="flex gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand"><Bell /></span><div className="flex-1"><h2 className="font-extrabold text-brand-dark">{t('notificationIndicator')}</h2><label className="mt-4 flex items-center gap-3"><input type="checkbox" className="h-4 w-4 accent-red-700" checked={notifications} onChange={(event) => updateNotifications(event.target.checked)} /><span className="text-sm font-semibold text-ink">{t('showNotificationIndicator')}</span></label></div></div></Card>
    <PasswordSettings />
    <Card className="!bg-white/40"><div className="flex gap-3"><ShieldCheck className="shrink-0 text-brand" /><p className="text-sm leading-6 text-muted">{t('privacyReminder')}</p></div></Card>
  </div>;
}
