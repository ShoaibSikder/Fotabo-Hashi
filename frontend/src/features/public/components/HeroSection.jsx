
import { useEffect, useState } from 'react';
import { ArrowDown, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLang } from '../../../contexts/LanguageContext.jsx';
import Button from '../../../components/ui/Button.jsx';
import { HERO_SLIDES } from '../data/heroSlides.js';

export default function HeroSection() {
  const { t } = useLang();
  const [activeIndex, setActiveIndex] = useState(0);
  const [loadVideo] = useState(() => {
    if (typeof window === 'undefined') return false;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const slowConnection = connection?.saveData || ['slow-2g', '2g'].includes(connection?.effectiveType);
    return !reducedMotion && !slowConnection;
  });
  const slide = HERO_SLIDES[activeIndex];

  useEffect(() => {
    if (HERO_SLIDES.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;
    const intervalId = window.setInterval(() => {
      setActiveIndex((index) => (index + 1) % HERO_SLIDES.length);
    }, 10000);
    return () => window.clearInterval(intervalId);
  }, []);

  const showSlide = (index) => {
    setActiveIndex((index + HERO_SLIDES.length) % HERO_SLIDES.length);
  };

  return <section className="relative isolate min-h-[370px] overflow-hidden bg-[#641717] text-white sm:min-h-[410px] lg:min-h-[440px]">
    <div className="hero-fallback" />
    {slide?.type === 'image' ? (
      <img key={slide.src} className="hero-video animate-[heroFadeIn_700ms_ease]" src={slide.src} alt="" aria-hidden="true" />
    ) : slide?.type === 'video' && loadVideo ? (
      <video key={slide.src} className="hero-video animate-[heroFadeIn_700ms_ease]" src={slide.src} autoPlay muted loop playsInline preload="metadata" aria-label={slide.alt} onError={(event) => { event.currentTarget.style.display = 'none'; }} />
    ) : null}
    <div className="hero-overlay" />
    <div className="page-shell relative z-10 flex min-h-[370px] items-end justify-start pb-8 pt-20 text-left sm:min-h-[410px] sm:pb-10 lg:min-h-[440px] lg:pb-12">
      <div className="max-w-3xl">
        <h1 className="max-w-3xl font-heading text-[clamp(2.6rem,6.8vw,5.5rem)] font-extrabold leading-[1.02] tracking-[-.065em] text-white">{t('slogan')}</h1>
        <p className="mt-4 max-w-xl text-base leading-7 text-rose-50/90 sm:text-lg">{t('heroBody')}</p>
        <div className="mt-4 flex flex-row justify-start gap-2.5 sm:mt-5 sm:gap-3">
          <Link to="/donors" className="min-w-0 flex-1"><Button variant="primary" className="w-full !min-h-12 !rounded-full !px-2.5 !text-xs !text-brand-deep !shadow-[0_5px_16px_rgba(0,0,0,0.22)] hover:!shadow-[0_6px_18px_rgba(0,0,0,0.26)] sm:!min-h-14 sm:!px-7 sm:!text-sm"><span className="truncate text-white">{t('findDonor')}</span><ArrowRight className="shrink-0" size={16} /></Button></Link>
          <a href="#about" className="inline-flex min-h-12 min-w-0 flex-1 items-center justify-center gap-1.5 rounded-full border border-white/40 px-2.5 text-xs font-bold text-white transition-colors hover:bg-white/10 sm:min-h-14 sm:gap-2 sm:px-7 sm:text-sm">{t('learnMore')}<ArrowDown className="shrink-0" size={16} /></a>
        </div>
      </div>
    </div>
    {HERO_SLIDES.length > 1 && <div className="absolute bottom-4 right-5 z-20 flex items-center gap-2 sm:bottom-6 sm:right-8">
      <button type="button" onClick={() => showSlide(activeIndex - 1)} aria-label={t('previousHeroSlide')} className="grid h-9 w-9 place-items-center rounded-full border border-white/40 bg-black/20 text-white backdrop-blur transition-colors hover:bg-black/40"><ChevronLeft size={18} /></button>
      <div className="flex items-center gap-1.5" role="group" aria-label={t('chooseHeroSlide')}>
        {HERO_SLIDES.map((item, index) => <button key={item.src} type="button" onClick={() => showSlide(index)} aria-label={t('heroSlideNumber', { number: index + 1 })} aria-current={index === activeIndex ? 'true' : undefined} className={`h-2 rounded-full transition-all ${index === activeIndex ? 'w-6 bg-white' : 'w-2 bg-white/60 hover:bg-white'}`} />)}
      </div>
      <button type="button" onClick={() => showSlide(activeIndex + 1)} aria-label={t('nextHeroSlide')} className="grid h-9 w-9 place-items-center rounded-full border border-white/40 bg-black/20 text-white backdrop-blur transition-colors hover:bg-black/40"><ChevronRight size={18} /></button>
    </div>}
  </section>;
}
