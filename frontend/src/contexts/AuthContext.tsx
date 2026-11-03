import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin, logoutOnServer } from '../services/api';
import { getSavedLogin, saveLogin, clearSavedLogin, markPageLeft, userCameBackAfterLeaving } from '../utils/session';
import { decodeJWT, getRoleFromToken, isTokenExpired } from '../utils/jwt';
import type { User, LoginCredentials, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  replaceToken: (newToken: string) => void;
  isAuthenticated: boolean;
  userRole: UserRole | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Read the user's details out of a login token
const getUserFromToken = (token: string): User | null => {
  const decoded = decodeJWT(token);
  if (!decoded) {
    return null;
  }
  const role = getRoleFromToken(token);
  return {
    id: decoded.sub || decoded.id || decoded.user_id || 0,
    email: decoded.email || '',
    name: decoded.name || decoded.username || '',
    username: decoded.username || decoded.email || '',
    role: role || undefined,
  };
};

// The saved login, if there is one and it is still allowed
const getSavedToken = (): string | null => {
  const savedToken = getSavedLogin();
  if (!savedToken) {
    return null;
  }

  // Left the LMS (for example to another website) and came back: log out
  if (userCameBackAfterLeaving()) {
    clearSavedLogin();
    logoutOnServer(savedToken).catch(() => {});
    return null;
  }

  if (isTokenExpired(savedToken)) {
    clearSavedLogin();
    return null;
  }
  return savedToken;
};

// Milliseconds until the token expires (0 if it already has)
const getTimeLeft = (token: string): number => {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) {
    return 0;
  }
  const timeLeft = decoded.exp * 1000 - Date.now();
  if (timeLeft < 0) {
    return 0;
  }
  return timeLeft;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Read the saved login straight away, before the first render. Reading it later
  // (in useEffect) meant the first render thought nobody was logged in, so every
  // page refresh sent the user to the login page and then to the dashboard.
  const [token, setToken] = useState<string | null>(getSavedToken);
  const [user, setUser] = useState<User | null>(() => {
    if (token) {
      return getUserFromToken(token);
    }
    return null;
  });

  // Log out the moment the login expires (30 minutes), not on the next click
  useEffect(() => {
    if (!token) {
      return;
    }
    const timer = setTimeout(() => {
      clearSavedLogin();
      setToken(null);
      setUser(null);
      window.location.href = '/login?expired=1';
    }, getTimeLeft(token));
    return () => clearTimeout(timer);
  }, [token]);

  // Notice when the user leaves the LMS
  useEffect(() => {
    // The page is going away: tab closed, another site opened, or a refresh.
    // On the next load we can tell a refresh apart from coming back.
    const handlePageHide = () => {
      markPageLeft();
    };

    // The browser can restore the page from memory when the user presses Back.
    // That skips the normal start-up check, so log out here.
    const handlePageShow = (event: PageTransitionEvent) => {
      if (event.persisted) {
        const savedToken = getSavedLogin();
        clearSavedLogin();
        if (savedToken) {
          logoutOnServer(savedToken).catch(() => {});
        }
        window.location.href = '/login';
      }
    };

    window.addEventListener('pagehide', handlePageHide);
    window.addEventListener('pageshow', handlePageShow);
    return () => {
      window.removeEventListener('pagehide', handlePageHide);
      window.removeEventListener('pageshow', handlePageShow);
    };
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await apiLogin(credentials);
      // Read the user's details out of the token
      const userData = getUserFromToken(response.token);
      saveLogin(response.token, userData);
      setToken(response.token);
      setUser(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  // Used after the user changes their username: the server sends a new token
  // with the new username in it, and we read the user details from it again.
  const replaceToken = (newToken: string) => {
    const userData = getUserFromToken(newToken);
    saveLogin(newToken, userData);
    setToken(newToken);
    setUser(userData);
  };

  const logout = () => {
    // Block the token on the server too, so it can't be used again
    if (token) {
      logoutOnServer(token).catch(() => {});
    }
    clearSavedLogin();
    setToken(null);
    setUser(null);
  };

  // Get role from user object or decode from token
  const userRole: UserRole | null = user?.role || (token ? getRoleFromToken(token) : null);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        replaceToken,
        isAuthenticated: !!token,
        userRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

