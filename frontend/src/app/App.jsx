

import Providers from './providers.jsx';
import Router from './router.jsx';
import ErrorBoundary from '../components/errors/ErrorBoundary.jsx';
import GlobalErrorNotice from '../components/errors/GlobalErrorNotice.jsx';

export default function App() {
  return (
    <ErrorBoundary>
      <Providers>
        <GlobalErrorNotice />
        <Router />
      </Providers>
    </ErrorBoundary>
  );
}
