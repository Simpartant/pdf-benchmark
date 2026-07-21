"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  CheckCircle2,
  XCircle,
  Trophy,
  Clock,
  Cpu,
  MemoryStick,
  FileText,
  Image as ImageIcon,
  Table as TableIcon,
  Loader2,
  ArrowLeft,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import {
  getComparisonByGroupId,
  getBenchmarkResult,
} from "@/lib/api/benchmark";
import type { ExtractionResultResponse } from "@/lib/api/types";

interface LibraryComparison {
  runId: string;
  library: string;
  version: string;
  status: "success" | "failed";
  processingTimeSeconds: number;
  peakMemoryMb: number;
  averageCpuPercent: number;
  inputSizeBytes: number;
  outputSizeBytes: number;
  pageCount: number;
  tableCount: number;
  imageCount: number;
  markdownLength: number;
  jsonSizeBytes: number;
  warnings: string[];
  error?: string;
}

function extractToComparison(r: ExtractionResultResponse): LibraryComparison {
  return {
    runId: r.runId,
    library: r.library,
    version: r.libraryVersion,
    status: r.status === "success" ? "success" : "failed",
    processingTimeSeconds: r.processingTimeSeconds,
    peakMemoryMb: r.peakMemoryMb,
    averageCpuPercent: r.averageCpuPercent,
    inputSizeBytes: r.inputSizeBytes,
    outputSizeBytes: r.outputSizeBytes,
    pageCount: r.pageCount,
    tableCount: r.tableCount,
    imageCount: r.imageCount,
    markdownLength: r.markdownLength,
    jsonSizeBytes: r.jsonSizeBytes,
    warnings: r.warnings,
    error: r.error,
  };
}

export default function ComparisonPage() {
  const router = useRouter();
  const params = useParams();
  const benchmarkGroupId = params.benchmarkGroupId as string;

  // Fetch comparison data - use the benchmarkGroupId
  const {
    data: benchmarkData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["comparison", benchmarkGroupId],
    queryFn: () => getComparisonByGroupId(benchmarkGroupId!),
    enabled: !!benchmarkGroupId,
  });

  // Transform API data to comparison format
  const comparison: LibraryComparison[] = useMemo(() => {
    if (!benchmarkData?.extraction_results) return [];
    return benchmarkData.extraction_results.map(extractToComparison);
  }, [benchmarkData]);

  // Verify all runs share the same file hash
  const fileHashVerified = useMemo(() => {
    if (
      !benchmarkData?.extraction_results ||
      benchmarkData.extraction_results.length === 0
    ) {
      return true;
    }
    const hashes = benchmarkData.extraction_results.map((r) => r.fileHash);
    return new Set(hashes).size === 1;
  }, [benchmarkData]);

  const successfulResults = comparison.filter((c) => c.status === "success");

  // Find winners (only among successful results)
  // Lower is better for time, memory, CPU, and output size
  const fastest =
    successfulResults.length > 0
      ? successfulResults.reduce((prev, current) =>
          current.processingTimeSeconds < prev.processingTimeSeconds
            ? current
            : prev,
        )
      : null;
  const leastMemory =
    successfulResults.length > 0
      ? successfulResults.reduce((prev, current) =>
          current.peakMemoryMb < prev.peakMemoryMb ? current : prev,
        )
      : null;
  const leastCPU =
    successfulResults.length > 0
      ? successfulResults.reduce((prev, current) =>
          current.averageCpuPercent < prev.averageCpuPercent ? current : prev,
        )
      : null;
  const smallestOutput =
    successfulResults.length > 0
      ? successfulResults.reduce((prev, current) =>
          current.outputSizeBytes < prev.outputSizeBytes ? current : prev,
        )
      : null;

  const isWinner = (lib: LibraryComparison, metric: string) => {
    if (lib.status === "failed") return false;
    switch (metric) {
      case "time":
        return fastest ? lib.runId === fastest.runId : false;
      case "memory":
        return leastMemory ? lib.runId === leastMemory.runId : false;
      case "cpu":
        return leastCPU ? lib.runId === leastCPU.runId : false;
      case "output":
        return smallestOutput ? lib.runId === smallestOutput.runId : false;
      default:
        return false;
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds === 0) return "-";
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)} ms`;
    return `${seconds.toFixed(2)} s`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "-";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  // Prepare chart data
  const chartData = successfulResults.map((lib) => ({
    name: lib.library,
    time: parseFloat(lib.processingTimeSeconds.toFixed(2)),
    memory: parseFloat(lib.peakMemoryMb.toFixed(1)),
    cpu: parseFloat(lib.averageCpuPercent.toFixed(1)),
    outputSize: parseFloat((lib.outputSizeBytes / 1024).toFixed(2)),
  }));

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading benchmark results...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8 flex items-center justify-center">
        <div className="bg-card rounded-lg border shadow-sm p-8 max-w-md text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Failed to Load Results</h2>
          <p className="text-muted-foreground mb-4">
            {error instanceof Error
              ? error.message
              : "An unexpected error occurred"}
          </p>
          <p className="text-sm text-muted-foreground">
            Benchmark Group ID: {benchmarkGroupId || "unknown"}
          </p>
        </div>
      </div>
    );
  }

  // Empty state - no results
  if (comparison.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8 flex items-center justify-center">
        <div className="bg-card rounded-lg border shadow-sm p-8 max-w-md text-center">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">No Results Found</h2>
          <p className="text-muted-foreground">
            No benchmark data found for the provided group ID.
          </p>
        </div>
      </div>
    );
  }

  // Partial success state
  if (comparison.length > 0 && successfulResults.length < comparison.length) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="mb-8">
            <button
              onClick={() => router.push("/upload")}
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Upload
            </button>
            <h1 className="text-3xl font-bold">Performance Comparison</h1>
            <p className="text-muted-foreground mt-1">
              {successfulResults.length} of {comparison.length} libraries
              succeeded
            </p>
          </div>

          {/* Comparison Table */}
          <div className="bg-card rounded-lg border shadow-sm overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Detailed Comparison</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50 border-b">
                  <tr>
                    <th className="text-left p-4 font-medium">Library</th>
                    <th className="text-left p-4 font-medium">Version</th>
                    <th className="text-left p-4 font-medium">Time</th>
                    <th className="text-left p-4 font-medium">Memory</th>
                    <th className="text-left p-4 font-medium">CPU</th>
                    <th className="text-left p-4 font-medium">Output Size</th>
                    <th className="text-left p-4 font-medium">Pages</th>
                    <th className="text-left p-4 font-medium">Tables</th>
                    <th className="text-left p-4 font-medium">Images</th>
                    <th className="text-left p-4 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.map((lib) => (
                    <tr
                      key={lib.runId}
                      className="border-b hover:bg-muted/30 transition-colors"
                    >
                      <td className="p-4 font-semibold">{lib.library}</td>
                      <td className="p-4 text-sm">{lib.version}</td>
                      <td className="p-4">
                        {lib.status === "success"
                          ? formatTime(lib.processingTimeSeconds)
                          : "-"}
                      </td>
                      <td className="p-4">
                        {lib.status === "success"
                          ? `${lib.peakMemoryMb.toFixed(1)} MB`
                          : "-"}
                      </td>
                      <td className="p-4">
                        {lib.status === "success"
                          ? `${lib.averageCpuPercent.toFixed(1)}%`
                          : "-"}
                      </td>
                      <td className="p-4">
                        {lib.status === "success"
                          ? formatBytes(lib.outputSizeBytes)
                          : "-"}
                      </td>
                      <td className="p-4">{lib.pageCount}</td>
                      <td className="p-4">{lib.tableCount}</td>
                      <td className="p-4">{lib.imageCount}</td>
                      <td className="p-4">
                        {lib.status === "success" ? (
                          <span className="flex items-center gap-1 text-green-500">
                            <CheckCircle2 className="w-4 h-4" />
                            Success
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-500">
                            <XCircle className="w-4 h-4" />
                            Failed
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <button
            onClick={() => router.push("/upload")}
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Upload
          </button>
          <h1 className="text-3xl font-bold">Performance Comparison</h1>
          <p className="text-muted-foreground mt-1">
            Compare extraction libraries side-by-side • {comparison.length}{" "}
            run(s)
          </p>
          {!fileHashVerified && (
            <p className="text-sm text-red-500 mt-2">
              Warning: Not all runs share the same input file hash
            </p>
          )}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              <h3 className="text-sm font-medium">Fastest</h3>
            </div>
            <p className="text-2xl font-bold">
              {fastest ? fastest.library : "N/A"}
            </p>
            <p className="text-sm text-muted-foreground">
              {fastest ? formatTime(fastest.processingTimeSeconds) : "-"}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <MemoryStick className="w-5 h-5 text-orange-500" />
              <h3 className="text-sm font-medium">Least Memory</h3>
            </div>
            <p className="text-2xl font-bold">
              {leastMemory ? leastMemory.library : "N/A"}
            </p>
            <p className="text-sm text-muted-foreground">
              {leastMemory ? leastMemory.peakMemoryMb.toFixed(1) + " MB" : "-"}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-5 h-5 text-purple-500" />
              <h3 className="text-sm font-medium">Least CPU</h3>
            </div>
            <p className="text-2xl font-bold">
              {leastCPU ? leastCPU.library : "N/A"}
            </p>
            <p className="text-sm text-muted-foreground">
              {leastCPU ? leastCPU.averageCpuPercent.toFixed(1) + "%" : "-"}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-5 h-5 text-green-500" />
              <h3 className="text-sm font-medium">Smallest Output</h3>
            </div>
            <p className="text-2xl font-bold">
              {smallestOutput ? smallestOutput.library : "N/A"}
            </p>
            <p className="text-sm text-muted-foreground">
              {smallestOutput
                ? formatBytes(smallestOutput.outputSizeBytes)
                : "-"}
            </p>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="bg-card rounded-lg border shadow-sm overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Detailed Comparison</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <th className="text-left p-4 font-medium">Library</th>
                  <th className="text-left p-4 font-medium">Version</th>
                  <th className="text-left p-4 font-medium">Time</th>
                  <th className="text-left p-4 font-medium">Memory</th>
                  <th className="text-left p-4 font-medium">CPU</th>
                  <th className="text-left p-4 font-medium">Output Size</th>
                  <th className="text-left p-4 font-medium">Pages</th>
                  <th className="text-left p-4 font-medium">Tables</th>
                  <th className="text-left p-4 font-medium">Images</th>
                  <th className="text-left p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((lib) => (
                  <tr
                    key={lib.runId}
                    className="border-b hover:bg-muted/30 transition-colors"
                  >
                    <td className="p-4 font-semibold">{lib.library}</td>
                    <td className="p-4 text-sm">{lib.version}</td>
                    <td className="p-4">
                      {isWinner(lib, "time") && (
                        <Trophy className="w-4 h-4 text-yellow-500 inline mr-1" />
                      )}
                      {formatTime(lib.processingTimeSeconds)}
                    </td>
                    <td className="p-4">
                      {isWinner(lib, "memory") && (
                        <Trophy className="w-4 h-4 text-yellow-500 inline mr-1" />
                      )}
                      {lib.peakMemoryMb.toFixed(1)} MB
                    </td>
                    <td className="p-4">
                      {isWinner(lib, "cpu") && (
                        <Trophy className="w-4 h-4 text-yellow-500 inline mr-1" />
                      )}
                      {lib.averageCpuPercent.toFixed(1)}%
                    </td>
                    <td className="p-4">
                      {isWinner(lib, "output") && (
                        <Trophy className="w-4 h-4 text-yellow-500 inline mr-1" />
                      )}
                      {formatBytes(lib.outputSizeBytes)}
                    </td>
                    <td className="p-4">{lib.pageCount}</td>
                    <td className="p-4">{lib.tableCount}</td>
                    <td className="p-4">{lib.imageCount}</td>
                    <td className="p-4">
                      {lib.status === "success" ? (
                        <span className="flex items-center gap-1 text-green-500">
                          <CheckCircle2 className="w-4 h-4" />
                          Success
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-500">
                          <XCircle className="w-4 h-4" />
                          Failed
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Charts Section */}
        {chartData.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Performance Charts</h2>

            {/* Processing Time Chart */}
            <div className="bg-card rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-500" />
                Processing Time Comparison
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                  />
                  <XAxis dataKey="name" className="text-sm" />
                  <YAxis
                    label={{
                      value: "Time (seconds)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="time"
                    fill="hsl(217, 91%, 60%)"
                    name="Processing Time (s)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Memory Usage Chart */}
            <div className="bg-card rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <MemoryStick className="w-5 h-5 text-orange-500" />
                Memory Usage Comparison
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                  />
                  <XAxis dataKey="name" className="text-sm" />
                  <YAxis
                    label={{
                      value: "Memory (MB)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="memory"
                    fill="hsl(25, 95%, 53%)"
                    name="Peak Memory (MB)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* CPU Usage Chart */}
            <div className="bg-card rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-500" />
                CPU Usage Comparison
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                  />
                  <XAxis dataKey="name" className="text-sm" />
                  <YAxis
                    label={{
                      value: "CPU (%)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="cpu"
                    fill="hsl(280, 65%, 60%)"
                    name="Average CPU (%)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Output Size Chart */}
            <div className="bg-card rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-green-500" />
                Output Size Comparison
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                  />
                  <XAxis dataKey="name" className="text-sm" />
                  <YAxis
                    label={{
                      value: "Size (KB)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="outputSize"
                    fill="hsl(142, 76%, 36%)"
                    name="Output Size (KB)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
