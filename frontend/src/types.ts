export interface TailorRequest {
  resume_text: string;
  job_description: string;
  company_name?: string;
  notes?: string;
}

export interface JobResult {
  fit_score: number;
  keywords_matched: number;
  keywords_total: number;
  gaps: string[];
  strengths: string[];
  talking_points: string[];
  seniority_fit: string;
  job_title: string;
  company: string;
  docx_filename: string | null;
  tailored_summary: string;
  bullets_rewritten: number;
  keywords_added: string[];
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  current_step: number;
  total_steps: number;
  step_description: string;
  result: JobResult | null;
  error: string | null;
}

export type AppState = 'form' | 'processing' | 'results';
