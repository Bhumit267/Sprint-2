'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import VersionDropdown from '@/components/VersionDropdown';
import { getVersions, getSuggestions } from '@/lib/api';

export default function LandingPage() {
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const [version, setVersion] = useState('');
  const [availableVersions, setAvailableVersions] = React.useState<string[]>([]);
  const [suggestions, setSuggestions] = React.useState<{text: string, version: string}[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function loadVersions() {
      try {
        const versions = await getVersions();
        setAvailableVersions(versions);
        if (versions.length > 0) {
          setVersion(versions[0]);
        }
        
        try {
          const fetchedSuggestions = await getSuggestions(versions.length > 0 ? versions[0] : undefined);
          setSuggestions(fetchedSuggestions);
        } catch (err) {
          console.error('Failed to load dynamic suggestions', err);
        }
      } catch (err) {
        console.error('Failed to load versions', err);
      } finally {
        setLoading(false);
      }
    }
    loadVersions();
  }, []);

  const handleStart = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = question.trim();
    if (!query) {
      router.push('/chat');
      return;
    }
    router.push(`/chat?q=${encodeURIComponent(query)}&v=${encodeURIComponent(version)}`);
  };

  const handleSelectExample = (exampleText: string, exampleVersion: string) => {
    setQuestion(exampleText);
    setVersion(exampleVersion);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
      <Navigation />

      {/* Main Hero & Large Question Input */}
      <main className="max-w-2xl mx-auto w-full px-4 py-8 sm:py-16 md:py-20 space-y-6 sm:space-y-8 text-center">
        {/* App Title & One-line Description */}
        <div className="space-y-2.5 sm:space-y-3">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] px-3 py-0.5 text-[11px] font-mono text-primary dark:text-[#EDE7D9]">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            <span>Strict Version-Isolated RAG</span>
          </div>

          <h1 className="font-serif text-3xl sm:text-5xl md:text-6xl font-normal tracking-tight text-primary dark:text-[#EDE7D9] leading-tight">
            DocDrift
          </h1>
          <p className="text-sm sm:text-base md:text-lg text-study-text/75 dark:text-study-text-dark/75 max-w-xl mx-auto font-sans leading-relaxed px-2">
            Version-isolated developer documentation intelligence with exact source citations.
          </p>
        </div>

        {/* Large Centered Input Form */}
        {loading ? (
          <div className="archive-card rounded-xl p-8 text-center text-xs font-mono text-study-text/50">
            Loading available versions...
          </div>
        ) : availableVersions.length === 0 ? (
          <div className="archive-card rounded-xl p-8 text-center text-sm font-sans text-study-text/70 dark:text-study-text-dark/70 border border-warning/20 bg-warning/5">
            <p className="font-semibold text-warning mb-1">No versions available yet</p>
            <p>Ask your admin to upload documentation to start using the Reference Desk.</p>
          </div>
        ) : (
          <>
            <form
              onSubmit={handleStart}
              className="archive-card rounded-xl p-3 sm:p-4 text-left shadow-md transition-all focus-within:ring-2 focus-within:ring-accent/40 focus-within:border-accent"
            >
              <div className="flex items-center justify-between border-b border-study-border/60 dark:border-study-border-dark/60 pb-2.5 mb-2.5">
                <label
                  htmlFor="landing-question-input"
                  className="text-[11px] font-mono font-semibold uppercase tracking-wider text-study-text/60 dark:text-study-text-dark/60 flex items-center gap-2"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                  Target Version Scope
                </label>
                <VersionDropdown
                  selectedVersion={version}
                  onSelectVersion={setVersion}
                  availableVersions={availableVersions}
                />
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
                <input
                  id="landing-question-input"
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask any documentation question..."
                  className="flex-1 bg-transparent px-2 py-2 text-sm sm:text-base md:text-lg text-study-text dark:text-study-text-dark placeholder:text-study-text/35 dark:placeholder:text-study-text-dark/35 focus:outline-none font-sans"
                  autoFocus
                />

                <button
                  type="submit"
                  className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-accent hover:bg-accent-hover text-[#161A16] font-medium px-4 sm:px-5 py-2.5 text-xs sm:text-sm font-mono tracking-wide transition-all shadow-xs hover:shadow-md cursor-pointer shrink-0"
                >
                  <span>Start</span>
                  <span className="text-sm leading-none">&rarr;</span>
                </button>
              </div>
            </form>

            {/* Example Question Chips */}
            {suggestions.length > 0 && (
              <div className="space-y-2.5 pt-2">
                <div className="flex items-center justify-center gap-2 text-[11px] sm:text-xs font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                  </span>
                  AI Suggested Inquiries
                </div>
                <div className="flex flex-wrap justify-center gap-2">
                  {suggestions.map((sug, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleSelectExample(sug.text, sug.version)}
                      className="inline-flex items-center gap-1.5 sm:gap-2 rounded-lg border border-study-border dark:border-study-border-dark bg-[#FFFFFF] dark:bg-[#1A1F1A] px-2.5 sm:px-3 py-1.5 text-left text-xs font-mono text-study-text/80 dark:text-study-text-dark/80 hover:border-accent hover:text-accent dark:hover:border-accent dark:hover:text-accent transition-all cursor-pointer shadow-2xs group max-w-full"
                    >
                      <span className="break-words line-clamp-1">{sug.text}</span>
                      <span className="text-[10px] text-accent font-semibold rounded bg-accent/10 px-1 py-0.2 shrink-0">
                        {sug.version}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Subtle Footer */}
      <footer className="max-w-4xl mx-auto w-full px-4 py-4 sm:py-6 border-t border-study-border/60 dark:border-study-border-dark/60 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs font-mono text-study-text/50 dark:text-study-text-dark/50 text-center sm:text-left">
        <p>&copy; {new Date().getFullYear()} DocDrift Reference Desk &bull; Team GroundTruth</p>
        <p className="flex items-center justify-center gap-2">
          <span>Grounded Inquiries</span>
          <span>&bull;</span>
          <span>Zero Speculation</span>
        </p>
      </footer>
    </div>
  );
}
