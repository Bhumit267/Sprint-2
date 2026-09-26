'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { getCurrentUser, authLogout } from '@/lib/api';

export default function Navigation() {
  const pathname = usePathname();
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [user, setUser] = useState<{ email: string; role: string; org_id: string | null; org_name: string | null } | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('docdrift-theme');
      const isDarkMode = stored
        ? stored === 'dark'
        : document.documentElement.classList.contains('dark') ||
          window.matchMedia('(prefers-color-scheme: dark)').matches;

      setIsDark(isDarkMode);
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch {
      // Ignore localStorage errors
    }

    // Fetch current user
    getCurrentUser().then(userData => {
      if (userData) {
        setUser(userData);
      }
    });
  }, []);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    try {
      localStorage.setItem('docdrift-theme', nextDark ? 'dark' : 'light');
      if (nextDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch {
      // Ignore localStorage errors
    }
  };

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/chat', label: 'Chat' },
    { href: '/documents', label: 'Documents' },
  ];

  if (user?.role === 'admin') {
    navLinks.push({ href: '/admin/upload', label: 'Upload' });
  }

  if (user?.role === 'admin' || user?.role === 'employee') {
    navLinks.push({ href: '/organization', label: 'Team' });
  }

  if (user?.role === 'maintainer') {
    navLinks.push({ href: '/admin/organizations', label: 'Tenants' });
  }

  navLinks.push({ href: '/settings', label: 'Settings' });

  return (
    <nav className="shrink-0 border-b border-study-border/70 dark:border-study-border-dark/70 bg-primary text-[#EDE7D9] px-4 sm:px-6 py-3 shadow-xs">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <Link href="/" className="group flex items-center gap-2">
            <span className="font-serif text-lg sm:text-xl font-bold tracking-tight text-[#FAF6EE] group-hover:text-accent transition-colors">
              DocDrift
            </span>
            <span className="text-[10px] font-mono uppercase tracking-widest text-accent bg-accent/10 border border-accent/20 px-2 py-0.5 rounded-full hidden sm:inline">
              Archive
            </span>
          </Link>
        </div>

        {/* Desktop Navigation Links */}
        <div className="hidden sm:flex items-center gap-1 md:gap-2">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                  isActive
                    ? 'bg-accent/20 text-accent font-semibold border border-accent/30'
                    : 'text-[#EDE7D9]/80 hover:text-accent hover:bg-white/5'
                }`}
              >
                {link.label}
              </Link>
            );
          })}

          <div className="h-4 w-px bg-white/15 mx-1" />

          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle visual theme"
            className="rounded border border-accent/30 bg-accent/10 hover:bg-accent/20 px-2.5 py-1 text-xs font-mono text-accent transition-all cursor-pointer flex items-center gap-1"
          >
            <span>{isDark ? '☀' : '☾'}</span>
            <span className="text-[11px] hidden md:inline">{isDark ? 'Light' : 'Dark'}</span>
          </button>
          
          <div className="h-4 w-px bg-white/15 mx-1" />
          
          {/* User Profile */}
          {user ? (
            <div className="relative">
              <button 
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 transition-colors px-3 py-1 text-xs font-mono cursor-pointer text-left"
              >
                <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" title="Online" />
                <div className="flex flex-col">
                  <span className="text-[#EDE7D9]/90 truncate max-w-[120px] lg:max-w-[180px] leading-tight">{user.email}</span>
                  <span className="text-[9px] text-accent/80 uppercase tracking-wider leading-tight">
                    {user.role}{user.org_name ? ` • ${user.org_name}` : ''}
                  </span>
                </div>
              </button>
              
              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-36 rounded-lg border border-study-border/50 bg-[#161A16] shadow-lg overflow-hidden z-50">
                  <button
                    onClick={() => authLogout()}
                    className="w-full text-left px-4 py-2.5 text-xs font-mono text-warning hover:bg-warning/10 transition-colors cursor-pointer"
                  >
                    Log out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="rounded border border-accent/30 bg-accent/10 hover:bg-accent/20 px-3 py-1 text-xs font-mono text-accent transition-all flex items-center"
            >
              Log in
            </Link>
          )}
        </div>

        {/* Mobile Nav Controls */}
        <div className="flex sm:hidden items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle visual theme"
            className="rounded border border-accent/30 bg-accent/10 px-2 py-1 text-xs font-mono text-accent cursor-pointer"
          >
            {isDark ? '☀' : '☾'}
          </button>

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            className="rounded border border-white/20 px-2.5 py-1 text-xs font-mono text-[#EDE7D9] hover:bg-white/10"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="sm:hidden mt-2 pt-2 border-t border-white/10 flex flex-col gap-1 pb-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2 rounded text-xs font-mono transition-all ${
                  isActive
                    ? 'bg-accent/20 text-accent font-semibold'
                    : 'text-[#EDE7D9]/80 hover:text-accent hover:bg-white/5'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          
          <div className="my-1 border-t border-white/10" />
          
          {user ? (
            <div className="flex flex-col gap-2 px-2 py-1 mx-1">
              <div className="px-2 py-2 flex items-center gap-3 bg-white/5 rounded">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                <div className="flex flex-col">
                  <span className="text-[#EDE7D9] text-xs font-mono">{user.email}</span>
                  <span className="text-[10px] text-accent/80 font-mono uppercase tracking-wider">
                    {user.role}{user.org_name ? ` • ${user.org_name}` : ''}
                  </span>
                </div>
              </div>
              <button
                onClick={() => authLogout()}
                className="text-left px-3 py-2 text-xs font-mono text-warning hover:bg-warning/10 rounded transition-colors"
              >
                Log out
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded text-xs font-mono text-accent hover:bg-accent/10 transition-all mx-1"
            >
              Log in
            </Link>
          )}
        </div>
      )}
    </nav>
  );
}
