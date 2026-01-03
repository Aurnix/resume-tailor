import { TailorForm } from './components/TailorForm';
import { ProcessingView } from './components/ProcessingView';
import { ResultsView } from './components/ResultsView';
import { useTailoring } from './hooks/useTailoring';

function App() {
  const { appState, jobStatus, error, submit, reset } = useTailoring();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Resume Tailor
          </h1>
          <p className="text-gray-600 mt-1">
            AI-powered resume optimization for job applications
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {appState === 'form' && (
          <div className="bg-white rounded-lg shadow p-6">
            <TailorForm onSubmit={submit} error={error} />
          </div>
        )}

        {appState === 'processing' && (
          <div className="bg-white rounded-lg shadow p-6">
            <ProcessingView status={jobStatus} />
          </div>
        )}

        {appState === 'results' && jobStatus && (
          <ResultsView status={jobStatus} onReset={reset} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
          Resume Tailor helps you present your real experience in the language each employer is looking for.
        </div>
      </footer>
    </div>
  );
}

export default App;
