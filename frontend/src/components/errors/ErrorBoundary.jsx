import { Component } from 'react';

export default class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled interface error', error, errorInfo);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    const isBangla = document.documentElement.lang === 'bn';

    return (
      <main className="grid min-h-screen place-items-center bg-[#f5f5f7] px-4 py-12 text-ink">
        <section role="alert" className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-7 text-center shadow-sm sm:p-9">
          <h1 className="font-heading text-2xl font-extrabold text-brand-dark">{isBangla ? 'কিছু একটা সমস্যা হয়েছে' : 'Something went wrong'}</h1>
          <p className="mt-3 leading-6 text-slate-600">{isBangla ? 'পৃষ্ঠাটি দেখানো যাচ্ছে না। অনুগ্রহ করে আবার চেষ্টা করুন।' : 'The page could not be displayed. Please try again.'}</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <button type="button" onClick={() => window.location.reload()} className="min-h-11 cursor-pointer rounded-xl bg-brand px-5 font-bold text-white transition-colors hover:bg-brand-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">
              {isBangla ? 'পুনরায় লোড করুন' : 'Reload page'}
            </button>
            <a href="/" className="inline-flex min-h-11 items-center rounded-xl border border-slate-200 px-5 font-bold text-slate-700 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">
              {isBangla ? 'হোমে যান' : 'Go to home'}
            </a>
          </div>
        </section>
      </main>
    );
  }
}
