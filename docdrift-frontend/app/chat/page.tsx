'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Navigation from '@/components/Navigation';
import ChatMessage from '@/components/ChatMessage';
import VersionDropdown from '@/components/VersionDropdown';
import ProtectedRoute from '@/components/ProtectedRoute';
import { ChatEntry } from '@/lib/types';
import { askQuestion, getVersions } from '@/lib/api';

function ChatContent() {
  const searchParams = useSearchParams();
  const [entries, setEntries] = useState<ChatEntry[]>([]);
  const [input, setInput] = useState('');
  const [availableVersions, setAvailableVersions] = useState<string[]>([]);
  const [activeVersion, setActiveVersion] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const initialTriggered = useRef(false);

  // Auto-scroll to bottom as entries change or answers arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [entries]);

  // Fetch available versions dynamically from GET /versions
  useEffect(() => {
    async function fetchDocVersions() {
      try {
        const versions = await getVersions();

        if (versions.length > 0) {
          setAvailableVersions(versions);
          const paramVersion = searchParams.get('v');
          if (paramVersion && versions.includes(paramVersion)) {
            setActiveVersion(paramVersion);
          } else if (!paramVersion) {
            setActiveVersion(versions[0]);
          }
        }
      } catch (err) {
        console.error('Failed to retrieve versions from /documents:', err);
      }
    }

    fetchDocVersions();
  }, [searchParams]);

  // Execute an inquiry and update state
  const executeQuestion = async (questionText: string, version: string) => {
    const entryId = Date.now().toString() + Math.random().toString(36).substring(2, 7);
    const newEntry: ChatEntry = {
      id: entryId,
      question: questionText,
      version: version,
      response: null,
      loading: true,
      error: null,
    };

    setEntries((prev) => [...prev, newEntry]);

    try {
      const response = await askQuestion(questionText, version);
      setEntries((prev) =>
        prev.map((e) =>
          e.id === entryId
            ? { ...e, response, loading: false, error: null }
            : e
        )
      );
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error ? err.message : 'Failed to consult documentation';
      setEntries((prev) =>
        prev.map((e) =>
          e.id === entryId
            ? { ...e, loading: false, error: errorMsg }
            : e
        )
      );
    }
  };

  // If a question was passed in from the landing page, show it and auto-call askQuestion on mount
  useEffect(() => {
    // Only proceed if we have a resolved version (activeVersion)
    if (!activeVersion) return;
    
    const query = searchParams.get('q');
    const versionParam = searchParams.get('v') || activeVersion;

    if (query && !initialTriggered.current) {
      initialTriggered.current = true;
      executeQuestion(query, versionParam);
    }
  }, [searchParams, activeVersion]);

  // When changing dropdown on an existing message, re-ask against the new version as a new entry
  const handleReaskVersion = (question: string, newVersion: string) => {
    executeQuestion(question, newVersion);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || !activeVersion) return;

    executeQuestion(trimmed, activeVersion);
    setInput('');
  };

  const isSubmitting = entries.some((e) => e.loading);

  return (
    <div className="flex h-screen flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
      <Navigation />

      {/* Subheader info bar */}
      <div className="shrink-0 border-b border-study-border/50 dark:border-study-border-dark/50 bg-[#F5EFE4]/60 dark:bg-[#1A1F1A]/60 px-4 sm:px-6 py-2">
        <div className="max-w-3xl mx-auto flex items-center justify-between text-[11px] font-mono text-study-text/60 dark:text-study-text-dark/60">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            <span>Consultation Thread</span>
          </span>
          <span className="hidden sm:inline">
            Active Scope: <strong className="text-accent">{activeVersion}</strong>
          </span>
        </div>
      </div>

      {/* Scrollable Message Thread Area (most recent at bottom) */}
      <main className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-5 sm:space-y-6 max-w-3xl mx-auto w-full">
        {entries.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center p-6 sm:p-8 space-y-4">
            <div className="h-12 w-12 rounded-full border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] flex items-center justify-center text-accent text-xl font-serif">
              §
            </div>
            <div className="max-w-md space-y-1">
              <h2 className="font-serif text-lg font-semibold text-primary dark:text-[#EDE7D9]">
                Version-Pinned Consultation Desk
              </h2>
              <p className="text-xs text-study-text/60 dark:text-study-text-dark/60 leading-relaxed font-sans">
                Each inquiry retains its own version context. Use the dropdown attached to any question to re-examine that same question against another version.
              </p>
            </div>
          </div>
        ) : (
          entries.map((entry) => (
            <ChatMessage
              key={entry.id}
              entry={entry}
              availableVersions={availableVersions}
              onReaskVersion={handleReaskVersion}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Fixed Bottom Input Bar with Responsive Version Selector */}
      <footer className="shrink-0 border-t border-study-border/70 dark:border-study-border-dark/70 bg-[#FAF6EE] dark:bg-[#161A16] p-3 sm:p-4">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className="archive-card rounded-xl p-2 sm:p-2.5 flex flex-col sm:flex-row items-stretch sm:items-center gap-2 shadow-xs focus-within:ring-2 focus-within:ring-accent/40 focus-within:border-accent"
          >
            <div className="flex items-center justify-between sm:justify-start gap-2 border-b sm:border-b-0 border-study-border/50 dark:border-study-border-dark/50 pb-1.5 sm:pb-0">
              <span className="text-[10px] font-mono uppercase text-study-text/50 dark:text-study-text-dark/50 sm:hidden">
                Target:
              </span>
              <VersionDropdown
                selectedVersion={activeVersion}
                onSelectVersion={setActiveVersion}
                availableVersions={availableVersions}
                disabled={isSubmitting}
              />
            </div>

            <div className="hidden sm:block h-4 w-px bg-study-border dark:bg-study-border-dark shrink-0" />

            <div className="flex items-center gap-2 flex-1">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Ask a question against ${activeVersion}...`}
                disabled={isSubmitting}
                className="flex-1 min-w-0 bg-transparent px-2 py-1.5 text-sm text-study-text dark:text-study-text-dark placeholder:text-study-text/40 dark:placeholder:text-study-text-dark/40 focus:outline-none font-sans"
              />

              <button
                type="submit"
                disabled={!input.trim() || isSubmitting || !activeVersion}
                className="rounded-lg bg-accent hover:bg-accent-hover text-[#161A16] px-3.5 sm:px-4 py-2 text-xs font-mono font-medium tracking-wide transition-all shadow-xs disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center gap-1.5 shrink-0"
              >
                <span>Ask</span>
                <span className="text-sm leading-none">&rarr;</span>
              </button>
            </div>
          </form>
        </div>
      </footer>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute allowedRoles={['admin', 'employee']}>
      <Suspense
        fallback={
          <div className="flex h-screen items-center justify-center bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark font-mono text-xs">
            Loading Reference Desk...
          </div>
        }
      >
        <ChatContent />
      </Suspense>
    </ProtectedRoute>
  );
}
