import { useState } from 'react';
import { TailorRequest } from '../types';

interface TailorFormProps {
  onSubmit: (request: TailorRequest) => void;
  error: string | null;
}

export function TailorForm({ onSubmit, error }: TailorFormProps) {
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!resumeText.trim() || !jobDescription.trim()) {
      return;
    }

    onSubmit({
      resume_text: resumeText,
      job_description: jobDescription,
      company_name: companyName || undefined,
    });
  };

  const isValid = resumeText.trim() && jobDescription.trim();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-2">
          Your Resume (Markdown format)
        </label>
        <textarea
          id="resume"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste your master resume here in Markdown format..."
          className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
          required
        />
      </div>

      <div>
        <label htmlFor="job" className="block text-sm font-medium text-gray-700 mb-2">
          Job Description (URL or paste text)
        </label>
        <textarea
          id="job"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste a job posting URL (e.g., https://jobs.lever.co/...) or paste the full job description text..."
          className="w-full h-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
          required
        />
      </div>

      <div>
        <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
          Company Name (optional - auto-extracted if not provided)
        </label>
        <input
          type="text"
          id="company"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., Acme Corp"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={!isValid}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
      >
        Tailor My Resume
      </button>
    </form>
  );
}
