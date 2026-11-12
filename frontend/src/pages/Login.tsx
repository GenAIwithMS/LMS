import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft } from 'lucide-react';
import Crest from '../components/Crest';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Sent here because the login expired
  useEffect(() => {
    if (searchParams.get('expired') === '1') {
      toast.error('Your session has expired. Please log in again.', { id: 'session-expired' });
    }
  }, [searchParams]);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login({ email, password });
      toast.success('Login successful!');
      
      // Redirect to dashboard for all users
      setTimeout(() => {
        navigate('/dashboard');
      }, 100);
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-paper">
      {/* The cover: green, with the faint ruling of a register page */}
      <aside
        className="hidden lg:flex lg:w-[42%] xl:w-[38%] bg-primary-800 text-primary-100 flex-col justify-between p-12"
        style={{ backgroundImage: 'repeating-linear-gradient(to bottom, transparent 0, transparent 39px, rgba(255,255,255,0.05) 39px, rgba(255,255,255,0.05) 40px)' }}
      >
        <Link to="/" className="flex items-center gap-3 w-fit">
          <Crest size={40} />
          <span className="font-serif text-2xl font-semibold text-white tracking-tight">The Lyceum</span>
        </Link>
        <div>
          <p className="font-serif text-[2.4rem] leading-[1.15] font-semibold text-white tracking-tight max-w-sm">
            Attendance, marks and homework, kept in one register.
          </p>
          <p className="mt-4 text-primary-200 max-w-sm">
            For the school office, teachers and students.
          </p>
        </div>
        <p className="text-sm text-primary-300">Accounts are made by the school office.</p>
      </aside>

      {/* The form */}
      <main className="flex-1 flex items-center justify-center px-5 py-12">
        <div className="w-full max-w-sm">
          <Link to="/" className="lg:hidden flex items-center gap-2.5 mb-10">
            <Crest size={34} />
            <span className="font-serif text-xl font-semibold text-gray-900 tracking-tight">The Lyceum</span>
          </Link>

          <h1 className="text-[2rem] font-semibold text-gray-900">Sign in</h1>
          <p className="text-gray-600 mt-1.5">Use the email and password the school gave you.</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-800 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input py-2.5"
                placeholder="name@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-800 mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input py-2.5"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-2.5 disabled:opacity-70"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <Link
            to="/"
            className="mt-8 inline-flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft size={15} />
            Back to the homepage
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Login;
