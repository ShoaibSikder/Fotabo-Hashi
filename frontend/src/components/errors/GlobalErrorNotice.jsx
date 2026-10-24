import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { useLang } from '../../contexts/LanguageContext.jsx';

export default function GlobalErrorNotice() {
  const { t, lang } = useLang();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const showNotice = () => setVisible(true);
    window.addEventListener('error', showNotice);
    window.addEventListener('unhandledrejection', showNotice);
    return () => {
      window.removeEventListener('error', showNotice);
      window.removeEventListener('unhandledrejection', showNotice);
    };
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed inset-x-4 top-4 z-[100] mx-auto flex max-w-xl items-start gap-3 rounded-xl border border-red-200 bg-white p-4 text-sm text-red-900 shadow-xl" role="alert">
      <p className="flex-1 font-semibold">{lang === 'bn' ? 'অপ্রত্যাশিত ত্রুটি হয়েছে। অনুগ্রহ করে পৃষ্ঠাটি রিফ্রেশ করে আবার চেষ্টা করুন।' : t('unexpectedAppError')}</p>
      <button type="button" onClick={() => setVisible(false)} className="grid h-7 w-7 shrink-0 cursor-pointer place-items-center rounded-md text-red-700 hover:bg-red-50" aria-label={lang === 'bn' ? 'বন্ধ করুন' : t('dismiss')}>
        <X size={16} />
      </button>
    </div>
  );
}
