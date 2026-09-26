'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { triggerIngestion } from '@/lib/api';

export default function AdminUploadPage() {
  const router = useRouter();
  const [docType, setDocType] = useState('api_reference');
  const [version, setVersion] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!version.trim()) {
      setError('Version is required');
      return;
    }
    if (!file) {
      setError('Please select a markdown file to upload');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      await triggerIngestion({ version: version.trim(), doc_type: docType, file });
      router.push('/documents');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <div className="min-h-screen flex flex-col bg-study-bg text-study-text dark:bg-study-bg-dark dark:text-study-text-dark paper-grain transition-colors">
        <Navigation />

        <main className="flex-1 p-4 sm:p-8 md:p-12 max-w-2xl mx-auto w-full space-y-6">
          <header className="border-b border-study-border/70 dark:border-study-border-dark/70 pb-5">
            <h1 className="font-serif text-2xl sm:text-3xl font-semibold text-primary dark:text-[#EDE7D9]">
              Upload Documentation
            </h1>
            <p className="text-xs text-study-text/60 dark:text-study-text-dark/60 font-mono mt-1">
              Add new documents to your organization's catalog
            </p>
          </header>

          <form onSubmit={handleSubmit} className="archive-card rounded-xl p-6 space-y-6">
            {error && (
              <div className="rounded border border-warning/40 bg-warning/5 p-3 text-xs font-mono text-warning">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-study-text/80 dark:text-study-text-dark/80 mb-2">
                  Document Type
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full rounded-lg border border-study-border dark:border-study-border-dark bg-transparent px-3 py-2 text-sm text-study-text dark:text-study-text-dark focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent font-sans"
                >
                  <option value="api_reference">API Reference</option>
                  <option value="migration_guide">Migration Guide</option>
                  <option value="changelog">Changelog</option>
                  <option value="general">General Documentation</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-study-text/80 dark:text-study-text-dark/80 mb-2">
                  Version <span className="text-warning">*</span>
                </label>
                <input
                  type="text"
                  value={version}
                  onChange={(e) => setVersion(e.target.value)}
                  placeholder="e.g. v1.0, 2024-Q3"
                  className="w-full rounded-lg border border-study-border dark:border-study-border-dark bg-transparent px-3 py-2 text-sm text-study-text dark:text-study-text-dark placeholder:text-study-text/40 dark:placeholder:text-study-text-dark/40 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent font-sans"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-study-text/80 dark:text-study-text-dark/80 mb-2">
                  File Upload <span className="text-warning">*</span>
                </label>
                <div className="rounded-lg border-2 border-dashed border-study-border/60 dark:border-study-border-dark/60 p-8 text-center bg-study-bg/50 dark:bg-study-bg-dark/50">
                  <span className="text-sm font-sans text-study-text/60 dark:text-study-text-dark/60 block mb-3">
                    {file ? file.name : 'Select a markdown file to upload'}
                  </span>
                  <input 
                    type="file" 
                    accept=".md,.mdx,.txt" 
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="mx-auto text-sm text-study-text/70 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accent/10 file:text-accent hover:file:bg-accent/20 cursor-pointer" 
                  />
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => router.back()}
                className="rounded-lg border border-study-border dark:border-study-border-dark px-4 py-2 text-xs font-mono text-study-text/80 dark:text-study-text-dark/80 hover:bg-study-border/10 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-accent hover:bg-accent-hover text-[#161A16] px-4 py-2 text-xs font-mono font-medium shadow-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Uploading...' : 'Upload & Ingest'}
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  );
}
