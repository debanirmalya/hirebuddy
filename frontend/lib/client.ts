import { API_BASE_URL } from '@/lib/config';
import type { Candidate, CandidateProfileData } from '@/lib/types';

export async function listCandidates(page: number, pageSize: number = 10, signal?: AbortSignal,) {
  const url = `${API_BASE_URL}/candidates?page=${page}&per_page=${pageSize}`;
  console.log("Fetching:", url);

  try {
    const res = await fetch(url, { signal, cache: "no-store" });
    const text = await res.text();
    console.log("Raw response:", res.status, text);

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(`Invalid JSON: ${text}`);
    }

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${data?.message || text}`);
    }

    console.log("Parsed data:", data);

    return {
      candidates: (data.candidates || []).map((c: any) => ({
        id: c.id,
        name: c.name,
        email: c.email,
        company: c.curr_company,
        extractionStatus: c.status,
        updatedAt: c.updated_at,
      })),
      pagination: data.pagination,
    };
  } catch (err) {
    console.error("❌ listCandidates failed:", err);
    throw err;
  }
}



export async function getCandidate(id: string, signal?: AbortSignal): Promise<CandidateProfileData> {
  const res = await fetch(`${API_BASE_URL}/candidates/${id}`, { signal, cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch candidate');
  return res.json();
}

export async function uploadResume(
  file: File,
  fields: { name: string; email: string; curr_company: string }
): Promise<{ data: any }> {
  const form = new FormData();
  form.append("file", file);
  form.append("name", fields.name);
  form.append("email", fields.email);
  form.append("curr_company", fields.curr_company);

  const res = await fetch(`${API_BASE_URL}/candidates/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Upload failed: ${errorText}`);
  }

  return res.json();
}


export async function requestDocuments(candidateId: string): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/candidates/${candidateId}/request-documents`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}


export async function submitDocuments(
  candidateId: string,
  files: File[],
  types: string[]
): Promise<{ message: string; uploaded: any[]; status: string }> {
  if (files.length !== types.length) {
    throw new Error("Files and types count mismatch");
  }

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  types.forEach((t) => formData.append("types", t));

  const res = await fetch(`${API_BASE_URL}/candidates/${candidateId}/submit-documents`, {
    method: "POST",
    body: formData,
  });

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Invalid JSON from server: ${text}`);
  }

  if (!res.ok) {
    throw new Error(`Upload failed: ${data?.message || text}`);
  }

  return data;
}
