"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import {
  uploadAndBenchmark,
  checkHealth,
  getSystemInfo,
  getBenchmarkHistory,
  getBenchmarkResult,
  deleteHistoryRecord,
} from "@/lib/api/benchmark";
import type {
  UploadBenchmarkRequest,
  BenchmarkResponse,
  HistoryListResponse,
} from "@/lib/api/types";

/**
 * Hook for uploading PDF and running benchmark
 */
export function useUploadBenchmark() {
  return useMutation({
    mutationFn: (request: UploadBenchmarkRequest) =>
      uploadAndBenchmark(request),
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
    refetchInterval: 30000,
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
    refetchInterval: 5000,
    enabled: false,
  });
}

/**
 * Hook for fetching benchmark history list
 */
export function useBenchmarkHistory() {
  return useQuery({
    queryKey: ["benchmarkHistory"],
    queryFn: getBenchmarkHistory,
    refetchInterval: 10000,
  });
}

/**
 * Hook for fetching a single benchmark result by history ID
 */
export function useBenchmarkResult(historyId: string | null) {
  return useQuery({
    queryKey: ["benchmarkResult", historyId],
    queryFn: () => getBenchmarkResult(historyId!),
    enabled: !!historyId,
  });
}

/**
 * Hook for deleting a history record
 */
export function useDeleteHistory() {
  return useMutation({
    mutationFn: (historyId: string) => deleteHistoryRecord(historyId),
  });
}
