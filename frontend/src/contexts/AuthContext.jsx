
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { loginRequest, logoutRequest, getCurrentUser, registerRequest } from '../features/authentication/services/authService.js';
import { clearApiCache } from '../services/apiClient.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const current = await getCurrentUser();
      setUser(current || null);
      return current || null;
    } catch {
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshUser(); }, [refreshUser]);

  const login = useCallback(async (credentials) => {
    clearApiCache();
    const result = await loginRequest(credentials);
    if (result?.user) {
      setUser(result.user);
      setLoading(false);
      return result.user;
    }
    return refreshUser();
  }, [refreshUser]);

  const register = useCallback(async (details) => {
    clearApiCache();
    const result = await registerRequest(details);
    if (result?.user) {
      setUser(result.user);
      setLoading(false);
      return result.user;
    }
    return refreshUser();
  }, [refreshUser]);

  const logout = useCallback(() => {
    clearApiCache();
    setUser(null);
    setLoading(false);
    return logoutRequest().catch(() => null);
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
