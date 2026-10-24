
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AboutSection from '../components/AboutSection.jsx';
import CampaignsSection from '../components/CampaignsSection.jsx';
import ActiveMembers from '../components/ActiveMembers.jsx';
import HeroSection from '../components/HeroSection.jsx';
import NoticeSection from '../components/NoticeSection.jsx';
import { getPublicContent } from '../services/publicContentService.js';
import { useLang } from '../../../contexts/LanguageContext.jsx';

export default function HomePage() {
  const { t } = useLang();
  const [content, setContent] = useState({ notices: [], members: [], hasError: false });
  const { pathname, search, hash } = useLocation();
  const navigate = useNavigate();
  const isInitialReload = useRef(
    performance.getEntriesByType?.('navigation')?.[0]?.type === 'reload',
  );
  const reloadHashToIgnore = useRef('');
  useEffect(() => {
    let active = true;
    getPublicContent().then((value) => { if (active) setContent(value); });
    return () => { active = false; };
  }, []);
  useLayoutEffect(() => {
    // Browsers restore the previous scroll position (and URL hash) on reload.
    // Start a fresh homepage view at the hero instead; in-app section links
    // continue to scroll normally because their navigation type is not reload.
    if (isInitialReload.current) {
      isInitialReload.current = false;
      reloadHashToIgnore.current = hash;

      if ('scrollRestoration' in window.history) {
        window.history.scrollRestoration = 'manual';
      }

      if (hash) {
        navigate(`${pathname}${search}`, { replace: true });
      }

      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      requestAnimationFrame(() => {
        window.history.scrollRestoration = 'auto';
      });
      return;
    }

    // StrictMode runs layout effects twice on mount. Ignore the original
    // reload hash until the replace navigation has updated Router's location.
    if (reloadHashToIgnore.current) {
      if (hash === reloadHashToIgnore.current) return;
      reloadHashToIgnore.current = '';
    }

    if (pathname !== '/' || !hash) return;
    const sectionId = decodeURIComponent(hash.slice(1));
    requestAnimationFrame(() => document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, [pathname, search, hash, navigate]);
  return <div className="overflow-hidden"><HeroSection />{content.hasError && <div className="page-shell pt-4"><p role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{t('connection')} {t('retry')}</p></div>}<AboutSection /><CampaignsSection /><ActiveMembers members={content.members} /><NoticeSection notices={content.notices} /></div>;
}
