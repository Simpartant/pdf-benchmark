"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { uploadAndBenchmark, checkHealth, getSystemInfo } from "@/lib/api/benchmark";
import type { UploadBenchmarkRequest } from "@/lib/api/types";

/**
 * Hook for uploading PDF and running benchmark
 */
export function useUploadBenchmark() {
  return useMutation({
    mutationFn: (request: UploadBenchmarkRequest) => uploadAndBenchmark(request),
    retry: false,
  });
}

/**
 * Hook for checking API health
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: checkHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 3,
  });
}

/**
 * Hook for getting system info
 */
export function useSystemInfo() {
  return useQuery({
    queryKey: ["systemInfo"],
    queryFn: getSystemInfo,
    refetchInterval: 5000, // Refresh every 5 seconds
    enabled: false, // Only fetch when explicitly enabled
  });
}
