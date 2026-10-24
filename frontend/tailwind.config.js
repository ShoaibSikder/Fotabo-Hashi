

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: '#B91C1C', dark: '#7F1D1D', soft: '#FDECEC' },
        surface: '#F5F5F7',
        ink: '#0F172A',
        muted: '#475569',
      },
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        heading: ['Manrope', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 4px 12px rgba(15, 23, 42, 0.08)',
        'soft-sm': '0 1px 4px rgba(15, 23, 42, 0.08)',
        inset: 'inset 0 1px 2px rgba(15, 23, 42, 0.04)',
      },
    },
  },
  plugins: [],
};
