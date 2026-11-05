import { Link } from 'react-router-dom';
import ProfileMenu from './ProfileMenu.jsx';
import NotificationCenter from './NotificationCenter.jsx';
import LanguageToggle from '../ui/LanguageToggle.jsx';

export default function AppHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white">
        <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between gap-2 px-3 sm:h-[72px] sm:gap-4 sm:px-6 lg:px-8">
        <Link to="/dashboard" className="flex min-w-0 items-center gap-2 sm:gap-3" aria-label="Fotabo Hashi member dashboard">
          <img src="/images/fotabo-hashi-logo.webp" alt="" className="h-8 w-8 shrink-0 object-contain sm:h-10 sm:w-10" />
          <span className="min-w-0">
            <span className="block truncate font-heading text-sm font-extrabold leading-5 text-slate-900 sm:text-lg">Fotabo Hashi</span>
          </span>
        </Link>
        <div className="flex shrink-0 items-center gap-1 sm:gap-4">
          <LanguageToggle compact />
          <NotificationCenter />
          <span className="h-8 w-px bg-slate-200" aria-hidden="true" />
          <ProfileMenu />
        </div>
      </div>
    </header>
  );
}
