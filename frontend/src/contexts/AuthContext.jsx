
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { loginRequest, logoutRequest, getCurrentUser, registerRequest } from '../features/authentication/services/authService.js';
import { apiGet } from '../services/apiClient.js';
import { API_ENDPOINTS } from '../services/endpointConfig.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const current = await getCurrentUser();
      if (!current) {
        setUser(null);
        return null;
      }

      let profile = null;
      try {
        profile = await apiGet(API_ENDPOINTS.profile);
      } catch {
        // Keep the authenticated session usable if profile data is unavailable.
      }

      const sessionUser = {
        ...current,
        name: profile?.name || current.name || '',
      };
      setUser(sessionUser);
      return sessionUser;
    } catch {
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshUser(); }, [refreshUser]);

  const login = useCallback(async (credentials) => {
    await loginRequest(credentials);
    return refreshUser();
  }, [refreshUser]);

  const register = useCallback(async (details) => {
    await registerRequest(details);
    return refreshUser();
  }, [refreshUser]);

  const logout = useCallback(async () => {
    try { await logoutRequest(); } finally { setUser(null); }
  }, []);

  const clearSession = useCallback(() => setUser(null), []);

  const value = useMemo(() => ({ user, loading, login, register, logout, clearSession, refreshUser }), [user, loading, login, register, logout, clearSession, refreshUser]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthCtx() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuthCtx must be used inside AuthProvider');
  return context;
}
