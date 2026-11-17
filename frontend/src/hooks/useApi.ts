import { useState, useCallback } from 'react';
import type { AxiosResponse, AxiosError } from 'axios';

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: unknown[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFn: (...args: unknown[]) => Promise<AxiosResponse<T>>
): UseApiReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: unknown[]): Promise<T | null> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiFn(...args);
        setData(response.data);
        setLoading(false);
        return response.data;
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string; message?: string }>;
        const message =
          axiosError.response?.data?.detail ||
          axiosError.response?.data?.message ||
          axiosError.message ||
          'Something went wrong';
        setError(message);
        setLoading(false);
        return null;
      }
    },
    [apiFn]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, execute, reset };
}
