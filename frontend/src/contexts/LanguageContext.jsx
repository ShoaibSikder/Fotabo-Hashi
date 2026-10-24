
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import enCommon from '../i18n/locales/en/common.json';
import enPublic from '../i18n/locales/en/public.json';
import enDashboard from '../i18n/locales/en/dashboard.json';
import enDonors from '../i18n/locales/en/donors.json';
import enRequests from '../i18n/locales/en/requests.json';
import enSettings from '../i18n/locales/en/settings.json';
import bnCommon from '../i18n/locales/bn/common.json';
import bnPublic from '../i18n/locales/bn/public.json';
import bnDashboard from '../i18n/locales/bn/dashboard.json';
import bnDonors from '../i18n/locales/bn/donors.json';
import bnRequests from '../i18n/locales/bn/requests.json';
import bnSettings from '../i18n/locales/bn/settings.json';

const dictionaries = {
  en: { ...enCommon, ...enPublic, ...enDashboard, ...enDonors, ...enRequests, ...enSettings },
  bn: { ...bnCommon, ...bnPublic, ...bnDashboard, ...bnDonors, ...bnRequests, ...bnSettings },
};
const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('fh-language') === 'bn' ? 'bn' : 'en');
  useEffect(() => { document.documentElement.lang = lang === 'bn' ? 'bn' : 'en'; }, [lang]);
  const changeLanguage = (next) => {
    setLang(next);
    localStorage.setItem('fh-language', next);
    document.documentElement.lang = next;
  };
  const value = useMemo(() => ({
    lang,
    setLang: changeLanguage,
    toggle: () => changeLanguage(lang === 'en' ? 'bn' : 'en'),
    t: (key, values = {}) => {
      const template = dictionaries[lang]?.[key] || dictionaries.en[key] || key;
      return Object.entries(values).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, String(value)), template);
    },
  }), [lang]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLang() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLang must be used inside LanguageProvider');
  return context;
}
