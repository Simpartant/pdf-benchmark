"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { POLLING_CONFIG } from "@/constants/config";

export interface UsePollingOptions<T> {
  interval?: number;
  enabled?: boolean;
  onData?: (data: T) => void;
  onError?: (error: Error) => void;
  shouldStopPolling?: (data: T) => boolean;
}

export interface UsePollingState<T> {
  data: T | null;
  isPolling: boolean;
  error: Error | null;
  startPolling: () => void;
  stopPolling: () => void;
}

/**
 * Custom hook for polling data at regular intervals
 * @param fetcher - Async function to fetch data
 * @param options - Polling configuration
 * @returns Polling state and control functions
 */
export function usePolling<T>(
  fetcher: () => Promise<T>,
  options: UsePollingOptions<T> = {}
): UsePollingState<T> {
  const {
    interval = POLLING_CONFIG.INTERVAL,
    enabled = false,
    onData,
    onError,
    shouldStopPolling,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isPolling, setIsPolling] = useState(enabled);
  const [error, setError] = useState<Error | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  const poll = useCallback(async () => {
    try {
      const result = await fetcher();

      if (isMountedRef.current) {
        setData(result);
        setError(null);
        onData?.(result);

        // Check if we should stop polling
        if (shouldStopPolling?.(result)) {
          setIsPolling(false);
        }
      }
    } catch (err) {
      if (isMountedRef.current) {
        const error = err instanceof Error ? err : new Error("Polling failed");
        setError(error);
        onError?.(error);
      }
    }
  }, [fetcher, onData, onError, shouldStopPolling]);

  const startPolling = useCallback(() => {
    setIsPolling(true);
  }, []);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  useEffect(() => {
    if (isPolling) {
      // Initial fetch
      poll();

      // Set up interval
      intervalRef.current = setInterval(poll, interval);
    } else {
      // Clear interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPolling, interval, poll]);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return {
    data,
    isPolling,
    error,
    startPolling,
    stopPolling,
  };
}
