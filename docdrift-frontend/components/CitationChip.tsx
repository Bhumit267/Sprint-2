import React from 'react';
import { Citation } from '@/lib/types';

interface CitationChipProps {
  citation: Citation;
}

export const CitationChip: React.FC<CitationChipProps> = ({ citation }) => {
  return (
    <div
      title={`Source: ${citation.source_doc} (${citation.doc_type || 'doc'}) | Version: ${citation.version}${citation.section ? ` | Section: ${citation.section}` : ''}`}
      className="group inline-flex max-w-full items-center gap-1.5 rounded border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] px-2 py-0.5 text-xs font-mono text-study-text dark:text-study-text-dark transition-all duration-150 hover:border-accent hover:bg-[#F0E6D2] dark:hover:border-accent dark:hover:bg-[#232B23] hover:text-accent cursor-default shadow-xs"
    >
      <span className="text-[10px] text-accent font-bold uppercase tracking-wider shrink-0">
        Ref
      </span>
      <span className="font-semibold text-primary dark:text-[#E2D9C5] group-hover:text-accent transition-colors truncate max-w-[130px] sm:max-w-[220px]">
        {citation.source_doc}
      </span>
      <span className="rounded bg-[#EBE2D0] dark:bg-[#252D25] px-1 text-[10px] font-medium text-study-text/80 dark:text-study-text-dark/80 shrink-0">
        {citation.version}
      </span>
      {citation.section && (
        <span className="text-study-text/70 dark:text-study-text-dark/70 text-[11px] truncate max-w-[110px] sm:max-w-[180px]">
          &sect; {citation.section}
        </span>
      )}
    </div>
  );
};

export default CitationChip;
