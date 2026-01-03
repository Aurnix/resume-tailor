import { JobStatus } from '../types';

interface ProcessingViewProps {
  status: JobStatus | null;
}

const STEP_LABELS = [
  'Analyzing job description',
  'Parsing resume',
  'Matching experience to requirements',
  'Calculating fit score',
  'Tailoring resume content',
];

export function ProcessingView({ status }: ProcessingViewProps) {
  const currentStep = status?.current_step ?? 0;
  const progress = (currentStep / 5) * 100;

  return (
    <div className="text-center py-12">
      <div className="mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
          <svg
            className="w-8 h-8 text-blue-600 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Tailoring Your Resume
        </h2>
        <p className="text-gray-600">
          {status?.step_description || 'Starting...'}
        </p>
      </div>

      {/* Progress bar */}
      <div className="max-w-md mx-auto mb-8">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-sm text-gray-500 mt-2">
          Step {currentStep} of 5
        </p>
      </div>

      {/* Step list */}
      <div className="max-w-sm mx-auto text-left">
        {STEP_LABELS.map((label, index) => {
          const stepNum = index + 1;
          const isComplete = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <div
              key={index}
              className={`flex items-center py-2 ${
                isCurrent ? 'text-blue-600' : isComplete ? 'text-green-600' : 'text-gray-400'
              }`}
            >
              <span className="w-6 h-6 flex items-center justify-center mr-3">
                {isComplete ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : isCurrent ? (
                  <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
                ) : (
                  <span className="w-2 h-2 bg-current rounded-full opacity-50" />
                )}
              </span>
              <span className="text-sm">{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
