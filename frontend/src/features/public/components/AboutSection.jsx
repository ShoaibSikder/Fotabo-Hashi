import { HeartHandshake, Scale, ShieldCheck } from 'lucide-react';
import { useLang } from '../../../contexts/LanguageContext.jsx';

const principles = [
  { title: 'missionTitle', body: 'missionBody', Icon: HeartHandshake },
  { title: 'visionTitle', body: 'visionBody', Icon: Scale },
  { title: 'valuesTitle', body: 'valuesBody', Icon: ShieldCheck },
];

export default function AboutSection() {
  const { t } = useLang();
  return (
    <section id="about" className="page-shell scroll-mt-24 py-12 sm:py-16">
      <div className="mx-auto max-w-4xl text-center">
        <p className="eyebrow mb-3">{t('aboutEyebrow')}</p>
        <h2 className="section-title">{t('aboutTitle')}</h2>
        <p className="section-copy mx-auto mt-5 max-w-3xl">{t('aboutBody')}</p>
      </div>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {principles.map(({ title, body, Icon }) => (
          <article key={title} className="neu min-h-52 p-6">
            <span className="grid h-12 w-12 place-items-center rounded-2xl bg-brand-soft text-brand">
              <Icon size={23} />
            </span>
            <h3 className="mt-5 text-lg font-extrabold">{t(title)}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{t(body)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
