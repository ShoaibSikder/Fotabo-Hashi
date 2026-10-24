import { useCallback, useEffect, useRef, useState } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost } from '../../services/apiClient.js';
import { API_ENDPOINTS } from '../../services/endpointConfig.js';
import { useLang } from '../../contexts/LanguageContext.jsx';

const EVENT_KEYS = {
  NEW_ACCOUNT: 'notificationNewAccount',
  NEW_BLOOD_REQUEST: 'notificationNewRequest',
  REQUEST_UPDATED: 'notificationRequestUpdated',
  ACCOUNT_UPDATED: 'notificationAccountUpdated',
  ANNOUNCEMENT: 'notificationAnnouncement',
  DONATION_RECORDED: 'notificationDonationRecorded',
  DONATION_COUNT_REVIEW: 'notificationDonationCountReview',
  DONATION_COUNT_REVIEWED: 'notificationDonationCountReviewed',
};

export default function NotificationCenter() {
  const { t, lang } = useLang();
  const navigate = useNavigate();
  const rootRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [showIndicator, setShowIndicator] = useState(() => localStorage.getItem('fh-notices') !== 'false');
  const unread = items.filter((item) => !item.is_read).length;

  const refresh = useCallback(async () => {
    try {
      const result = await apiGet(API_ENDPOINTS.notifications);
      setItems(Array.isArray(result) ? result : result?.results || []);
      setError('');
    } catch (err) {
      if (err.status !== 401) setError(err.message);
    }
  }, []);

  useEffect(() => {
    const refreshWhenVisible = () => {
      if (document.visibilityState === 'visible') refresh();
    };
    refreshWhenVisible();
    const timer = window.setInterval(refreshWhenVisible, 60000);
    document.addEventListener('visibilitychange', refreshWhenVisible);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', refreshWhenVisible);
    };
  }, [refresh]);

  useEffect(() => {
    const updatePreference = () => setShowIndicator(localStorage.getItem('fh-notices') !== 'false');
    window.addEventListener('fh-notices-changed', updatePreference);
    return () => window.removeEventListener('fh-notices-changed', updatePreference);
  }, []);

  useEffect(() => {
    if (!open) return undefined;
    function onPointerDown(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function onKeyDown(event) {
      if (event.key === 'Escape') setOpen(false);
    }
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  async function markAllRead() {
    setBusy(true);
    try {
      await apiPost(API_ENDPOINTS.notificationReadAll, {});
      setItems((current) => current.map((item) => ({ ...item, is_read: true })));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function openNotification(item) {
    if (!item.is_read) {
      try {
        await apiPost(API_ENDPOINTS.notificationRead(item.id), {});
        setItems((current) => current.map((row) => row.id === item.id ? { ...row, is_read: true } : row));
      } catch (err) {
        setError(err.message);
      }
    }
    setOpen(false);
    if (item.action_url?.startsWith('/')) navigate(item.action_url);
  }

  return <div className="relative" ref={rootRef}>
    <button type="button" onClick={() => { setOpen((value) => !value); if (!open) refresh(); }} className="relative grid h-10 w-10 cursor-pointer place-items-center rounded-xl text-slate-600 transition-colors hover:bg-slate-50 hover:text-brand" aria-label={unread ? t('unreadNotifications', { count: unread }) : t('notifications')} aria-expanded={open} aria-haspopup="dialog">
      <Bell size={19} />{showIndicator && unread > 0 && <span className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-brand px-1 text-[10px] font-extrabold text-white">{unread > 99 ? '99+' : unread}</span>}
    </button>
    {open && <section role="dialog" aria-label={t('notifications')} className="absolute right-0 top-full z-50 mt-2 w-[min(23rem,calc(100vw-1.5rem))] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
      <header className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3"><div><h2 className="text-sm font-extrabold text-slate-900">{t('notifications')}</h2><p className="text-xs text-slate-500">{t('unreadCount', { count: unread })}</p></div><button disabled={!unread || busy} type="button" onClick={markAllRead} className="inline-flex cursor-pointer items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-bold text-brand hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-40"><CheckCheck size={14} />{t('markAllRead')}</button></header>
      {error && <p role="alert" className="px-4 py-2 text-xs text-red-700">{error}</p>}
      <div className="max-h-[min(65vh,28rem)] overflow-y-auto">
        {items.length ? items.map((item) => <button key={item.id} type="button" onClick={() => openNotification(item)} className={`block w-full cursor-pointer border-b border-slate-50 px-4 py-3 text-left transition-colors hover:bg-slate-50 ${item.is_read ? 'bg-white' : 'bg-rose-50/60'}`}>
          <span className="flex items-start gap-2"><span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${item.is_read ? 'bg-transparent' : 'bg-brand'}`} /><span className="min-w-0 flex-1"><span className="block text-sm font-bold text-slate-800">{t(EVENT_KEYS[item.event_type] || 'notificationAnnouncement')}</span><span className="mt-0.5 block text-xs leading-5 text-slate-600">{item.payload?.message || notificationDetail(item, t)}</span><time className="mt-1 block text-[10px] text-slate-400" dateTime={item.created_at}>{new Intl.DateTimeFormat(lang === 'bn' ? 'bn-BD' : 'en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(item.created_at))}</time></span></span>
        </button>) : <p className="px-4 py-8 text-center text-sm text-slate-500">{t('noNotifications')}</p>}
      </div>
    </section>}
  </div>;
}

function notificationDetail(item, t) {
  const { blood_group: group, status } = item.payload || {};
  if (item.payload?.notice_title) {
    return t('notificationNoticePublished', { title: item.payload.notice_title });
  }
  if (group && status) return t('notificationGroupStatus', { group, status: t(`requestStatus_${status}`) || status });
  if (group) return t('notificationBloodGroup', { group });
  if (item.payload?.email) return item.payload.email;
  return t('notificationOpenForDetails');
}
