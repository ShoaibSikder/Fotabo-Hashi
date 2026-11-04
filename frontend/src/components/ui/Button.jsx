
import { Droplet, LoaderCircle } from 'lucide-react';

const variants = {
  primary: 'neu-red',
  secondary: '',
  ghost: 'bg-transparent !shadow-none hover:!shadow-none',
};

export default function Button({ variant = 'secondary', className = '', loading = false, loadingStyle = 'spinner', children, type = 'button', disabled = false, ...props }) {
  return (
    <button type={type} className={`neu-btn ${variants[variant] || ''} ${className}`} disabled={disabled || loading} aria-busy={loading || undefined} {...props}>
      {loading && (loadingStyle === 'donation' ? (
        <span className="donation-loading-mark" aria-hidden="true">
          <span className="donation-loading-pulse" />
          <Droplet size={17} className="donation-loading-drop" />
        </span>
      ) : <LoaderCircle size={17} className="animate-spin" aria-hidden="true" />)}
      {children}
    </button>
  );
}
