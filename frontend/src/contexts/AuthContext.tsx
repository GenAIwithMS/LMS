import React, { createContext, useContext, useState, ReactNode } from 'react';
import { login as apiLogin } from '../services/api';
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

// The saved login, if there is one and it has not expired yet
const getSavedToken = (): string | null => {
  const savedToken = localStorage.getItem('token');
  if (!savedToken) {
    return null;
  }
  if (isTokenExpired(savedToken)) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return null;
  }
  return savedToken;
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

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await apiLogin(credentials);
      setToken(response.token);
      localStorage.setItem('token', response.token);
      
      // Read the user's details out of the token
      const userData = getUserFromToken(response.token);
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  // Used after the user changes their username: the server sends a new token
  // with the new username in it, and we read the user details from it again.
  const replaceToken = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);

    const userData = getUserFromToken(newToken);
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
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

