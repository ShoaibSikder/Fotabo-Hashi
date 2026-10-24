
import { LoaderCircle } from 'lucide-react';

export default function Spinner({ label = 'Loading', className = '' }) {
  return <span className={`inline-flex items-center gap-2 text-sm font-semibold text-muted ${className}`} role="status"><LoaderCircle className="animate-spin text-brand" size={18} /><span>{label}</span></span>;
}
