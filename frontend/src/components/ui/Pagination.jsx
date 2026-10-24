
import Button from './Button.jsx';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ page, count, pageSize = 20, onChange }) {
  const pages = Math.max(1, Math.ceil((count || 0) / pageSize));
  return <div className="flex items-center justify-between gap-2 text-xs text-muted sm:text-sm"><span className="shrink-0">Page {page} of {pages}</span><div className="flex shrink-0 gap-2"><Button aria-label="Previous page" className="!min-h-10 !px-3 sm:!px-4" disabled={page <= 1} onClick={() => onChange(page - 1)}><ChevronLeft size={16} aria-hidden="true" /><span className="sr-only sm:not-sr-only">Previous</span></Button><Button aria-label="Next page" className="!min-h-10 !px-3 sm:!px-4" disabled={page >= pages} onClick={() => onChange(page + 1)}><span className="sr-only sm:not-sr-only">Next</span><ChevronRight size={16} aria-hidden="true" /></Button></div></div>;
}
