import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Search, HeartPulse, Trophy } from 'lucide-react';
import { useLang } from '../../contexts/LanguageContext.jsx';

const items = [
  ['/dashboard', 'dashboard', LayoutDashboard],
  ['/donors', 'donors', Search],
  ['/requests', 'requests', HeartPulse],
  ['/leaderboard', 'leaderboard', Trophy],
];

export default function MobileNavigation() {
  const { t } = useLang();
  return <nav className="member-mobile-nav fixed inset-x-2 bottom-2 z-40 flex gap-1 overflow-x-auto overscroll-x-contain rounded-2xl border border-slate-200 bg-white p-2 shadow-lg sm:inset-x-4 sm:bottom-4 xl:hidden" aria-label="Member navigation">{items.map(([to, key, Icon]) => <NavLink key={to} to={to} end={to === '/dashboard'} className={({ isActive }) => `flex min-h-14 min-w-[76px] shrink-0 flex-col items-center justify-center gap-1 rounded-xl px-2 py-2 text-[10px] font-bold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand ${isActive ? 'bg-rose-50 text-brand' : 'text-slate-500 hover:bg-slate-50'}`}><Icon size={20} /><span className="whitespace-nowrap">{t(key)}</span></NavLink>)}</nav>;
}
