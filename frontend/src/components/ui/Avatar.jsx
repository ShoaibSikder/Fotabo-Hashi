
import { initials } from '../../utils/formatters.js';

export default function Avatar({ name, size = 'md', className = '' }) {
  const dimensions = { sm: 'h-9 w-9 text-xs', md: 'h-12 w-12 text-sm', lg: 'h-20 w-20 text-xl' };
  return (
    <span className={`inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-soft font-extrabold text-brand ${dimensions[size] || dimensions.md} ${className}`}>
      {initials(name)}
    </span>
  );
}
