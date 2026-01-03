import { JobStatus } from '../types';
import { getDownloadUrl } from '../api';

interface ResultsViewProps {
  status: JobStatus;
  onReset: () => void;
}

export function ResultsView({ status, onReset }: ResultsViewProps) {
  const result = status.result;

  if (!result) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">No results available</p>
        <button
          onClick={onReset}
          className="mt-4 text-blue-600 hover:underline"
        >
          Start Over
        </button>
      </div>
    );
  }

  const scorePercent = Math.round(result.fit_score * 100);
  const scoreColor =
    scorePercent >= 70
      ? 'text-green-600'
      : scorePercent >= 50
      ? 'text-yellow-600'
      : 'text-red-600';

  return (
    <div className="space-y-8">
      {/* Header with score */}
      <div className="text-center bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {result.job_title} at {result.company}
        </h2>
        <div className="mt-4">
          <span className={`text-6xl font-bold ${scoreColor}`}>
            {scorePercent}%
          </span>
          <p className="text-gray-600 mt-2">Match Score</p>
        </div>
        <div className="mt-4 text-sm text-gray-500">
          {result.keywords_matched} of {result.keywords_total} keywords matched
          {' | '}
          {result.bullets_rewritten} bullets rewritten
        </div>
      </div>

      {/* Download button */}
      {result.docx_filename && (
        <div className="text-center">
          <a
            href={getDownloadUrl(result.docx_filename)}
            download
            className="inline-flex items-center bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 font-medium transition-colors"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Download Tailored Resume
          </a>
        </div>
      )}

      {/* Tailored summary */}
      {result.tailored_summary && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Tailored Summary</h3>
          <p className="text-gray-700">{result.tailored_summary}</p>
        </div>
      )}

      {/* Two column layout for strengths and gaps */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Strengths */}
        {result.strengths.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-green-700 mb-3 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Strengths
            </h3>
            <ul className="space-y-2">
              {result.strengths.map((strength, i) => (
                <li key={i} className="text-gray-700 text-sm">
                  {strength}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Gaps */}
        {result.gaps.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-amber-700 mb-3 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              Gaps to Address
            </h3>
            <ul className="space-y-2">
              {result.gaps.map((gap, i) => (
                <li key={i} className="text-gray-700 text-sm">
                  {gap}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Talking points */}
      {result.talking_points.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-blue-700 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
                clipRule="evenodd"
              />
            </svg>
            Interview Talking Points
          </h3>
          <ul className="space-y-2">
            {result.talking_points.map((point, i) => (
              <li key={i} className="text-gray-700 text-sm flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Keywords added */}
      {result.keywords_added.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Keywords Added</h3>
          <div className="flex flex-wrap gap-2">
            {result.keywords_added.map((keyword, i) => (
              <span
                key={i}
                className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Start over button */}
      <div className="text-center pt-4">
        <button
          onClick={onReset}
          className="text-blue-600 hover:underline font-medium"
        >
          Tailor Another Resume
        </button>
      </div>
    </div>
  );
}
