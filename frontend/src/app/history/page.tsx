"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  ArrowUpDown,
  Trash2,
  GitCompare,
  Download,
  Eye,
  Calendar,
  FileText,
  CheckCircle2,
  XCircle,
  Clock,
  Archive,
  Loader2,
} from "lucide-react";
import { useBenchmarkHistory, useDeleteHistory } from "@/hooks/useBenchmark";
import type { HistoryRecord } from "@/lib/api/types";

export default function HistoryPage() {
  const router = useRouter();

  // Real API hooks
  const {
    data: historyData,
    isLoading,
    error,
    refetch,
  } = useBenchmarkHistory();
  const deleteMutation = useDeleteHistory();

  const benchmarks: HistoryRecord[] = historyData?.history || [];

  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<
    "date" | "name" | "size" | "pages" | "time"
  >("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [selectedBenchmarks, setSelectedBenchmarks] = useState<string[]>([]);

  // Filter and sort benchmarks
  const filteredAndSortedBenchmarks = useMemo(() => {
    let filtered = benchmarks.filter(
      (b) =>
        b.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.runId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.selectedLibrary.toLowerCase().includes(searchQuery.toLowerCase()),
    );

    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case "date":
          comparison =
            new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case "name":
          comparison = a.filename.localeCompare(b.filename);
          break;
        case "size":
          comparison = a.outputSize - b.outputSize;
          break;
        case "pages":
          comparison = a.pageCount - b.pageCount;
          break;
        case "time":
          comparison = a.processingTime - b.processingTime;
          break;
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [benchmarks, searchQuery, sortBy, sortOrder]);

  const toggleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  const toggleBenchmarkSelection = (benchmarkId: string) => {
    setSelectedBenchmarks((prev) =>
      prev.includes(benchmarkId)
        ? prev.filter((id) => id !== benchmarkId)
        : [...prev, benchmarkId],
    );
  };

  const handleDelete = async (benchmarkId: string) => {
    if (confirm("Are you sure you want to delete this benchmark?")) {
      try {
        await deleteMutation.mutateAsync(benchmarkId);
        refetch();
      } catch (err) {
        console.error("Failed to delete benchmark:", err);
      }
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedBenchmarks.length === 0) return;
    if (confirm(`Delete ${selectedBenchmarks.length} selected benchmark(s)?`)) {
      try {
        await Promise.all(
          selectedBenchmarks.map((id) => deleteMutation.mutateAsync(id)),
        );
        setSelectedBenchmarks([]);
        refetch();
      } catch (err) {
        console.error("Failed to delete benchmarks:", err);
      }
    }
  };

  const handleCompare = () => {
    if (selectedBenchmarks.length < 2) {
      alert("Select at least 2 benchmarks to compare");
      return;
    }
    if (selectedBenchmarks.length > 4) {
      alert("You can compare up to 4 benchmarks at once");
      return;
    }
    // Use the first selected benchmark's benchmarkGroupId
    const firstSelected = benchmarks.find(
      (b) => b.runId === selectedBenchmarks[0],
    );
    if (firstSelected?.benchmarkGroupId) {
      router.push(`/compare/${firstSelected.benchmarkGroupId}`);
    }
  };

  const handleDownload = (benchmarkId: string, pdfName: string) => {
    // Navigate to the results page
    router.push(`/results/${benchmarkId}`);
  };

  const handleOpen = (benchmarkId: string) => {
    router.push(`/results/${benchmarkId}`);
  };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  const formatTime = (ms: number): string => {
    if (ms === 0) return "-";
    if (ms < 1000) return ms.toFixed(2) + " ms";
    return (ms / 1000).toFixed(2) + " s";
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading benchmark history...</p>
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
          <h2 className="text-xl font-bold mb-2">Failed to Load History</h2>
          <p className="text-muted-foreground">
            {error instanceof Error
              ? error.message
              : "An unexpected error occurred"}
          </p>
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
            <h1 className="text-3xl font-bold">Benchmark History</h1>
            <p className="text-muted-foreground mt-1">
              View and manage previous benchmark executions
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 bg-card border rounded-lg text-sm">
              <span className="font-semibold">
                {filteredAndSortedBenchmarks.length}
              </span>{" "}
              benchmarks
            </span>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Archive className="w-5 h-5 text-primary" />
              <h3 className="text-sm font-medium">Total Benchmarks</h3>
            </div>
            <p className="text-2xl font-bold">{benchmarks.length}</p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <h3 className="text-sm font-medium">Completed</h3>
            </div>
            <p className="text-2xl font-bold text-green-500">
              {benchmarks.filter((b) => b.status === "success").length}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <h3 className="text-sm font-medium">Has Failures</h3>
            </div>
            <p className="text-2xl font-bold text-red-500">
              {benchmarks.filter((b) => b.status === "failed").length}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <h3 className="text-sm font-medium">Total Time</h3>
            </div>
            <p className="text-2xl font-bold">
              {formatTime(
                benchmarks.reduce((sum, b) => sum + b.processingTime, 0),
              )}
            </p>
          </div>
        </div>

        {/* Search and Actions Bar */}
        <div className="bg-card rounded-lg border shadow-sm p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by PDF name, benchmark ID, or library..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Sort */}
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="px-4 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="date">Sort by Date</option>
                <option value="name">Sort by Name</option>
                <option value="size">Sort by Size</option>
                <option value="pages">Sort by Pages</option>
                <option value="time">Sort by Time</option>
              </select>
              <button
                onClick={() =>
                  setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                }
                className="px-3 py-2 border rounded-lg bg-background hover:bg-muted transition-colors"
                title={sortOrder === "asc" ? "Ascending" : "Descending"}
              >
                <ArrowUpDown className="w-4 h-4" />
              </button>
            </div>

            {/* Bulk Actions */}
            {selectedBenchmarks.length > 0 && (
              <div className="flex gap-2">
                <button
                  onClick={handleCompare}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
                >
                  <GitCompare className="w-4 h-4" />
                  Compare ({selectedBenchmarks.length})
                </button>
                <button
                  onClick={handleDeleteSelected}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Benchmarks List */}
        {filteredAndSortedBenchmarks.length === 0 ? (
          <div className="bg-card rounded-lg border shadow-sm p-12 text-center">
            <Archive className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No benchmarks found</h3>
            <p className="text-muted-foreground">
              {searchQuery
                ? "Try adjusting your search query"
                : "Start by uploading a PDF and running a benchmark"}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredAndSortedBenchmarks.map((benchmark) => (
              <div
                key={benchmark.runId}
                className="bg-card rounded-lg border shadow-sm hover:shadow-md transition-shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedBenchmarks.includes(benchmark.runId)}
                      onChange={() => toggleBenchmarkSelection(benchmark.runId)}
                      className="mt-1 w-4 h-4 rounded border-gray-300 focus:ring-2 focus:ring-primary"
                    />

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {/* Header Row */}
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="text-lg font-semibold truncate">
                              {benchmark.filename}
                            </h3>
                            {benchmark.status === "success" ? (
                              <span className="flex items-center gap-1 px-2 py-0.5 bg-green-500/10 text-green-500 rounded-full text-xs shrink-0">
                                <CheckCircle2 className="w-3 h-3" />
                                Completed
                              </span>
                            ) : benchmark.status === "failed" ? (
                              <span className="flex items-center gap-1 px-2 py-0.5 bg-red-500/10 text-red-500 rounded-full text-xs shrink-0">
                                <XCircle className="w-3 h-3" />
                                Failed
                              </span>
                            ) : (
                              <span className="flex items-center gap-1 px-2 py-0.5 bg-yellow-500/10 text-yellow-500 rounded-full text-xs shrink-0">
                                <XCircle className="w-3 h-3" />
                                Partial
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            ID: {benchmark.runId}
                          </p>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={() => handleOpen(benchmark.runId)}
                            className="p-2 hover:bg-muted rounded-lg transition-colors"
                            title="Open Results"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() =>
                              handleDownload(
                                benchmark.runId,
                                benchmark.filename,
                              )
                            }
                            className="p-2 hover:bg-muted rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(benchmark.runId)}
                            className="p-2 hover:bg-red-500/10 text-red-500 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Metadata Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-3">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Executed
                            </p>
                            <p className="text-sm font-medium">
                              {formatDate(benchmark.createdAt)}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Duration
                            </p>
                            <p className="text-sm font-medium">
                              {formatTime(benchmark.processingTime)}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Archive className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Library
                            </p>
                            <p className="text-sm font-medium">
                              {benchmark.selectedLibrary}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Pages
                            </p>
                            <p className="text-sm font-medium text-green-500">
                              {benchmark.pageCount}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-blue-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Memory
                            </p>
                            <p className="text-sm font-medium">
                              {benchmark.peakMemory.toFixed(1)} MB
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-purple-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Output Size
                            </p>
                            <p className="text-sm font-medium">
                              {formatBytes(benchmark.outputSize)}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
