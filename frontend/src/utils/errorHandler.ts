import toast from 'react-hot-toast';

export interface ApiError {
  message?: string;
  error?: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

/**
 * Extracts error message from API error response
 */
export const getErrorMessage = (error: any): string => {
  if (!error) {
    return 'An unexpected error occurred';
  }

  // Axios error structure
  if (error.response) {
    const data = error.response.data;
    
    // Check for different error message formats
    if (typeof data === 'string') {
      return data;
    }
    
    if (data?.message) {
      return data.message;
    }
    
    if (data?.error) {
      return data.error;
    }
    
    if (data?.detail) {
      return data.detail;
    }
    
    // Handle validation errors
    if (data?.errors && typeof data.errors === 'object') {
      const errorMessages = Object.entries(data.errors)
        .map(([field, messages]) => {
          const msgArray = Array.isArray(messages) ? messages : [messages];
          return `${field}: ${msgArray.join(', ')}`;
        })
        .join('; ');
      
      if (errorMessages) {
        return errorMessages;
      }
    }
    
    // Fallback to status text
    if (error.response.statusText) {
      return `${error.response.status}: ${error.response.statusText}`;
    }
  }
  
  // Network error
  if (error.message) {
    if (error.message.includes('Network Error') || error.message.includes('timeout')) {
      return 'Network error. Please check your connection and try again.';
    }
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

/**
 * Shows error toast with proper error message
 */
export const showError = (error: any, defaultMessage: string = 'Operation failed') => {
  const message = getErrorMessage(error);
  toast.error(message || defaultMessage);
  console.error('Error details:', error);
};

/**
 * Shows success toast
 */
export const showSuccess = (message: string) => {
  toast.success(message);
};

