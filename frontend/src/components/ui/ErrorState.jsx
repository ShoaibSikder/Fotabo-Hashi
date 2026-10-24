
import { AlertCircle } from 'lucide-react';
import Button from './Button.jsx';

export default function ErrorState({ message, onRetry }) {
  return <div role="alert" className="flex flex-col items-center gap-3 rounded-2xl border border-red-200 bg-red-50 px-6 py-9 text-center"><AlertCircle className="text-brand" size={24} /><p className="max-w-lg text-sm text-slate-700">{message}</p>{onRetry && <Button onClick={onRetry}>Try again</Button>}</div>;
}
