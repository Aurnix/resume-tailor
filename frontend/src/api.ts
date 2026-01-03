import { TailorRequest, JobStatus } from './types';

const API_BASE = '/api';

export async function startTailoring(request: TailorRequest): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/tailor`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to start tailoring: ${response.statusText}`);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error(`Failed to get job status: ${response.statusText}`);
  }

  return response.json();
}

export function getDownloadUrl(filename: string): string {
  return `${API_BASE}/download/${filename}`;
}

export async function checkHealth(): Promise<{ status: string; api_key_configured: boolean }> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
