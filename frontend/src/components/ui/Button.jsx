
import { LoaderCircle } from 'lucide-react';

const variants = {
  primary: 'neu-red',
  secondary: '',
  ghost: 'bg-transparent !shadow-none hover:!shadow-none',
};

export default function Button({ variant = 'secondary', className = '', loading = false, children, type = 'button', disabled = false, ...props }) {
  return (
    <button type={type} className={`neu-btn ${variants[variant] || ''} ${className}`} disabled={disabled || loading} {...props}>
      {loading && <LoaderCircle size={17} className="animate-spin" aria-hidden="true" />}
      {children}
    </button>
  );
}
