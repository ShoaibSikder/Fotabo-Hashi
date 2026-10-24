import { useState } from 'react';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLang } from '../../contexts/LanguageContext.jsx';

const links = [['#about', 'aboutEyebrow'], ['#campaigns', 'campaigns'], ['#active-members', 'activeMembers'], ['#notices', 'notices']];
const bangla = '\u09ac\u09be\u0982\u09b2\u09be';

export default function PublicHeader() {
  const { t, toggle, lang } = useLang();
  const [menuOpen, setMenuOpen] = useState(false);
  return <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white">
    <div className="page-shell flex h-[72px] items-center justify-between gap-5">
      <Link to="/" className="group flex shrink-0 items-center gap-2.5" aria-label="Fotabo Hashi home"><img src="/images/fotabo-hashi-logo.webp" alt="" className="h-10 w-10 object-contain transition-transform group-hover:-rotate-3" /><span className="font-heading text-lg font-extrabold tracking-tight text-brand-dark sm:text-xl">Fotabo Hashi</span></Link>
      <nav className="hidden items-center gap-8 lg:flex" aria-label="Main navigation">{links.map(([href,key])=><Link key={href} className="text-sm font-bold text-slate-600 transition-colors hover:text-brand" to={`/${href}`}>{t(key)}</Link>)}</nav>
      <div className="hidden items-center gap-3 sm:flex"><button type="button" onClick={toggle} className="rounded-xl px-3 py-2 text-sm font-bold text-brand-dark transition-colors hover:bg-white/60" aria-label="Change language">{lang==='en'?bangla:'EN'}</button><Link to="/login" className="neu-btn neu-red !min-h-11 !rounded-full !px-5">{t('login')} <ArrowUpRight size={16}/></Link></div>
      <button type="button" className="grid h-11 w-11 place-items-center rounded-xl text-brand lg:hidden" onClick={()=>setMenuOpen(open=>!open)} aria-label={menuOpen?'Close menu':'Open menu'} aria-expanded={menuOpen}>{menuOpen?<X/>:<Menu/>}</button>
    </div>
    {menuOpen&&<div className="absolute inset-x-0 top-full border-t border-white/70 bg-surface p-4 shadow-soft lg:hidden"><nav className="page-shell flex flex-col gap-2">{links.map(([href,key])=><Link key={href} onClick={()=>setMenuOpen(false)} className="rounded-xl px-4 py-3 font-bold text-muted hover:bg-white/60" to={`/${href}`}>{t(key)}</Link>)}<div className="flex items-center gap-3 px-3 pt-2"><button type="button" className="neu-btn" onClick={toggle}>{lang==='en'?bangla:'EN'}</button><Link to="/login" className="neu-btn neu-red flex-1" onClick={()=>setMenuOpen(false)}>{t('login')}</Link></div></nav></div>}
  </header>;
}
