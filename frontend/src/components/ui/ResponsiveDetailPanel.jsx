import { useEffect } from 'react';

/** Desktop detail column that becomes a plain-backdrop sheet on smaller screens. */
export default function ResponsiveDetailPanel({ open, onClose, label, children }) {
  useEffect(() => {
    if (!open) return undefined;
    function closeOnEscape(event) {
      if (event.key === 'Escape') onClose?.();
    }
    document.addEventListener('keydown', closeOnEscape);
    return () => {
      document.removeEventListener('keydown', closeOnEscape);
    };
  }, [open, onClose]);

  return (
    <div
      className={`${open ? 'fixed inset-0 z-[60] flex items-end bg-slate-950/35 p-0 sm:items-center sm:p-4 2xl:static 2xl:block 2xl:bg-transparent 2xl:p-0' : 'hidden 2xl:block'}`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
    >
      <section
        role={open ? 'dialog' : 'region'}
        aria-modal={open && (typeof window === 'undefined' || window.matchMedia('(max-width: 1535px)').matches) ? 'true' : undefined}
        aria-label={label}
        className="max-h-[92dvh] w-full overflow-y-auto rounded-t-3xl bg-white p-4 shadow-2xl sm:mx-auto sm:max-w-xl sm:rounded-2xl sm:p-5 2xl:max-h-none 2xl:max-w-none 2xl:overflow-visible 2xl:rounded-2xl 2xl:shadow-sm"
      >
        {children}
      </section>
    </div>
  );
}
