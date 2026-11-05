import toast from 'react-hot-toast';

export interface ApiError {
  message?: string;
  error?: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

// A field name from the server as people read it: "start_date" -> "Start date"
const fieldLabel = (field: string): string => {
  const words = field.replace(/_/g, ' ').trim();
  if (words === '') {
    return 'This field';
  }
  return words.charAt(0).toUpperCase() + words.slice(1);
};

// The server's wording for a field problem, in plain words
const plainFieldMessage = (message: string): string => {
  let match = message.match(/^Shorter than minimum length (\d+)\.?$/);
  if (match) {
    return `must be at least ${match[1]} characters`;
  }
  match = message.match(/^Longer than maximum length (\d+)\.?$/);
  if (match) {
    return `must be at most ${match[1]} characters`;
  }
  match = message.match(/^Length must be between (\d+) and (\d+)\.?$/);
  if (match) {
    return `must be ${match[1]} to ${match[2]} characters`;
  }
  if (message.startsWith('Missing data for required field')) {
    return 'is required';
  }
  if (message.startsWith('Not a valid email')) {
    return 'is not a valid email address';
  }
  if (message.startsWith('Not a valid date')) {
    return 'is not a valid date';
  }
  if (message.startsWith('Not a valid integer') || message.startsWith('Not a valid number')) {
    return 'must be a number';
  }
  if (message.startsWith('Field may not be null')) {
    return 'is required';
  }
  if (message.startsWith('Unknown field')) {
    return 'is not expected';
  }
  match = message.match(/^Must be greater than or equal to ([\d.]+) and less than or equal to ([\d.]+)\.?$/);
  if (match) {
    return `must be between ${match[1]} and ${match[2]}`;
  }
  match = message.match(/^Must be one of: (.*)\.?$/);
  if (match) {
    return `must be one of: ${match[1].replace(/\.$/, '')}`;
  }
  // Anything else: the server's own words
  return message.charAt(0).toLowerCase() + message.slice(1).replace(/\.$/, '');
};

// Field problems sent by the server, like {"password": ["Shorter than minimum length 6."]},
// as sentences: "Password must be at least 6 characters". Empty text if the data isn't like that.
const describeFieldErrors = (data: any, prefix: string = ''): string => {
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return '';
  }
  const sentences: string[] = [];
  for (const field of Object.keys(data)) {
    const value = data[field];
    // Rows of a list (like "records" -> "0" -> "status") are shown as "Row 1"
    let label = fieldLabel(field);
    if (/^\d+$/.test(field)) {
      label = `Row ${Number(field) + 1}`;
    }
    if (prefix !== '') {
      label = `${prefix} ${label.toLowerCase()}`;
    }
    if (Array.isArray(value)) {
      for (const message of value) {
        if (typeof message === 'string') {
          sentences.push(`${label} ${plainFieldMessage(message)}`);
        }
      }
    } else if (value && typeof value === 'object') {
      const inner = describeFieldErrors(value, label);
      if (inner !== '') {
        sentences.push(inner);
      }
    }
  }
  return sentences.join('. ');
};

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
    
    // Field problems from the server's form checks, like {"name": ["Shorter than minimum length 4."]}
    const fieldErrors = describeFieldErrors(data);
    if (fieldErrors !== '') {
      return fieldErrors;
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
  // No error object: just show the message given
  if (!error) {
    toast.error(defaultMessage);
    return;
  }
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

