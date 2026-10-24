import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Search, HeartPulse, Trophy, UserRound, Settings } from 'lucide-react';
import { useLang } from '../../contexts/LanguageContext.jsx';

const items = [
  ['/dashboard', 'dashboard', LayoutDashboard],
  ['/donors', 'donors', Search],
  ['/requests', 'requests', HeartPulse],
  ['/leaderboard', 'leaderboard', Trophy],
  ['/profile', 'profile', UserRound],
  ['/settings', 'settings', Settings],
];

export default function Sidebar() {
  const { t } = useLang();
  return (
    <aside className="sticky top-[92px] hidden h-[calc(100vh-112px)] w-64 shrink-0 xl:block">
      <nav className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-3 shadow-sm" aria-label="Member navigation">
        <div className="space-y-1">
          {items.map(([to, key, Icon]) => (
            <NavLink key={to} to={to} end={to === '/dashboard'} className={({ isActive }) => `group flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-bold transition-colors ${isActive ? 'bg-brand text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950'}`}>
              <Icon size={18} strokeWidth={2} /><span>{t(key)}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </aside>
  );
}
