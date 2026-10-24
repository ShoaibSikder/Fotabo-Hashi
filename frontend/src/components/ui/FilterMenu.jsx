import { useEffect, useRef, useState } from 'react';
import { SlidersHorizontal } from 'lucide-react';
import Button from './Button.jsx';
import { useLang } from '../../contexts/LanguageContext.jsx';

export default function FilterMenu({ activeCount = 0, onClear, children }) {
  const { t } = useLang();
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    function closeOnOutsideClick(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
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

  return (
    <div className="relative shrink-0" ref={rootRef}>
      <Button
        type="button"
        variant="secondary"
        aria-expanded={open}
        aria-haspopup="true"
        aria-label={t('filter')}
        onClick={() => setOpen((current) => !current)}
        className="!min-h-11 !w-11 !shrink-0 !justify-center !rounded-xl !border !border-slate-200 !bg-white !px-2 !shadow-none hover:!bg-slate-50 sm:!w-auto sm:!px-4"
      >
        <SlidersHorizontal size={16} aria-hidden="true" />
        <span className="sr-only sm:not-sr-only">{t('filter')}</span>
        {activeCount > 0 && (
          <span className="grid h-5 min-w-5 place-items-center rounded-full bg-brand px-1 text-[11px] font-extrabold text-white">
            {activeCount}
          </span>
        )}
      </Button>

      {open && (
        <div
          role="region"
          aria-label={t('filterOptions')}
          className="absolute right-0 z-30 mt-2 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-slate-200 bg-white p-4 shadow-xl"
        >
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-sm font-extrabold text-slate-900">{t('filterOptions')}</h2>
            {activeCount > 0 && (
              <button
                type="button"
                onClick={() => {
                  onClear?.();
                  setOpen(false);
                }}
                className="cursor-pointer rounded-md px-2 py-1 text-xs font-bold text-brand transition-colors hover:bg-rose-50"
              >
                {t('clearFilters')}
              </button>
            )}
          </div>
          <div className="grid gap-3">{children}</div>
        </div>
      )}
    </div>
  );
}
