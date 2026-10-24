import { Languages } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLang } from '../../contexts/LanguageContext.jsx';
import ProfileMenu from './ProfileMenu.jsx';
import NotificationCenter from './NotificationCenter.jsx';

const bangla = '\u09ac\u09be\u0982\u09b2\u09be';

export default function AppHeader() {
  const { toggle, lang, t } = useLang();
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white">
        <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between gap-2 px-3 sm:h-[72px] sm:gap-4 sm:px-6 lg:px-8">
        <Link to="/dashboard" className="flex min-w-0 items-center gap-2 sm:gap-3" aria-label="Fotabo Hashi member dashboard">
          <img src="/images/Fotabo_Hashi_Logo.svg" alt="" className="h-8 w-8 shrink-0 object-contain sm:h-10 sm:w-10" />
          <span className="min-w-0">
            <span className="block truncate font-heading text-sm font-extrabold leading-5 text-slate-900 sm:text-lg">Fotabo Hashi</span>
          </span>
        </Link>
        <div className="flex shrink-0 items-center gap-1 sm:gap-4">
          <button type="button" onClick={toggle} className="inline-flex min-h-10 cursor-pointer items-center gap-1 rounded-lg px-1.5 py-2 text-[11px] font-bold text-slate-600 transition-colors hover:bg-slate-50 sm:gap-2 sm:px-3 sm:text-sm" aria-label={t('changeLanguage')}>
            <Languages size={17} />{lang === 'en' ? <><span className="sm:hidden">BN</span><span className="hidden sm:inline">{bangla}</span></> : 'EN'}
          </button>
          <NotificationCenter />
          <span className="h-8 w-px bg-slate-200" aria-hidden="true" />
          <ProfileMenu />
        </div>
      </div>
    </header>
  );
}
