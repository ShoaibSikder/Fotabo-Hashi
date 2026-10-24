
export default function Card({ as: Element = 'div', className = '', inset = false, children, ...props }) {
  return <Element className={`${inset ? 'neu-in' : 'neu'} p-5 sm:p-6 ${className}`} {...props}>{children}</Element>;
}
