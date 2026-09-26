'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authLogin } from '../../lib/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await authLogin(email, password);
      // Store token and user role
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.user.role);
      
      if (data.user.role === 'maintainer') {
        router.push('/admin/organizations');
      } else {
        router.push('/chat');
      }
    } catch (err: unknown) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md bg-white dark:bg-[#1C2B24] rounded-lg shadow-xl p-8 border border-border">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-serif text-primary dark:text-accent mb-2">DocDrift</h1>
          <p className="text-text/70 dark:text-text/70">Sign in to your account</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-warning/10 border border-warning/20 text-warning rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-text mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 rounded-md border border-border bg-transparent text-text focus:outline-none focus:ring-2 focus:ring-accent/50"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-md border border-border bg-transparent text-text focus:outline-none focus:ring-2 focus:ring-accent/50"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-accent hover:bg-accent/90 text-white rounded-md transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <div className="mt-8 text-center border-t border-study-border/30 pt-6">
          <p className="text-xs text-study-text/60 font-sans">
            Don't have a workspace?{' '}
            <Link href="/signup" className="text-accent hover:underline font-medium">
              Create an organization
            </Link>
          </p>
        </div>

      </div>
    </div>
  );
}
