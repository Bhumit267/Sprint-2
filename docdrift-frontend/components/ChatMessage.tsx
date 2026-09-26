import React from 'react';
import { ChatEntry } from '@/lib/types';
import VersionDropdown from './VersionDropdown';
import CitationChip from './CitationChip';

interface ChatMessageProps {
  entry: ChatEntry;
  availableVersions: string[];
  onReaskVersion?: (question: string, newVersion: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  entry,
  availableVersions,
  onReaskVersion,
}) => {
  return (
    <div className="flex flex-col space-y-2 w-full">
      {/* Question Container: Right-Aligned */}
      <div className="flex flex-col items-end max-w-full">
        {/* Version dropdown sits just above the question bubble */}
        <div className="flex items-center gap-1.5 mb-1 max-w-full flex-wrap justify-end">
          <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50 shrink-0">
            Scope:
          </span>
          <VersionDropdown
            selectedVersion={entry.version}
            availableVersions={availableVersions}
            onSelectVersion={(newVersion) => {
              if (newVersion !== entry.version && onReaskVersion) {
                onReaskVersion(entry.question, newVersion);
              }
            }}
            disabled={entry.loading}
          />
        </div>

        {/* Right-aligned Question Bubble */}
        <div className="max-w-[92%] sm:max-w-[80%] rounded-2xl rounded-tr-xs bg-primary text-[#FAF6EE] px-3.5 sm:px-4 py-2.5 sm:py-3 shadow-xs">
          <p className="text-xs sm:text-sm font-sans whitespace-pre-wrap leading-relaxed break-words">
            {entry.question}
          </p>
        </div>
      </div>

      {/* Answer Container: Left-Aligned */}
      {entry.loading && (
        <div className="flex justify-start pt-1">
          <div className="archive-card w-full max-w-[92%] sm:max-w-[80%] rounded-2xl rounded-tl-xs p-3.5 sm:p-4 space-y-3">
            <div className="flex items-center justify-between text-xs font-mono text-accent">
              <div className="flex items-center gap-2">
                <svg
                  className="animate-spin h-3.5 w-3.5 text-accent shrink-0"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span className="truncate">Consulting archive for {entry.version}...</span>
              </div>
              <span className="text-[10px] text-study-text/40 dark:text-study-text-dark/40 font-mono shrink-0 pl-1">
                {entry.version}
              </span>
            </div>

            {/* Skeleton loader bars */}
            <div className="space-y-2 pt-1 animate-pulse">
              <div className="h-3.5 bg-study-border/50 dark:bg-study-border-dark/50 rounded w-5/6" />
              <div className="h-3.5 bg-study-border/40 dark:bg-study-border-dark/40 rounded w-full" />
              <div className="h-3.5 bg-study-border/30 dark:bg-study-border-dark/30 rounded w-3/4" />
            </div>
          </div>
        </div>
      )}

      {/* Answer Once Arrived */}
      {!entry.loading && entry.response && (
        <div className="flex justify-start pt-1">
          <div className="archive-card max-w-[92%] sm:max-w-[80%] rounded-2xl rounded-tl-xs p-3.5 sm:p-4 text-xs sm:text-sm text-study-text dark:text-study-text-dark space-y-3">
            <div className="flex items-center justify-between border-b border-study-border/50 dark:border-study-border-dark/50 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50">
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                Response Grounded in Archive
              </span>
              <span className="rounded bg-accent/10 px-1.5 py-0.5 text-accent font-semibold shrink-0">
                {entry.version}
              </span>
            </div>

            <p className="whitespace-pre-wrap leading-relaxed font-sans break-words">
              {entry.response.answer}
            </p>

            {/* Citation Chips with responsive wrapping */}
            {entry.response.citations && entry.response.citations.length > 0 && (
              <div className="pt-2 border-t border-study-border/40 dark:border-study-border-dark/40 space-y-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50 block">
                  Verified Citations ({entry.response.citations.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {entry.response.citations.map((citation, i) => (
                    <CitationChip key={i} citation={citation} />
                  ))}
                </div>
              </div>
            )}

            {/* Refusal notification in muted brick red */}
            {entry.response.is_refusal && (
              <div className="flex items-start gap-2 rounded-lg border border-warning/40 bg-warning/5 dark:bg-warning/10 p-2.5 text-xs text-warning">
                <span className="font-serif font-bold text-sm leading-none mt-0.5">&sect;</span>
                <div className="font-sans leading-normal">
                  <span className="font-semibold">Grounding Notice:</span> Information not found in documentation for version {entry.version}. Refusing to speculate.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error state */}
      {!entry.loading && entry.error && (
        <div className="flex justify-start pt-1">
          <div className="rounded-2xl rounded-tl-xs border border-warning/40 bg-warning/5 dark:bg-warning/10 p-3 sm:p-4 text-xs font-mono text-warning max-w-[92%] sm:max-w-[80%] break-words">
            <strong>Inquiry Error ({entry.version}):</strong> {entry.error}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
