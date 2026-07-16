"use client";

import { useState, useEffect } from "react";
import { ApiError } from "@/types";

export interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
  enabled?: boolean;
}

export interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for API calls with loading and error states
 * @param fetcher - Async function that fetches data
 * @param options - Configuration options
 * @returns API state and refetch function
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiState<T> {
  const { onSuccess, onError, enabled = true } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher();
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const apiError: ApiError = {
        message: err instanceof Error ? err.message : "An error occurred",
        status: (err as any).status,
      };
      setError(apiError);
      onError?.(apiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [enabled]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchData,
  };
}

/**
 * Custom hook for mutations (POST, PUT, DELETE)
 * @returns Mutation function and state
 */
export function useMutation<T, V = any>() {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const mutate = async (
    mutationFn: (variables: V) => Promise<T>,
    variables: V,
    options?: {
      onSuccess?: (data: T) => void;
      onError?: (error: ApiError) => void;
    }
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await mutationFn(variables);
      setData(result);
      options?.onSuccess?.(result);
      return result;
    } catch (err) {
      const apiError: ApiError = {
        message: err instanceof Error ? err.message : "An error occurred",
        status: (err as any).status,
      };
      setError(apiError);
      options?.onError?.(apiError);
      throw apiError;
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
    setIsLoading(false);
  };

  return {
    data,
    isLoading,
    error,
    mutate,
    reset,
  };
}
