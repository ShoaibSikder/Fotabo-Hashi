

import Providers from './providers.jsx';
import Router from './router.jsx';
import ErrorBoundary from '../components/errors/ErrorBoundary.jsx';
import GlobalErrorNotice from '../components/errors/GlobalErrorNotice.jsx';
import SeoManager from '../components/seo/SeoManager.jsx';

export default function App() {
  return (
    <ErrorBoundary>
      <Providers>
        <SeoManager />
        <GlobalErrorNotice />
        <Router />
      </Providers>
    </ErrorBoundary>
  );
}
