import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useLang } from '../../contexts/LanguageContext.jsx';

const SITE_URL = 'https://fotabohashi.vercel.app';
const SITE_NAME = 'Fotabo Hashi';
const BRAND_IMAGE = `${SITE_URL}/images/fotabo-hashi-logo.webp`;

const pages = [
  { match: /^\/$/, en: 'Find Blood Donors in Bangladesh', bn: 'বাংলাদেশে রক্তদাতা খুঁজুন' },
  { match: /^\/login\/?$/, en: 'Log in', bn: 'লগ ইন' },
  { match: /^\/register\/?$/, en: 'Create account', bn: 'অ্যাকাউন্ট তৈরি' },
  { match: /^\/forgot-password\/?$/, en: 'Reset password', bn: 'পাসওয়ার্ড রিসেট' },
  { match: /^\/reset-password\/?$/, en: 'Choose a new password', bn: 'নতুন পাসওয়ার্ড দিন' },
  { match: /^\/dashboard\/?$/, en: 'Dashboard', bn: 'ড্যাশবোর্ড' },
  { match: /^\/donors\/?$/, en: 'Find donors', bn: 'রক্তদাতা খুঁজুন' },
  { match: /^\/requests(?:\/.*)?$/, en: 'Blood requests', bn: 'রক্তের অনুরোধ' },
  { match: /^\/leaderboard\/?$/, en: 'Leaderboard', bn: 'লিডারবোর্ড' },
  { match: /^\/profile\/?$/, en: 'Profile', bn: 'প্রোফাইল' },
  { match: /^\/settings\/?$/, en: 'Settings', bn: 'সেটিংস' },
  { match: /^\/admin(?:\/.*)?$/, en: 'Administration', bn: 'অ্যাডমিন প্যানেল' },
];

function setMeta(attribute, key, value) {
  let element = document.head.querySelector(`meta[${attribute}="${key}"]`);
  if (!element) {
    element = document.createElement('meta');
    element.setAttribute(attribute, key);
    document.head.appendChild(element);
  }
  element.setAttribute('content', value);
}

function setCanonical(url) {
  let element = document.head.querySelector('link[rel="canonical"]');
  if (!url) {
    element?.remove();
    return;
  }
  if (!element) {
    element = document.createElement('link');
    element.rel = 'canonical';
    document.head.appendChild(element);
  }
  element.href = url;
}

export default function SeoManager() {
  const { pathname } = useLocation();
  const { lang } = useLang();

  useEffect(() => {
    const isHome = pathname === '/';
    const page = pages.find((item) => item.match.test(pathname));
    const pageTitle = page?.[lang] || (lang === 'bn' ? 'Fotabo Hashi' : 'Fotabo Hashi');
    const title = isHome
      ? lang === 'bn'
        ? 'Fotabo Hashi | বাংলাদেশে রক্তদাতা খুঁজুন'
        : `${SITE_NAME} | Find Blood Donors in Bangladesh`
      : `${pageTitle} | ${SITE_NAME}`;
    const description = lang === 'bn'
      ? 'Fotabo Hashi-এর মাধ্যমে বাংলাদেশে রক্তদাতা খুঁজুন, জরুরি রক্তের অনুরোধ জানান এবং স্বেচ্ছায় রক্তদানে সহায়তা করুন।'
      : 'Find blood donors in Bangladesh with Fotabo Hashi. Share urgent blood requests and support voluntary donation in Ashuganj, Brahmanbaria.';

    document.title = title;
    document.documentElement.lang = lang === 'bn' ? 'bn' : 'en';
    setMeta('name', 'description', description);
    setMeta('name', 'robots', isHome ? 'index, follow, max-image-preview:large' : 'noindex, nofollow');
    setMeta('property', 'og:site_name', SITE_NAME);
    setMeta('property', 'og:type', 'website');
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:locale', lang === 'bn' ? 'bn_BD' : 'en_BD');
    setMeta('name', 'twitter:card', 'summary');
    setMeta('name', 'twitter:title', title);
    setMeta('name', 'twitter:description', description);

    if (isHome) {
      setCanonical(`${SITE_URL}/`);
      setMeta('property', 'og:url', `${SITE_URL}/`);
      setMeta('property', 'og:image', BRAND_IMAGE);
      setMeta('property', 'og:image:alt', 'Fotabo Hashi blood donor community logo');
      setMeta('name', 'twitter:image', BRAND_IMAGE);
    } else {
      setCanonical('');
      document.head.querySelector('meta[property="og:url"]')?.remove();
      document.head.querySelector('meta[property="og:image"]')?.remove();
      document.head.querySelector('meta[property="og:image:alt"]')?.remove();
      document.head.querySelector('meta[name="twitter:image"]')?.remove();
    }
  }, [lang, pathname]);

  return null;
}
