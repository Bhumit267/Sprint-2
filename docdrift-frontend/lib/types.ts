/**
 * Shared TypeScript types for DocDrift frontend.
 * Matches backend FastAPI response models and state representations.
 */

export type Citation = {
  source_doc: string;
  doc_type: string;
  version: string;
  section?: string;
};

export type AskResponse = {
  answer: string;
  citations: Citation[];
  is_refusal: boolean;
};

export type ChatEntry = {
  id: string;
  question: string;
  version: string;
  response: AskResponse | null;
  loading: boolean;
  error?: string | null;
};

export type Document = {
  id?: string;
  source_doc: string;
  doc_type: string;
  version: string;
  last_updated?: string;
};

export type IngestedDocument = Document;

export type IngestResponse = {
  status: string;
  documents_processed: number;
  indexed_chunks: number;
};
