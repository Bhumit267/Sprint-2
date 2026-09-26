'use client';

import React, { useEffect, useState, useMemo } from 'react';
import Navigation from '@/components/Navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Document } from '@/lib/types';
import { getDocuments, getDocumentDownloadUrl } from '@/lib/api';
import Link from 'next/link';

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedVersion, setSelectedVersion] = useState('all');

  useEffect(() => {
    async function loadDocs() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDocuments();
        setDocs(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to retrieve documents');
      } finally {
        setLoading(false);
      }
    }

    loadDocs();
  }, []);

  // Compute unique types and versions for filter dropdowns
  const availableTypes = useMemo(() => {
    const types = Array.from(new Set(docs.map((d) => d.doc_type))).filter(Boolean);
    return types.sort();
  }, [docs]);

  const availableVersions = useMemo(() => {
    const versions = Array.from(new Set(docs.map((d) => d.version))).filter(Boolean);
    return versions.sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
  }, [docs]);

  // Filter documents by search query, doc type, and version
  const filteredDocs = useMemo(() => {
    return docs.filter((doc) => {
      const matchesSearch =
        searchQuery.trim() === '' ||
        doc.source_doc.toLowerCase().includes(searchQuery.toLowerCase().trim());
      const matchesType = selectedType === 'all' || doc.doc_type === selectedType;
      const matchesVersion = selectedVersion === 'all' || doc.version === selectedVersion;

      return matchesSearch && matchesType && matchesVersion;
    });
  }, [docs, searchQuery, selectedType, selectedVersion]);

  const hasAnyFilter = searchQuery.trim() !== '' || selectedType !== 'all' || selectedVersion !== 'all';

  return (
    <ProtectedRoute allowedRoles={['admin', 'employee']}>
      <div className="min-h-screen flex flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
        <Navigation />

      <main className="flex-1 p-4 sm:p-8 md:p-12 max-w-5xl mx-auto w-full space-y-6">
        {/* Header Bar */}
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-study-border/70 dark:border-study-border-dark/70 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-accent font-semibold">
                Holdings &amp; Catalog
              </span>
            </div>
            <h1 className="font-serif text-2xl sm:text-3xl font-semibold text-primary dark:text-[#EDE7D9]">
              Document Library
            </h1>
            <p className="text-xs text-study-text/60 dark:text-study-text-dark/60 font-mono mt-1">
              Indexed documentation files tracked in the vector archive
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Upload Button */}
            <Link
              href="/admin/upload"
              className="rounded-lg border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] px-3.5 py-1.5 text-xs font-mono text-primary dark:text-[#EDE7D9] hover:border-accent focus:border-accent cursor-pointer flex items-center gap-1.5 shadow-2xs transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-3.5 w-3.5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Upload document</span>
            </Link>
          </div>
        </header>

        {/* Filters and Search Bar */}
        <section className="archive-card rounded-xl p-4 space-y-3">
          <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter by document name (e.g. api_reference.md)..."
                className="w-full rounded-lg border border-study-border dark:border-study-border-dark bg-transparent px-3 py-1.5 text-xs sm:text-sm text-study-text dark:text-study-text-dark placeholder:text-study-text/40 dark:placeholder:text-study-text-dark/40 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent font-sans"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs font-mono text-study-text/40 hover:text-accent cursor-pointer"
                >
                  &times;
                </button>
              )}
            </div>

            <div className="flex items-center gap-2">
              {/* Doc Type Dropdown */}
              <div className="flex items-center gap-1.5 flex-1 sm:flex-initial">
                <label
                  htmlFor="doc-type-filter"
                  className="text-[11px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50 hidden lg:inline"
                >
                  Type:
                </label>
                <select
                  id="doc-type-filter"
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full sm:w-auto appearance-none rounded-lg border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] px-2.5 py-1.5 text-xs font-mono text-primary dark:text-[#EDE7D9] hover:border-accent focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent cursor-pointer"
                >
                  <option value="all">All Types ({docs.length})</option>
                  {availableTypes.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              {/* Version Dropdown */}
              <div className="flex items-center gap-1.5 flex-1 sm:flex-initial">
                <label
                  htmlFor="doc-version-filter"
                  className="text-[11px] font-mono uppercase tracking-wider text-study-text/50 dark:text-study-text-dark/50 hidden lg:inline"
                >
                  Version:
                </label>
                <select
                  id="doc-version-filter"
                  value={selectedVersion}
                  onChange={(e) => setSelectedVersion(e.target.value)}
                  className="w-full sm:w-auto appearance-none rounded-lg border border-study-border dark:border-study-border-dark bg-[#F5EFE4] dark:bg-[#1A1F1A] px-2.5 py-1.5 text-xs font-mono text-primary dark:text-[#EDE7D9] hover:border-accent focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent cursor-pointer"
                >
                  <option value="all">All Versions</option>
                  {availableVersions.map((v) => (
                    <option key={v} value={v}>
                      {v}
                    </option>
                  ))}
                </select>
              </div>

              {/* Reset Filters button */}
              {hasAnyFilter && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedType('all');
                    setSelectedVersion('all');
                  }}
                  className="text-xs font-mono text-accent hover:underline cursor-pointer shrink-0 px-1"
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          {/* Result summary indicator */}
          <div className="flex items-center justify-between text-[11px] font-mono text-study-text/50 dark:text-study-text-dark/50 pt-1 border-t border-study-border/40 dark:border-study-border-dark/40">
            <span>
              Showing {filteredDocs.length} of {docs.length} cataloged documents
            </span>
            {hasAnyFilter && <span className="text-accent">Filter active</span>}
          </div>
        </section>

        {/* Error Notification */}
        {error && (
          <div className="rounded-xl border border-warning/40 bg-warning/5 p-4 text-xs font-mono text-warning">
            <strong>Archive Access Failure:</strong> {error}
          </div>
        )}

        {/* Document Table */}
        {loading ? (
          <div className="archive-card rounded-xl p-12 text-center text-xs font-mono text-study-text/50 dark:text-study-text-dark/50 space-y-2">
            <span className="inline-block h-2 w-2 rounded-full bg-accent animate-ping" />
            <p>Retrieving documents from archive vector store...</p>
          </div>
        ) : (
          <div className="archive-card rounded-xl overflow-hidden shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm min-w-[540px]">
                <thead className="border-b border-study-border/70 dark:border-study-border-dark/70 bg-[#F5EFE4] dark:bg-[#151915] text-[11px] font-mono uppercase tracking-wider text-study-text/60 dark:text-study-text-dark/60">
                  <tr>
                    <th className="px-4 sm:px-5 py-3.5">Document Name</th>
                    <th className="px-4 sm:px-5 py-3.5">Doc Type</th>
                    <th className="px-4 sm:px-5 py-3.5">Version</th>
                    <th className="px-4 sm:px-5 py-3.5">Last Updated</th>
                    <th className="px-4 sm:px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-study-border/40 dark:divide-study-border-dark/40">
                  {filteredDocs.length === 0 ? (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-5 py-8 text-center text-xs text-study-text/50 dark:text-study-text-dark/50 font-mono"
                      >
                        {docs.length === 0
                          ? 'No documents currently indexed in backend store.'
                          : 'No documents match the active filter criteria.'}
                      </td>
                    </tr>
                  ) : (
                    filteredDocs.map((doc, idx) => (
                      <tr
                        key={`${doc.source_doc}-${doc.version}-${idx}`}
                        className="hover:bg-[#F9F5EC] dark:hover:bg-[#1F261F] transition-colors"
                      >
                        {/* Document Name */}
                        <td className="px-4 sm:px-5 py-3.5 font-mono text-xs font-semibold text-primary dark:text-[#EDE7D9]">
                          <div className="flex items-center gap-2">
                            <span className="text-accent/80 text-xs">📄</span>
                            <span className="break-all">{doc.source_doc}</span>
                          </div>
                        </td>

                        {/* Doc Type */}
                        <td className="px-4 sm:px-5 py-3.5 text-xs">
                          <span className="rounded bg-study-border/30 dark:bg-study-border-dark/40 px-2 py-0.5 font-mono text-[11px] text-study-text/80 dark:text-study-text-dark/80 whitespace-nowrap">
                            {doc.doc_type}
                          </span>
                        </td>

                        {/* Version */}
                        <td className="px-4 sm:px-5 py-3.5 font-mono text-xs font-bold text-accent whitespace-nowrap">
                          <span className="rounded bg-accent/10 px-1.5 py-0.5">
                            {doc.version}
                          </span>
                        </td>

                        {/* Last Updated */}
                        <td className="px-4 sm:px-5 py-3.5 font-mono text-[11px] text-study-text/50 dark:text-study-text-dark/50 whitespace-nowrap">
                          {doc.last_updated || '—'}
                        </td>

                        {/* Actions */}
                        <td className="px-4 sm:px-5 py-3.5 text-right">
                          {doc.id ? (
                            <button
                              type="button"
                              onClick={async () => {
                                try {
                                  const url = await getDocumentDownloadUrl(doc.id!);
                                  window.open(url, '_blank');
                                } catch (e) {
                                  alert('Failed to get download link');
                                }
                              }}
                              className="text-xs font-mono text-accent hover:underline cursor-pointer px-2 py-1 rounded hover:bg-accent/10 transition-colors"
                            >
                              Download
                            </button>
                          ) : (
                            <span className="text-[10px] text-study-text/40">Legacy</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
    </ProtectedRoute>
  );
}
