"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Loader2,
  CheckCircle2,
  Clock,
  Cpu,
  MemoryStick,
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface BenchmarkProgress {
  benchmarkId: string;
  status: "pending" | "processing" | "completed" | "failed";
  currentLibrary: string | null;
  completedLibraries: string[];
  totalLibraries: number;
  elapsedTime: number; // seconds
  currentMetrics: {
    cpu: number;
    memory: number;
    page: number | null;
  };
  logs: Array<{
    timestamp: string;
    level: "info" | "success" | "warning" | "error";
    message: string;
    library?: string;
  }>;
}

export default function ProcessingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const benchmarkId = searchParams.get("id");

  const [progress, setProgress] = useState<BenchmarkProgress>({
    benchmarkId: benchmarkId || "unknown",
    status: "processing",
    currentLibrary: "docling",
    completedLibraries: [],
    totalLibraries: 4,
    elapsedTime: 0,
    currentMetrics: {
      cpu: 0,
      memory: 0,
      page: null,
    },
    logs: [],
  });

  const [isLogsExpanded, setIsLogsExpanded] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  // Simulate progress - Replace with actual API polling
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        // Simulate completion
        if (prev.completedLibraries.length === prev.totalLibraries) {
          clearInterval(interval);
          setTimeout(() => {
            router.push(`/results?id=${benchmarkId}`);
          }, 2000);
          return { ...prev, status: "completed", currentLibrary: null };
        }

        // Simulate progress
        const libraries = ["docling", "mineru", "unstructured"];
        const currentIndex = prev.completedLibraries.length;
        const shouldComplete = Math.random() > 0.7 && prev.elapsedTime > 3;

        const newLogs = [...prev.logs];
        if (shouldComplete && currentIndex < libraries.length) {
          newLogs.push({
            timestamp: new Date().toISOString(),
            level: "success",
            message: `Completed extraction with ${prev.currentLibrary}`,
            library: prev.currentLibrary || undefined,
          });
        } else if (prev.elapsedTime % 5 === 0) {
          newLogs.push({
            timestamp: new Date().toISOString(),
            level: "info",
            message: `Processing page ${prev.currentMetrics.page || 1} with ${prev.currentLibrary}`,
            library: prev.currentLibrary || undefined,
          });
        }

        return {
          ...prev,
          completedLibraries: shouldComplete
            ? [...prev.completedLibraries, prev.currentLibrary!]
            : prev.completedLibraries,
          currentLibrary: shouldComplete
            ? libraries[currentIndex + 1] || null
            : prev.currentLibrary,
          elapsedTime: prev.elapsedTime + 1,
          currentMetrics: {
            cpu: Math.min(95, 20 + Math.random() * 60),
            memory: Math.min(500, 100 + Math.random() * 200),
            page: prev.currentMetrics.page
              ? prev.currentMetrics.page + (Math.random() > 0.7 ? 1 : 0)
              : 1,
          },
          logs: newLogs.slice(-20), // Keep last 20 logs
        };
      });
    }, 1000);

    // Initial load complete
    setTimeout(() => setIsLoading(false), 500);

    return () => clearInterval(interval);
  }, [benchmarkId, router]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const progressPercentage =
    (progress.completedLibraries.length / progress.totalLibraries) * 100;

  const getLogColor = (level: string) => {
    switch (level) {
      case "success":
        return "text-green-500";
      case "warning":
        return "text-yellow-500";
      case "error":
        return "text-red-500";
      default:
        return "text-muted-foreground";
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="h-10 bg-muted animate-pulse rounded-lg w-64" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-card rounded-lg border p-6">
                <div className="h-4 bg-muted animate-pulse rounded w-24 mb-3" />
                <div className="h-8 bg-muted animate-pulse rounded w-16" />
              </div>
            ))}
          </div>
          <div className="bg-card rounded-lg border p-6">
            <div className="h-6 bg-muted animate-pulse rounded w-32 mb-4" />
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-4 bg-muted animate-pulse rounded" />
              ))}
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Processing Benchmark</h1>
            <p className="text-muted-foreground mt-1">
              Benchmark ID: {progress.benchmarkId}
            </p>
          </div>
          {progress.status === "completed" && (
            <div className="flex items-center gap-2 text-green-500">
              <CheckCircle2 className="w-6 h-6" />
              <span className="font-semibold">Completed</span>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="bg-card rounded-lg border shadow-sm p-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {progress.status === "completed" ? (
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              ) : (
                <Loader2 className="w-5 h-5 animate-spin text-primary" />
              )}
              <span className="font-semibold">
                {progress.status === "completed"
                  ? "All Extractions Complete"
                  : `Processing: ${progress.currentLibrary}`}
              </span>
            </div>
            <span className="text-sm text-muted-foreground">
              {progress.completedLibraries.length} / {progress.totalLibraries}{" "}
              libraries
            </span>
          </div>

          {/* Progress Bar */}
          <div className="relative h-3 bg-muted rounded-full overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-primary/80 transition-all duration-500 ease-out rounded-full"
              style={{ width: `${progressPercentage}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
            </div>
          </div>

          {/* Completed Libraries */}
          {progress.completedLibraries.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {progress.completedLibraries.map((lib) => (
                <span
                  key={lib}
                  className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm flex items-center gap-1"
                >
                  <CheckCircle2 className="w-3 h-3" />
                  {lib}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Elapsed Time */}
          <div className="bg-card rounded-lg border shadow-sm p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Elapsed Time</p>
                <p className="text-2xl font-bold">
                  {formatTime(progress.elapsedTime)}
                </p>
              </div>
            </div>
          </div>

          {/* CPU Usage */}
          <div className="bg-card rounded-lg border shadow-sm p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-purple-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">CPU Usage</p>
                <p className="text-2xl font-bold">
                  {progress.currentMetrics.cpu.toFixed(1)}%
                </p>
              </div>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 transition-all duration-300"
                style={{ width: `${progress.currentMetrics.cpu}%` }}
              />
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-card rounded-lg border shadow-sm p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                <MemoryStick className="w-5 h-5 text-orange-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Memory</p>
                <p className="text-2xl font-bold">
                  {progress.currentMetrics.memory.toFixed(0)} MB
                </p>
              </div>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500 transition-all duration-300"
                style={{
                  width: `${(progress.currentMetrics.memory / 512) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Current Page */}
          <div className="bg-card rounded-lg border shadow-sm p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <FileText className="w-5 h-5 text-green-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Current Page</p>
                <p className="text-2xl font-bold">
                  {progress.currentMetrics.page || "-"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Live Logs */}
        <div className="bg-card rounded-lg border shadow-sm">
          <button
            onClick={() => setIsLogsExpanded(!isLogsExpanded)}
            className="w-full p-6 flex items-center justify-between hover:bg-muted/50 transition-colors"
          >
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Live Logs
              <span className="text-sm text-muted-foreground font-normal">
                ({progress.logs.length})
              </span>
            </h2>
            {isLogsExpanded ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </button>

          {isLogsExpanded && (
            <div className="border-t">
              <div className="p-6 max-h-96 overflow-y-auto">
                {progress.logs.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No logs yet...
                  </p>
                ) : (
                  <div className="space-y-2 font-mono text-sm">
                    {progress.logs.map((log, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-2 rounded hover:bg-muted/50 transition-colors"
                      >
                        <span className="text-muted-foreground text-xs mt-0.5 w-20 flex-shrink-0">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                        <span className={`${getLogColor(log.level)} mt-0.5`}>
                          {log.level === "success" && "✓"}
                          {log.level === "error" && "✗"}
                          {log.level === "warning" && "⚠"}
                          {log.level === "info" && "ℹ"}
                        </span>
                        <span className="flex-1">{log.message}</span>
                        {log.library && (
                          <span className="text-xs bg-muted px-2 py-0.5 rounded text-muted-foreground">
                            {log.library}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-blue-500">
              Processing in Progress
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              This page will automatically redirect to results when all
              extractions are complete. You can safely close this page - the
              benchmark will continue in the background.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
