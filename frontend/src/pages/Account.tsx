import React, { useState, useEffect } from 'react';
import { UserCircle, KeyRound, AtSign } from 'lucide-react';
import { getMyAccount, updateMyUsername, changeMyPassword } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

interface AccountDetails {
  name: string;
  email: string;
  username: string;
  role: string;
}

// Read the error message from a failed request.
// Validation errors come back as { field: ["message"] } instead of { message }.
const getRequestError = (error: any, fallback: string) => {
  const data = error.response?.data;
  if (data?.message) {
    return data.message;
  }
  if (data && typeof data === 'object') {
    const firstField = Object.values(data)[0];
    if (Array.isArray(firstField) && firstField.length > 0) {
      return firstField[0];
    }
  }
  return error.message || fallback;
};

const Account: React.FC = () => {
  const { replaceToken } = useAuth();
  const [account, setAccount] = useState<AccountDetails | null>(null);
  const [loading, setLoading] = useState(true);

  const [newUsername, setNewUsername] = useState('');
  const [savingUsername, setSavingUsername] = useState(false);

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    fetchAccount();
  }, []);

  const fetchAccount = async () => {
    try {
      setLoading(true);
      const data = await getMyAccount();
      setAccount(data.account);
      setNewUsername(data.account.username);
    } catch (error: any) {
      toast.error(getRequestError(error, 'Failed to load your account'));
    } finally {
      setLoading(false);
    }
  };

  const handleUsernameSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const username = newUsername.trim();
    if (!account) {
      return;
    }
    if (username.length < 3) {
      toast.error('Username must be at least 3 characters');
      return;
    }
    if (username === account.username) {
      toast.error('This is already your username');
      return;
    }

    try {
      setSavingUsername(true);
      const data = await updateMyUsername(username);
      // The server sends a new token that has the new username in it
      replaceToken(data.token);
      setAccount({ ...account, username: username });
      toast.success('Username updated successfully');
    } catch (error: any) {
      toast.error(getRequestError(error, 'Failed to update username'));
    } finally {
      setSavingUsername(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordData.new_password.length < 6) {
      toast.error('New password must be at least 6 characters');
      return;
    }
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    try {
      setSavingPassword(true);
      await changeMyPassword(passwordData.current_password, passwordData.new_password);
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      toast.success('Password changed successfully');
    } catch (error: any) {
      toast.error(getRequestError(error, 'Failed to change password'));
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Account</h1>
        <p className="text-gray-600 mt-2">View your details and change your username or password</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl">
        {/* Account details */}
        <div className="card lg:col-span-2">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center text-primary-700 border-2 border-primary-300">
              <UserCircle size={32} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{account?.name}</h2>
              <p className="text-sm text-gray-500">{account?.email}</p>
              <p className="text-sm text-gray-500">
                Username: <span className="font-medium text-gray-800">{account?.username}</span>
                <span className="mx-2">·</span>
                <span className="capitalize">{account?.role}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Change username */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <AtSign size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Change Username</h2>
          </div>
          <form onSubmit={handleUsernameSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">New Username</label>
              <input
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                className="input"
                minLength={3}
                maxLength={100}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={savingUsername}>
              {savingUsername ? 'Saving...' : 'Update Username'}
            </button>
          </form>
        </div>

        {/* Change password */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <KeyRound size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Change Password</h2>
          </div>
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
              <input
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                className="input"
                autoComplete="current-password"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                className="input"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                className="input"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={savingPassword}>
              {savingPassword ? 'Saving...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Account;
