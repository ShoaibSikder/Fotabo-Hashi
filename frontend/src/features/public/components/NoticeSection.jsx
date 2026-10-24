import { BellRing } from 'lucide-react';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import EmptyState from '../../../components/ui/EmptyState.jsx';
import { formatDate } from '../../../utils/formatDate.js';

export default function NoticeSection({ notices = [] }) {
  const { t } = useLang();
  return (
    <section id="notices" className="scroll-mt-24 bg-slate-100/70 py-12 sm:py-16">
      <div className="page-shell">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-3">{t('noticesIntro')}</p>
          <h2 className="section-title">{t('notices')}</h2>
        </div>
        {notices.length ? (
          <div
            className="mt-7 grid auto-cols-[minmax(260px,78vw)] grid-flow-col grid-rows-2 gap-4 overflow-x-auto overscroll-x-contain pb-3 snap-x snap-mandatory focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-brand lg:auto-cols-[340px] lg:grid-rows-1"
            tabIndex={0}
            aria-label={t('noticesSlider')}
          >
            {notices.map((notice) => (
              <article key={notice.id} className="neu flex min-h-40 snap-start gap-4 p-5 sm:p-6">
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-soft text-brand"><BellRing size={20} /></span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-brand">{formatDate(notice.published_at)}</p>
                  <h3 className="mt-2 font-heading text-lg font-extrabold text-brand-dark">{notice.title}</h3>
                  <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted">{notice.content}</p>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="mt-7"><EmptyState title={t('noticesEmptyTitle')} description={t('noticesEmptyBody')} /></div>
        )}
      </div>
    </section>
  );
}
