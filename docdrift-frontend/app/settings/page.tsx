'use client';

import React, { useEffect, useState } from 'react';
import Navigation from '@/components/Navigation';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function SettingsPage() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('docdrift-theme');
      const isDarkMode = stored
        ? stored === 'dark'
        : document.documentElement.classList.contains('dark') ||
          window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDark(isDarkMode);
    } catch {
      // Ignore
    }
  }, []);

  const handleToggleTheme = () => {
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
      // Ignore
    }
  };

  return (
    <ProtectedRoute allowedRoles={['maintainer', 'admin', 'employee']}>
      <div className="min-h-screen flex flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
        <Navigation />

      <main className="flex-1 p-4 sm:p-8 md:p-12 max-w-3xl mx-auto w-full space-y-6">
        {/* Header */}
        <header className="border-b border-study-border/70 dark:border-study-border-dark/70 pb-4">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-accent font-semibold">
              Preferences &amp; System Info
            </span>
          </div>
          <h1 className="font-serif text-3xl font-semibold text-primary dark:text-[#EDE7D9]">
            Desk Settings
          </h1>
          <p className="text-xs text-study-text/60 dark:text-study-text-dark/60 font-mono mt-1">
            System configuration, team provenance, and interface preferences
          </p>
        </header>

        {/* Settings Card */}
        <div className="archive-card rounded-xl p-6 space-y-6 shadow-xs">
          {/* Appearance Section */}
          <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-study-border/50 dark:border-study-border-dark/50 pb-5">
            <div>
              <h2 className="font-serif text-base font-semibold text-primary dark:text-[#EDE7D9]">
                Study Theme &amp; Appearance
              </h2>
              <p className="text-xs text-study-text/70 dark:text-study-text-dark/70 font-sans mt-0.5">
                Toggle between warm English parchment and deep archival study mode. Persists across sessions.
              </p>
            </div>

            <button
              type="button"
              onClick={handleToggleTheme}
              className="inline-flex items-center gap-2 rounded-lg border border-accent bg-accent/10 hover:bg-accent/20 px-4 py-2 text-xs font-mono text-accent transition-all cursor-pointer shrink-0"
            >
              <span>{isDark ? '☀ Switch to Light Mode' : '☾ Switch to Dark Mode'}</span>
            </button>
          </section>

          {/* Team Provenance Section */}
          <section className="border-b border-study-border/50 dark:border-study-border-dark/50 pb-5 space-y-2">
            <h2 className="font-serif text-base font-semibold text-primary dark:text-[#EDE7D9]">
              Engineering Team
            </h2>
            <div className="rounded-lg border border-study-border/60 dark:border-study-border-dark/60 bg-[#F5EFE4] dark:bg-[#151915] p-3.5 flex items-center justify-between">
              <div>
                <p className="font-serif font-bold text-sm text-primary dark:text-[#EDE7D9]">
                  Team GroundTruth
                </p>
                <p className="text-xs text-study-text/70 dark:text-study-text-dark/70 font-mono mt-0.5">
                  DocDrift: Version-Aware Documentation Intelligence System
                </p>
              </div>
              <span className="rounded bg-accent/15 text-accent border border-accent/30 px-2 py-0.5 text-[10px] font-mono font-semibold uppercase">
                Active
              </span>
            </div>
          </section>

          {/* Service Endpoints & Tech Specs */}
          <section className="space-y-4">
            <h2 className="font-serif text-base font-semibold text-primary dark:text-[#EDE7D9]">
              Service Configuration
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="rounded-lg border border-study-border/50 dark:border-study-border-dark/50 p-3 space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
                  Backend API Endpoint
                </span>
                <p className="font-mono text-primary dark:text-[#EDE7D9] break-all">
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                </p>
              </div>

              <div className="rounded-lg border border-study-border/50 dark:border-study-border-dark/50 p-3 space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
                  Inference Provider
                </span>
                <p className="font-sans font-medium text-primary dark:text-[#EDE7D9]">
                  Ollama Cloud (gemma4:31b)
                </p>
              </div>

              <div className="rounded-lg border border-study-border/50 dark:border-study-border-dark/50 p-3 space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
                  Vector Database
                </span>
                <p className="font-sans font-medium text-primary dark:text-[#EDE7D9]">
                  Chroma Collection (docdrift_docs)
                </p>
              </div>

              <div className="rounded-lg border border-study-border/50 dark:border-study-border-dark/50 p-3 space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
                  Grounding Mandate
                </span>
                <p className="font-sans text-study-text/80 dark:text-study-text-dark/80">
                  Strict version-isolation with automated refusal on ungrounded queries
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
    </ProtectedRoute>
  );
}
