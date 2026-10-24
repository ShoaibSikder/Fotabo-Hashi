

import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext.jsx';
import { LanguageProvider } from '../contexts/LanguageContext.jsx';

export default function Providers({ children }) {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>{children}</AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
}
