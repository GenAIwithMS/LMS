import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getRoleFromToken } from '../utils/jwt';

export const RoleRedirect: React.FC = () => {
  const { isAuthenticated, userRole } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Always redirect to dashboard for all roles
  return <Navigate to="/dashboard" replace />;
};

