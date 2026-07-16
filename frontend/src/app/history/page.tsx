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
  Filter,
  Archive,
} from "lucide-react";

interface BenchmarkMetadata {
  benchmarkId: string;
  pdfName: string;
  pdfSize: number;
  pdfPages: number;
  executedAt: string;
  libraries: string[];
  totalLibraries: number;
  successfulLibraries: number;
  failedLibraries: number;
  totalTime: number;
  status: "completed" | "failed" | "in-progress";
}

export default function HistoryPage() {
  const router = useRouter();

  // Mock data - Replace with actual API call to read benchmark.json and metadata.json
  const [benchmarks] = useState<BenchmarkMetadata[]>([
    {
      benchmarkId: "bench_2026_07_15_143022",
      pdfName: "annual-report-2025.pdf",
      pdfSize: 2457600,
      pdfPages: 45,
      executedAt: "2026-07-15T14:30:22Z",
      libraries: ["PyPDF", "PDFPlumber", "PyMuPDF", "Docling", "MinerU", "Unstructured"],
      totalLibraries: 6,
      successfulLibraries: 5,
      failedLibraries: 1,
      totalTime: 8234.56,
      status: "completed",
    },
    {
      benchmarkId: "bench_2026_07_14_093015",
      pdfName: "technical-manual.pdf",
      pdfSize: 5242880,
      pdfPages: 120,
      executedAt: "2026-07-14T09:30:15Z",
      libraries: ["PyPDF", "PDFPlumber", "PyMuPDF", "Docling", "MinerU", "Unstructured", "OpenDataLoader"],
      totalLibraries: 7,
      successfulLibraries: 7,
      failedLibraries: 0,
      totalTime: 15678.43,
      status: "completed",
    },
    {
      benchmarkId: "bench_2026_07_13_162045",
      pdfName: "research-paper.pdf",
      pdfSize: 1048576,
      pdfPages: 12,
      executedAt: "2026-07-13T16:20:45Z",
      libraries: ["Docling", "MinerU", "Unstructured"],
      totalLibraries: 3,
      successfulLibraries: 3,
      failedLibraries: 0,
      totalTime: 3456.78,
      status: "completed",
    },
    {
      benchmarkId: "bench_2026_07_12_110330",
      pdfName: "invoice-template.pdf",
      pdfSize: 524288,
      pdfPages: 2,
      executedAt: "2026-07-12T11:03:30Z",
      libraries: ["PyPDF", "PyMuPDF"],
      totalLibraries: 2,
      successfulLibraries: 2,
      failedLibraries: 0,
      totalTime: 567.89,
      status: "completed",
    },
    {
      benchmarkId: "bench_2026_07_11_154512",
      pdfName: "presentation-deck.pdf",
      pdfSize: 8388608,
      pdfPages: 75,
      executedAt: "2026-07-11T15:45:12Z",
      libraries: ["PyPDF", "PDFPlumber", "PyMuPDF", "Docling"],
      totalLibraries: 4,
      successfulLibraries: 2,
      failedLibraries: 2,
      totalTime: 9876.54,
      status: "completed",
    },
    {
      benchmarkId: "bench_2026_07_10_084020",
      pdfName: "legal-document.pdf",
      pdfSize: 3145728,
      pdfPages: 89,
      executedAt: "2026-07-10T08:40:20Z",
      libraries: ["Docling", "MinerU"],
      totalLibraries: 2,
      successfulLibraries: 0,
      failedLibraries: 2,
      totalTime: 0,
      status: "failed",
    },
  ]);

  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"date" | "name" | "size" | "pages" | "time">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [selectedBenchmarks, setSelectedBenchmarks] = useState<string[]>([]);

  // Filter and sort benchmarks
  const filteredAndSortedBenchmarks = useMemo(() => {
    let filtered = benchmarks.filter(
      (b) =>
        b.pdfName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.benchmarkId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.libraries.some((lib) => lib.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case "date":
          comparison = new Date(a.executedAt).getTime() - new Date(b.executedAt).getTime();
          break;
        case "name":
          comparison = a.pdfName.localeCompare(b.pdfName);
          break;
        case "size":
          comparison = a.pdfSize - b.pdfSize;
          break;
        case "pages":
          comparison = a.pdfPages - b.pdfPages;
          break;
        case "time":
          comparison = a.totalTime - b.totalTime;
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
        : [...prev, benchmarkId]
    );
  };

  const handleDelete = (benchmarkId: string) => {
    if (confirm("Are you sure you want to delete this benchmark?")) {
      // API call to delete benchmark
      console.log("Delete benchmark:", benchmarkId);
    }
  };

  const handleDeleteSelected = () => {
    if (selectedBenchmarks.length === 0) return;
    if (confirm(`Delete ${selectedBenchmarks.length} selected benchmark(s)?`)) {
      console.log("Delete benchmarks:", selectedBenchmarks);
      setSelectedBenchmarks([]);
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
    router.push(`/comparison?ids=${selectedBenchmarks.join(",")}`);
  };

  const handleDownload = (benchmarkId: string, pdfName: string) => {
    // API call to download benchmark results
    console.log("Download benchmark:", benchmarkId);
    alert(`Downloading results for ${pdfName}`);
  };

  const handleOpen = (benchmarkId: string) => {
    router.push(`/results?id=${benchmarkId}`);
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
              <span className="font-semibold">{filteredAndSortedBenchmarks.length}</span> benchmarks
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
              {benchmarks.filter((b) => b.status === "completed").length}
            </p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <h3 className="text-sm font-medium">Failed</h3>
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
              {formatTime(benchmarks.reduce((sum, b) => sum + b.totalTime, 0))}
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
                onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
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
                key={benchmark.benchmarkId}
                className="bg-card rounded-lg border shadow-sm hover:shadow-md transition-shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedBenchmarks.includes(benchmark.benchmarkId)}
                      onChange={() => toggleBenchmarkSelection(benchmark.benchmarkId)}
                      className="mt-1 w-4 h-4 rounded border-gray-300 focus:ring-2 focus:ring-primary"
                    />

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {/* Header Row */}
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="text-lg font-semibold truncate">{benchmark.pdfName}</h3>
                            {benchmark.status === "completed" ? (
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
                              <span className="flex items-center gap-1 px-2 py-0.5 bg-blue-500/10 text-blue-500 rounded-full text-xs shrink-0">
                                <Clock className="w-3 h-3" />
                                In Progress
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">ID: {benchmark.benchmarkId}</p>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={() => handleOpen(benchmark.benchmarkId)}
                            className="p-2 hover:bg-muted rounded-lg transition-colors"
                            title="Open Results"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDownload(benchmark.benchmarkId, benchmark.pdfName)}
                            className="p-2 hover:bg-muted rounded-lg transition-colors"
                            title="Download Results"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(benchmark.benchmarkId)}
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
                            <p className="text-xs text-muted-foreground">Executed</p>
                            <p className="text-sm font-medium">{formatDate(benchmark.executedAt)}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">Size</p>
                            <p className="text-sm font-medium">{formatBytes(benchmark.pdfSize)}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">Pages</p>
                            <p className="text-sm font-medium">{benchmark.pdfPages}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Archive className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-xs text-muted-foreground">Libraries</p>
                            <p className="text-sm font-medium">{benchmark.totalLibraries}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">Success</p>
                            <p className="text-sm font-medium text-green-500">
                              {benchmark.successfulLibraries}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-blue-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">Total Time</p>
                            <p className="text-sm font-medium">{formatTime(benchmark.totalTime)}</p>
                          </div>
                        </div>
                      </div>

                      {/* Libraries */}
                      <div>
                        <p className="text-xs text-muted-foreground mb-2">Libraries tested:</p>
                        <div className="flex flex-wrap gap-2">
                          {benchmark.libraries.map((lib) => (
                            <span
                              key={lib}
                              className="px-2 py-1 bg-muted/50 text-xs rounded border"
                            >
                              {lib}
                            </span>
                          ))}
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
