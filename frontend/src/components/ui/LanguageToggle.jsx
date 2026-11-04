import { useLang } from '../../contexts/LanguageContext.jsx';

export default function LanguageToggle({ compact = false, className = '' }) {
  const { lang, setLang, t } = useLang();
  const isBangla = lang === 'bn';

  return (
    <button
      type="button"
      role="switch"
      aria-label={t('changeLanguage')}
      aria-checked={isBangla}
      title={t(isBangla ? 'switchToEnglish' : 'switchToBangla')}
      onClick={() => setLang(isBangla ? 'en' : 'bn')}
      className={`relative inline-flex shrink-0 cursor-pointer items-center rounded-full border border-white bg-[#ebebee] shadow-[inset_0_2px_7px_rgba(15,23,42,0.16),0_1px_2px_rgba(15,23,42,0.08)] transition-colors hover:bg-[#e5e5e9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand ${compact ? 'h-9 w-[76px]' : 'h-12 w-[104px]'} ${className}`}
    >
      <span className={`absolute font-extrabold leading-none tracking-wide text-slate-600 transition-all duration-300 ${compact ? 'text-xs' : 'text-base'} ${isBangla ? 'right-2' : 'left-3'}`}>
        {isBangla ? 'BN' : 'EN'}
      </span>
      <span aria-hidden="true" className={`absolute left-1 grid shrink-0 place-items-center rounded-full bg-white shadow-[0_2px_6px_rgba(15,23,42,0.24)] ring-1 ring-slate-900/5 transition-transform duration-300 ease-in-out ${compact ? 'h-7 w-7' : 'h-10 w-10'} ${isBangla ? 'translate-x-0' : (compact ? 'translate-x-[38px]' : 'translate-x-[56px]')}`}>
        <LanguageFlag bangla={isBangla} />
      </span>
      <span className="sr-only">{t(isBangla ? 'switchToEnglish' : 'switchToBangla')}</span>
    </button>
  );
}

function LanguageFlag({ bangla }) {
  return bangla ? (
    <svg viewBox="0 0 32 32" className="h-[72%] w-[72%] overflow-hidden rounded-full" focusable="false">
      <circle cx="16" cy="16" r="16" fill="#006a4e" />
      <circle cx="17" cy="16" r="7" fill="#f42a41" />
    </svg>
  ) : (
    <svg viewBox="0 0 32 32" className="h-[72%] w-[72%] overflow-hidden rounded-full" focusable="false">
      <circle cx="16" cy="16" r="16" fill="#1c2b63" />
      <path d="M2 2 30 30M30 2 2 30" stroke="#fff" strokeWidth="7" />
      <path d="M2 2 30 30M30 2 2 30" stroke="#c8102e" strokeWidth="3" />
      <path d="M16 0v32M0 16h32" stroke="#fff" strokeWidth="10" />
      <path d="M16 0v32M0 16h32" stroke="#c8102e" strokeWidth="5" />
    </svg>
  );
}
