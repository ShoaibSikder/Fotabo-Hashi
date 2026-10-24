
export function formatDate(value, locale = 'en-BD') {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
}

export function timeAgo(value, locale = 'en') {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const elapsed = Math.max(0, Date.now() - date.getTime());
  const hours = Math.floor(elapsed / 3600000);
  if (hours < 1) return locale === 'bn' ? 'এইমাত্র' : 'Just now';
  if (hours < 24) return locale === 'bn' ? `${hours} ঘণ্টা আগে` : `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return locale === 'bn' ? `${days} দিন আগে` : `${days}d ago`;
}
