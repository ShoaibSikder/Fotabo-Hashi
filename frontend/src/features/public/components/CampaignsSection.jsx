import { HeartHandshake } from 'lucide-react';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function CampaignsSection() {
  const { t } = useLang();
  return (
    <section id="campaigns" className="bg-slate-100/70 py-12 sm:py-16">
      <div className="page-shell">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-3">Fotabo Hashi</p>
          <h2 className="section-title">{t('campaigns')}</h2>
          <div className="neu mt-7 px-6 py-8">
            <HeartHandshake className="mx-auto text-brand" size={32} />
            <p className="mt-4 text-sm leading-6 text-muted">{t('campaignsEmpty')}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
