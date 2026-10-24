import { useEffect, useRef, useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Suspense } from 'react';
import {
  Activity,
  HeartPulse,
  LayoutDashboard,
  Megaphone,
  LogOut,
  ShieldCheck,
  ChevronDown,
  UsersRound,
  ClipboardCheck,
} from 'lucide-react';
import { useAuthCtx } from '../../contexts/AuthContext.jsx';
import Avatar from '../ui/Avatar.jsx';
import PublicFooter from './PublicFooter.jsx';
import NotificationCenter from './NotificationCenter.jsx';
import { useLang } from '../../contexts/LanguageContext.jsx';
import { DashboardContentSkeleton } from '../ui/RouteLoadingSkeleton.jsx';

const adminNavigation = [
  { to: '/admin/dashboard', label: 'Overview', Icon: LayoutDashboard },
  { to: '/admin/users', label: 'People & donors', Icon: UsersRound },
  { to: '/admin/donation-reviews', label: 'Leaderboard', Icon: ClipboardCheck },
  { to: '/admin/requests', label: 'Blood requests', Icon: HeartPulse },
  { to: '/admin/public-content', label: 'Public content', Icon: Megaphone },
  { to: '/admin/audit', label: 'Audit activity', Icon: Activity },
];

export default function AdminLayout({ loading = false }) {
  const { user, logout } = useAuthCtx();
  const { t, toggle, lang } = useLang();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileMenuRef = useRef(null);
  const name = user?.name || 'Administrator';

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (!profileMenuRef.current?.contains(event.target)) setProfileOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === 'Escape') setProfileOpen(false);
    }
    document.addEventListener('pointerdown', closeOnOutsideClick);
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsideClick);
      document.removeEventListener('keydown', closeOnEscape);
    };
  }, []);

  function signOut() {
    const pendingLogout = logout();
    navigate('/', { replace: true });
    void pendingLogout;
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f5f7] text-ink">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white">
        <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between gap-2 px-3 sm:h-[72px] sm:gap-4 sm:px-6 lg:px-8">
          <NavLink to="/admin/dashboard" className="flex min-w-0 items-center gap-2 sm:gap-3" aria-label="Administration overview">
            <img src="/images/fotabo-hashi-logo.webp" alt="" className="h-8 w-8 shrink-0 object-contain sm:h-10 sm:w-10" />
            <span className="min-w-0">
              <span className="block truncate font-heading text-sm font-extrabold leading-5 text-slate-900 sm:text-lg">Fotabo Hashi</span>
              <span className="block truncate text-[9px] font-bold uppercase tracking-[.12em] text-brand sm:text-[10px] sm:tracking-[.16em]">{t('administration')}</span>
            </span>
          </NavLink>
          <div className="flex shrink-0 items-center gap-1 sm:gap-4">
            <button type="button" onClick={toggle} aria-label={t('changeLanguage')} className="inline-flex cursor-pointer items-center gap-1 rounded-lg px-1.5 py-2 text-[11px] font-bold text-slate-600 hover:bg-slate-50 sm:px-2 sm:text-xs">{lang === 'en' ? 'BN' : 'EN'}</button>
            <NotificationCenter />
            <span className="hidden items-center gap-1.5 rounded-full bg-rose-50 px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-wide text-brand sm:inline-flex"><ShieldCheck size={14} /> {t('admin')}</span>
            <div className="relative" ref={profileMenuRef}>
              <button type="button" onClick={() => setProfileOpen((open) => !open)} aria-expanded={profileOpen} aria-haspopup="menu" aria-label={`Administrator profile: ${name}`} className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-xl px-2 py-1.5 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">
                <Avatar name={name} size="sm" className="!h-9 !w-9" />
                <span className="hidden max-w-36 truncate text-sm font-bold text-slate-700 md:block">{name}</span>
                <ChevronDown size={15} className={`text-slate-500 transition-transform ${profileOpen ? 'rotate-180' : ''}`} />
              </button>
              {profileOpen && <div role="menu" className="absolute right-0 top-full z-50 mt-2 min-w-48 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl">
                <p className="truncate px-3 py-2 text-xs font-semibold text-slate-500">{name}</p>
                <button type="button" role="menuitem" onClick={signOut} className="flex min-h-10 w-full cursor-pointer items-center gap-2 rounded-lg px-3 text-sm font-bold text-slate-700 transition-colors hover:bg-rose-50 hover:text-brand">
                  <LogOut size={16} /> {t('logout')}
                </button>
              </div>}
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1600px] flex-1 items-start gap-6 px-4 py-5 sm:px-6 sm:py-7 lg:gap-8 lg:px-8">
        <aside className="sticky top-[92px] hidden h-[calc(100vh-112px)] w-64 shrink-0 xl:block">
          <nav className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-3 shadow-sm" aria-label={t('administrationNavigation')}>
            <AdminNavItems />
          </nav>
        </aside>

        <main className="min-w-0 flex-1 pb-24 xl:pb-8">
          {loading ? <DashboardContentSkeleton /> : <Suspense fallback={<DashboardContentSkeleton />}><Outlet /></Suspense>}
        </main>
      </div>

      <nav className="fixed inset-x-3 bottom-3 z-40 flex gap-1 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2 shadow-lg xl:hidden" aria-label={t('administrationNavigation')}>
        {adminNavigation.map(({ to, label, Icon }) => (
        <NavLink key={to} to={to} aria-label={t(({ Overview: 'adminOverview', 'People & donors': 'adminUsers', Leaderboard: 'adminDonationReviews', 'Blood requests': 'adminRequests', 'Public content': 'adminPublicContent', 'Audit activity': 'adminAudit' })[label])} className={({ isActive }) => `flex min-w-0 flex-1 flex-col items-center justify-center gap-1 rounded-xl px-0.5 py-2 text-[9px] font-bold transition-colors ${isActive ? 'bg-rose-50 text-brand' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}`}>
            <Icon size={18} /><span className="max-w-full truncate whitespace-nowrap">{t(({ Overview: 'adminOverview', 'People & donors': 'adminUsers', Leaderboard: 'adminDonationReviews', 'Blood requests': 'adminRequests', 'Public content': 'adminPublicContent', 'Audit activity': 'adminAudit' })[label])}</span>
          </NavLink>
        ))}
      </nav>
      <div className="pb-24 xl:pb-0"><PublicFooter /></div>
    </div>
  );
}

function AdminNavItems() {
  const { t } = useLang();
  return (
    <div className="space-y-1">
      {adminNavigation.map(({ to, label, Icon }) => (
        <NavLink key={to} to={to} className={({ isActive }) => `flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-bold transition-colors ${isActive ? 'bg-brand text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950'}`}>
          <Icon size={18} /><span>{t(({ 'Overview': 'adminOverview', 'People & donors': 'adminUsers', Leaderboard: 'adminDonationReviews', 'Blood requests': 'adminRequests', 'Public content': 'adminPublicContent', 'Audit activity': 'adminAudit' })[label])}</span>
        </NavLink>
      ))}
    </div>
  );
}
