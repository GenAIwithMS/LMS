import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin } from '../services/api';
import { decodeJWT, getRoleFromToken } from '../utils/jwt';
import type { User, LoginCredentials, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  userRole: UserRole | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    
    if (storedToken) {
      setToken(storedToken);
      
      // Always decode fresh user data from token to ensure we have latest info
      const decoded = decodeJWT(storedToken);
      const role = getRoleFromToken(storedToken);
      
      if (decoded) {
        const userData: User = {
          id: decoded.sub || decoded.id || decoded.user_id || 0,
          email: decoded.email || '',
          name: decoded.name || decoded.username || '',
          username: decoded.username || decoded.email || '',
          role: role || undefined,
        };
        
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      }
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await apiLogin(credentials);
      setToken(response.token);
      localStorage.setItem('token', response.token);
      
      // Decode JWT token to get user info
      const decoded = decodeJWT(response.token);
      const role = getRoleFromToken(response.token);
      
      const userData: User = {
        id: decoded.sub || decoded.id || decoded.user_id || 0,
        email: decoded.email || credentials.email,
        name: decoded.name || decoded.username || '',
        username: decoded.username || decoded.email || '',
        role: role || undefined,
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Clear chat history on logout
    sessionStorage.removeItem('lms_chatbot_history');
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

