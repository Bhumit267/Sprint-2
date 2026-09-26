'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authSignup } from '@/lib/api';

export default function SignupPage() {
  const router = useRouter();
  const [orgName, setOrgName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authSignup(orgName, email, password);
      // Immediately redirect to login on success
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
      <div className="archive-card w-full max-w-md p-8 sm:p-10 rounded-2xl shadow-xl border border-study-border/50">
        
        {/* Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="w-12 h-12 mx-auto bg-primary text-accent rounded-xl flex items-center justify-center text-2xl font-serif font-bold shadow-inner mb-4">
            D
          </div>
          <h1 className="text-2xl font-serif font-semibold text-primary dark:text-[#EDE7D9]">Create Organization</h1>
          <p className="text-sm text-study-text/70 dark:text-study-text-dark/70 font-sans">
            Register a new workspace on DocDrift
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 p-3 rounded-lg bg-warning/10 border border-warning/20 text-warning text-xs font-mono text-center">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSignup} className="space-y-5">
          <div className="space-y-1.5">
            <label className="block text-[11px] font-mono uppercase tracking-widest text-study-text/70 ml-1">
              Organization Name
            </label>
            <input
              type="text"
              required
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-study-bg/50 border border-study-border focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all text-sm font-sans"
              placeholder="e.g. Acme Corp"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-[11px] font-mono uppercase tracking-widest text-study-text/70 ml-1">
              Admin Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-study-bg/50 border border-study-border focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all text-sm font-sans"
              placeholder="admin@acme.com"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-[11px] font-mono uppercase tracking-widest text-study-text/70 ml-1">
              Admin Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-study-bg/50 border border-study-border focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all text-sm font-sans"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-accent hover:bg-accent-hover text-[#161A16] font-mono font-bold uppercase tracking-wider text-xs transition-colors shadow-md disabled:opacity-50 mt-4"
          >
            {loading ? 'Creating...' : 'Register Workspace'}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-study-border/30 pt-6">
          <p className="text-xs text-study-text/60 font-sans">
            Already have an organization?{' '}
            <Link href="/login" className="text-accent hover:underline font-medium">
              Log in instead
            </Link>
          </p>
        </div>

      </div>
    </div>
  );
}
