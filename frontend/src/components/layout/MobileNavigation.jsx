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
  return <nav className="fixed inset-x-3 bottom-3 z-40 flex justify-around rounded-2xl border border-slate-200 bg-white p-2 shadow-lg xl:hidden" aria-label="Member navigation">{items.map(([to, key, Icon]) => <NavLink key={to} to={to} end={to === '/dashboard'} className={({ isActive }) => `flex min-w-[52px] flex-col items-center gap-1 rounded-xl px-2 py-2 text-[10px] font-bold transition-colors ${isActive ? 'bg-rose-50 text-brand' : 'text-slate-500 hover:bg-slate-50'}`}><Icon size={20} /><span>{t(key)}</span></NavLink>)}</nav>;
}
