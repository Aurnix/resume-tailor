import { useState, useCallback, useRef } from 'react';
import { TailorRequest, JobStatus, AppState } from '../types';
import { startTailoring, getJobStatus } from '../api';

export function useTailoring() {
  const [appState, setAppState] = useState<AppState>('form');
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const pollJobStatus = useCallback((jobId: string) => {
    pollingRef.current = window.setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === 'completed') {
          stopPolling();
          setAppState('results');
        } else if (status.status === 'failed') {
          stopPolling();
          setError(status.error || 'An unknown error occurred');
          setAppState('form');
        }
      } catch (err) {
        stopPolling();
        setError(err instanceof Error ? err.message : 'Failed to check status');
        setAppState('form');
      }
    }, 1000);
  }, [stopPolling]);

  const submit = useCallback(async (request: TailorRequest) => {
    setError(null);
    setAppState('processing');

    try {
      const initialStatus = await startTailoring(request);
      setJobStatus(initialStatus);
      pollJobStatus(initialStatus.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start tailoring');
      setAppState('form');
    }
  }, [pollJobStatus]);

  const reset = useCallback(() => {
    stopPolling();
    setAppState('form');
    setJobStatus(null);
    setError(null);
  }, [stopPolling]);

  return {
    appState,
    jobStatus,
    error,
    submit,
    reset,
  };
}
