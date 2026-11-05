import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SearchX } from 'lucide-react';

// Shown for an address that doesn't exist (for example a mistyped link)
const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="card max-w-lg mx-auto text-center py-12">
      <SearchX size={48} className="mx-auto text-gray-300 mb-4" />
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Page not found</h1>
      <p className="text-gray-600 mb-6">This page doesn't exist. Use the menu, or go back to your dashboard.</p>
      <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
        Go to the dashboard
      </button>
    </div>
  );
};

export default NotFound;
