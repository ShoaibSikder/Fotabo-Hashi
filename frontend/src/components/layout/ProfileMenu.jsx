
import { useEffect, useRef, useState } from 'react';
import { ChevronDown, LogOut, Settings, UserRound } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthCtx } from '../../contexts/AuthContext.jsx';
import Avatar from '../ui/Avatar.jsx';
import { useLang } from '../../contexts/LanguageContext.jsx';

export default function ProfileMenu() {
  const { user, logout } = useAuthCtx();
  const { t } = useLang();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const displayName = user?.name?.trim() || 'Community member';

  useEffect(() => {
    if (!open) return undefined;

    function closeOnOutsideClick(event) {
      if (!menuRef.current?.contains(event.target)) setOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === 'Escape') setOpen(false);
    }

    document.addEventListener('pointerdown', closeOnOutsideClick);
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsideClick);
      document.removeEventListener('keydown', closeOnEscape);
    };
  }, [open]);

  return <div ref={menuRef} className="relative"><button type="button" className="flex cursor-pointer items-center gap-2 rounded-full p-1.5 transition-colors hover:bg-white/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand" onClick={() => setOpen((value) => !value)} aria-expanded={open} aria-haspopup="menu" aria-label={`Open profile menu for ${displayName}`}><Avatar name={displayName} size="sm" /><span className="hidden max-w-32 truncate text-left text-xs font-bold text-ink sm:block">{displayName}</span><ChevronDown size={15} className="text-muted" /></button>{open && <div role="menu" className="neu absolute right-0 top-full z-50 mt-2 w-56 p-2"><Link role="menuitem" onClick={() => setOpen(false)} to="/profile" className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold hover:bg-white/70"><UserRound size={17} />{t('profile')}</Link><Link role="menuitem" onClick={() => setOpen(false)} to="/settings" className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold hover:bg-white/70"><Settings size={17} />{t('settings')}</Link><div className="my-1 soft-divider" /><button role="menuitem" type="button" onClick={() => { setOpen(false); const pendingLogout = logout(); navigate('/', { replace: true }); void pendingLogout; }} className="flex w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-bold text-brand hover:bg-brand-soft"><LogOut size={17} />{t('logout')}</button></div>}</div>;
}
