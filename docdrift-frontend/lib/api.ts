/**
 * Centralized API client for communicating with the DocDrift FastAPI backend.
 * All fetch calls to the backend live here, nowhere else.
 */

import { AskResponse, Document, IngestResponse } from './types';

function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return url.replace(/\/+$/, '');
}

function getAuthHeaders(): Record<string, string> {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

export async function authLogin(email: string, password: string): Promise<any> {
  const endpoint = `${getApiBaseUrl()}/auth/login`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  return response.json();
}

export async function authSignup(organization_name: string, email: string, password: string): Promise<any> {
  const endpoint = `${getApiBaseUrl()}/auth/signup`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ organization_name, email, password }),
  });
  
  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || 'Signup failed');
  }
  return response.json();
}

export function authLogout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
}

/**
 * Sends a version-scoped question to the FastAPI backend.
 *
 * @param question - Developer question text
 * @param version - Product version to isolate retrieval to (e.g. 'v2.1', 'v3.0')
 * @returns Parsed JSON response containing answer, citations, and is_refusal
 * @throws Clear Error message on network or non-200 responses
 */
export async function askQuestion(question: string, version: string): Promise<AskResponse> {
  const endpoint = `${getApiBaseUrl()}/ask`;
  let response: Response;

  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ question, version }),
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(`Network failure connecting to DocDrift backend at ${endpoint}: ${errorMsg}`);
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Fallback to status text
    }
    throw new Error(`DocDrift API error (${response.status}): ${errorDetail}`);
  }

  return response.json();
}

/**
 * Retrieves the catalog of all indexed documents from the Chroma vector store.
 *
 * @returns Array of Document objects with source_doc, doc_type, and version
 * @throws Clear Error message on failure
 */
export async function getDocuments(): Promise<Document[]> {
  const endpoint = `${getApiBaseUrl()}/documents`;
  let response: Response;

  try {
    response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      cache: 'no-store',
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(`Network failure connecting to DocDrift backend at ${endpoint}: ${errorMsg}`);
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Fallback
    }
    throw new Error(`Failed to fetch documents (${response.status}): ${errorDetail}`);
  }

  return response.json();
}

/**
 * Retrieves the distinct list of versions available in the Chroma vector store for the user's organization.
 *
 * @returns Array of version strings
 * @throws Clear Error message on failure
 */
export async function getVersions(): Promise<string[]> {
  const endpoint = `${getApiBaseUrl()}/versions`;
  let response: Response;

  try {
    response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      cache: 'no-store',
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(`Network failure connecting to DocDrift backend at ${endpoint}: ${errorMsg}`);
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Fallback
    }
    throw new Error(`Failed to fetch versions (${response.status}): ${errorDetail}`);
  }

  return response.json();
}

/**
 * Dynamically fetches suggested questions generated by the LLM based on the org's documents.
 */
export async function getSuggestions(version?: string): Promise<{ text: string, version: string }[]> {
  const endpoint = `${getApiBaseUrl()}/suggestions${version ? `?version=${encodeURIComponent(version)}` : ''}`;
  
  const response = await fetch(endpoint, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch suggestions');
  }

  return response.json();
}

/**
 * Triggers re-ingestion and indexing of all raw markdown files in data/raw_docs/.
 */
export async function triggerIngestion(payload?: { version?: string, doc_type?: string, file?: File }): Promise<IngestResponse> {
  const endpoint = `${getApiBaseUrl()}/ingest`;
  let response: Response;

  try {
    const headers: Record<string, string> = {
      ...getAuthHeaders(),
    };

    let body: any = undefined;
    if (payload && payload.file) {
      // Use FormData if file is present
      const formData = new FormData();
      formData.append('file', payload.file);
      if (payload.version) formData.append('version', payload.version);
      if (payload.doc_type) formData.append('doc_type', payload.doc_type);
      body = formData;
    } else if (payload) {
      // Fallback to JSON if no file (legacy/testing)
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(payload);
    }

    response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body,
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(`Network failure connecting to DocDrift backend at ${endpoint}: ${errorMsg}`);
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Fallback
    }
    throw new Error(`Failed to trigger ingestion (${response.status}): ${errorDetail}`);
  }

  return response.json();
}

/**
 * Gets a signed download URL for a document.
 */
export async function getDocumentDownloadUrl(docId: string): Promise<string> {
  const endpoint = `${getApiBaseUrl()}/documents/${docId}/download`;
  const response = await fetch(endpoint, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch download link (${response.status})`);
  }
  
  const data = await response.json();
  return data.download_url;
}

/**
 * Gets the current authenticated user's profile.
 */
export async function getCurrentUser(): Promise<{ id: string; email: string; role: string; org_id: string | null; org_name: string | null } | null> {
  const endpoint = `${getApiBaseUrl()}/auth/me`;
  try {
    const response = await fetch(endpoint, {
      headers: getAuthHeaders(),
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    // Ignore network errors or unauthenticated
  }
  return null;
}

export async function getOrganizations(): Promise<any[]> {
  const endpoint = `${getApiBaseUrl()}/auth/organizations`;
  const response = await fetch(endpoint, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch organizations');
  return response.json();
}

export async function createOrganization(name: string): Promise<any> {
  const endpoint = `${getApiBaseUrl()}/auth/organization`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ name }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to create organization');
  }
  return response.json();
}

export async function getOrganizationUsers(orgId: string): Promise<any[]> {
  const endpoint = `${getApiBaseUrl()}/auth/organizations/${orgId}/users`;
  const response = await fetch(endpoint, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch users');
  return response.json();
}

export async function registerUser(email: string, password: string, role: string, orgId?: string): Promise<any> {
  const endpoint = `${getApiBaseUrl()}/auth/register`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ email, password, role, org_id: orgId }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to create user');
  }
  return response.json();
}
