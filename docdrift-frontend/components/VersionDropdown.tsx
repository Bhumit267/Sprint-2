import React from 'react';

interface VersionDropdownProps {
  selectedVersion: string;
  onSelectVersion: (version: string) => void;
  availableVersions?: string[];
  disabled?: boolean;
  className?: string;
}

export const VersionDropdown: React.FC<VersionDropdownProps> = ({
  selectedVersion,
  onSelectVersion,
  availableVersions = [],
  disabled = false,
  className = '',
}) => {
  // If list is empty while loading, display at least selectedVersion
  const versions =
    availableVersions && availableVersions.length > 0
      ? availableVersions
      : [selectedVersion];

  return (
    <div className={`relative inline-flex items-center ${className}`}>
      <label htmlFor={`version-select-${selectedVersion}`} className="sr-only">
        Version selector
      </label>
      <select
        id={`version-select-${selectedVersion}`}
        value={selectedVersion}
        onChange={(e) => onSelectVersion(e.target.value)}
        disabled={disabled}
        aria-label="Select target documentation version"
        className="appearance-none rounded-md border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] pl-2 pr-6 py-0.5 text-[11px] font-mono font-semibold tracking-tight text-primary dark:text-[#EDE7D9] transition-all hover:border-accent dark:hover:border-accent focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer shadow-2xs"
      >
        {versions.map((v) => (
          <option
            key={v}
            value={v}
            className="bg-[#FAF6EE] text-[#1C2B24] dark:bg-[#161A16] dark:text-[#EDE7D9]"
          >
            {v}
          </option>
        ))}
      </select>
      <span className="pointer-events-none absolute right-1.5 flex items-center text-accent text-[9px]">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-3 w-3"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </span>
    </div>
  );
};

export default VersionDropdown;
