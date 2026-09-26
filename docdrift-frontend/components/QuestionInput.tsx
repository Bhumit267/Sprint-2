import React, { useState } from 'react';
import VersionDropdown from './VersionDropdown';

interface QuestionInputProps {
  onAsk: (question: string, version: string) => void;
  disabled?: boolean;
  defaultVersion?: string;
}

export const QuestionInput: React.FC<QuestionInputProps> = ({
  onAsk,
  disabled = false,
  defaultVersion = 'v3.0',
}) => {
  const [question, setQuestion] = useState('');
  const [version, setVersion] = useState(defaultVersion);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || disabled) return;
    onAsk(question.trim(), version);
    setQuestion('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="archive-card rounded-lg p-3 transition-shadow focus-within:shadow-md"
    >
      <div className="flex items-center justify-between border-b border-border/60 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-text/60">
            Inquiry Version Target
          </span>
        </div>
        <VersionDropdown
          selectedVersion={version}
          onSelectVersion={setVersion}
          disabled={disabled}
        />
      </div>

      <div className="flex items-center gap-2.5">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Consult the archive on APIs, breaking changes, migration steps..."
          disabled={disabled}
          className="flex-1 rounded bg-transparent px-3 py-2 text-sm text-text placeholder:text-text/40 focus:outline-none font-sans"
        />
        <button
          type="submit"
          disabled={disabled || !question.trim()}
          className="rounded bg-accent hover:bg-accent-hover text-[#161A16] font-medium px-4 py-2 text-xs font-mono tracking-wide transition-all shadow-xs hover:shadow focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          Consult Desk &rarr;
        </button>
      </div>
    </form>
  );
};

export default QuestionInput;
