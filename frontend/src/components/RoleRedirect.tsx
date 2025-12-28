import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getRoleFromToken } from '../utils/jwt';

export const RoleRedirect: React.FC = () => {
  const { isAuthenticated, userRole } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Get role from token if not in context
  const token = localStorage.getItem('token');
  const role = userRole || (token ? getRoleFromToken(token) : null);

  // Redirect based on role
  if (role === 'admin') {
    return <Navigate to="/admin/students" replace />;
  } else if (role === 'teacher') {
    return <Navigate to="/teacher/assignments" replace />;
  } else if (role === 'student') {
    return <Navigate to="/student/assignments" replace />;
  }

  // Fallback to dashboard
  return <Navigate to="/dashboard" replace />;
};

