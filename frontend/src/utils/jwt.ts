// Simple JWT decoder (for client-side use only)
export const decodeJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
};

export const getRoleFromToken = (token: string): 'admin' | 'teacher' | 'student' | null => {
  const decoded = decodeJWT(token);
  if (!decoded) return null;
  
  // The role might be in different fields depending on your backend
  // Common field names: role, user_type, type, user_role
  const role = decoded.role || decoded.user_type || decoded.type || decoded.user_role;
  
  if (role) {
    const roleLower = role.toLowerCase();
    if (roleLower === 'admin' || roleLower === 'teacher' || roleLower === 'student') {
      return roleLower as 'admin' | 'teacher' | 'student';
    }
  }
  
  return null;
};

