"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
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
  Eye,
  TrendingUp,
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

interface LibraryComparison {
  libraryName: string;
  status: "success" | "failed";
  time: number; // ms
  memory: number; // MB
  cpu: number; // %
  outputSize: number; // bytes
  markdownLength: number; // chars
  images: number;
  tables: number;
  ocr: boolean;
}

export default function ComparisonPage() {
  const searchParams = useSearchParams();
  const benchmarkId = searchParams.get("id");

  // Mock data - Replace with actual API call
  const [comparison] = useState<LibraryComparison[]>([
    {
      libraryName: "PyPDF",
      status: "success",
      time: 856.23,
      memory: 89.4,
      cpu: 28.5,
      outputSize: 12340,
      markdownLength: 11200,
      images: 0,
      tables: 0,
      ocr: false,
    },
    {
      libraryName: "PDFPlumber",
      status: "success",
      time: 1234.56,
      memory: 145.2,
      cpu: 42.8,
      outputSize: 18920,
      markdownLength: 16800,
      images: 0,
      tables: 3,
      ocr: false,
    },
    {
      libraryName: "PyMuPDF",
      status: "success",
      time: 654.32,
      memory: 78.6,
      cpu: 35.2,
      outputSize: 14560,
      markdownLength: 13400,
      images: 2,
      tables: 1,
      ocr: false,
    },
    {
      libraryName: "Docling",
      status: "success",
      time: 1234.56,
      memory: 128.5,
      cpu: 45.2,
      outputSize: 38870,
      markdownLength: 15420,
      images: 3,
      tables: 2,
      ocr: false,
    },
    {
      libraryName: "MinerU",
      status: "success",
      time: 2345.67,
      memory: 256.3,
      cpu: 68.4,
      outputSize: 45100,
      markdownLength: 16200,
      images: 4,
      tables: 3,
      ocr: true,
    },
    {
      libraryName: "Unstructured",
      status: "success",
      time: 1876.43,
      memory: 189.2,
      cpu: 52.1,
      outputSize: 46000,
      markdownLength: 14800,
      images: 2,
      tables: 2,
      ocr: false,
    },
    {
      libraryName: "OpenDataLoader",
      status: "failed",
      time: 0,
      memory: 0,
      cpu: 0,
      outputSize: 0,
      markdownLength: 0,
      images: 0,
      tables: 0,
      ocr: false,
    },
  ]);

  const successfulResults = comparison.filter((c) => c.status === "success");

  // Find winners
  const fastest = successfulResults.reduce((prev, current) =>
    current.time < prev.time ? current : prev
  );
  const leastMemory = successfulResults.reduce((prev, current) =>
    current.memory < prev.memory ? current : prev
  );
  const leastCPU = successfulResults.reduce((prev, current) =>
    current.cpu < prev.cpu ? current : prev
  );
  const largestOutput = successfulResults.reduce((prev, current) =>
    current.outputSize > prev.outputSize ? current : prev
  );

  const isWinner = (library: LibraryComparison, metric: string) => {
    if (library.status === "failed") return false;
    switch (metric) {
      case "time":
        return library.libraryName === fastest.libraryName;
      case "memory":
        return library.libraryName === leastMemory.libraryName;
      case "cpu":
        return library.libraryName === leastCPU.libraryName;
      case "output":
        return library.libraryName === largestOutput.libraryName;
      default:
        return false;
    }
  };

  const formatTime = (ms: number): string => {
    if (ms === 0) return "-";
    if (ms < 1000) return ms.toFixed(2) + " ms";
    return (ms / 1000).toFixed(2) + " s";
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "-";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  // Prepare chart data
  const chartData = successfulResults.map((lib) => ({
    name: lib.libraryName,
    time: parseFloat((lib.time / 1000).toFixed(2)),
    memory: parseFloat(lib.memory.toFixed(1)),
    cpu: parseFloat(lib.cpu.toFixed(1)),
    outputSize: parseFloat((lib.outputSize / 1024).toFixed(2)),
  }));

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Performance Comparison</h1>
          <p className="text-muted-foreground mt-1">
            Compare extraction libraries side-by-side • Benchmark ID: {benchmarkId || "unknown"}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              <h3 className="text-sm font-medium">Fastest</h3>
            </div>
            <p className="text-2xl font-bold">{fastest.libraryName}</p>
            <p className="text-sm text-muted-foreground">{formatTime(fastest.time)}</p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <MemoryStick className="w-5 h-5 text-orange-500" />
              <h3 className="text-sm font-medium">Least Memory</h3>
            </div>
            <p className="text-2xl font-bold">{leastMemory.libraryName}</p>
            <p className="text-sm text-muted-foreground">{leastMemory.memory.toFixed(1)} MB</p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-5 h-5 text-purple-500" />
              <h3 className="text-sm font-medium">Least CPU</h3>
            </div>
            <p className="text-2xl font-bold">{leastCPU.libraryName}</p>
            <p className="text-sm text-muted-foreground">{leastCPU.cpu.toFixed(1)}%</p>
          </div>

          <div className="bg-card rounded-lg border shadow-sm p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-5 h-5 text-green-500" />
              <h3 className="text-sm font-medium">Most Complete</h3>
            </div>
            <p className="text-2xl font-bold">{largestOutput.libraryName}</p>
            <p className="text-sm text-muted-foreground">{formatBytes(largestOutput.outputSize)}</p>
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
                  <th className="text-left p-4 font-medium">Time</th>
                  <th className="text-left p-4 font-medium">Memory</th>
                  <th className="text-left p-4 font-medium">CPU</th>
                  <th className="text-left p-4 font-medium">Output Size</th>
                  <th className="text-left p-4 font-medium">Markdown</th>
                  <th className="text-center p-4 font-medium">Images</th>
                  <th className="text-center p-4 font-medium">Tables</th>
                  <th className="text-center p-4 font-medium">OCR</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-center p-4 font-medium">Winner</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((lib) => (
                  <tr key={lib.libraryName} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="p-4 font-semibold">{lib.libraryName}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {isWinner(lib, "time") && <Trophy className="w-4 h-4 text-yellow-500" />}
                        {formatTime(lib.time)}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {isWinner(lib, "memory") && <Trophy className="w-4 h-4 text-yellow-500" />}
                        {lib.memory > 0 ? `${lib.memory.toFixed(1)} MB` : "-"}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {isWinner(lib, "cpu") && <Trophy className="w-4 h-4 text-yellow-500" />}
                        {lib.cpu > 0 ? `${lib.cpu.toFixed(1)}%` : "-"}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {isWinner(lib, "output") && <Trophy className="w-4 h-4 text-yellow-500" />}
                        {formatBytes(lib.outputSize)}
                      </div>
                    </td>
                    <td className="p-4 text-muted-foreground">
                      {lib.markdownLength > 0 ? lib.markdownLength.toLocaleString() + " chars" : "-"}
                    </td>
                    <td className="p-4 text-center">
                      {lib.images > 0 ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/10 text-blue-500 rounded-full text-xs">
                          <ImageIcon className="w-3 h-3" />
                          {lib.images}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="p-4 text-center">
                      {lib.tables > 0 ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-500 rounded-full text-xs">
                          <TableIcon className="w-3 h-3" />
                          {lib.tables}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="p-4 text-center">
                      {lib.ocr ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/10 text-purple-500 rounded-full text-xs">
                          <Eye className="w-3 h-3" />
                          Yes
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
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
                    <td className="p-4 text-center">
                      {(isWinner(lib, "time") ||
                        isWinner(lib, "memory") ||
                        isWinner(lib, "cpu") ||
                        isWinner(lib, "output")) && (
                        <div className="flex items-center justify-center gap-1">
                          <Trophy className="w-5 h-5 text-yellow-500" />
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Charts Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-primary" />
            <h2 className="text-2xl font-bold">Performance Charts</h2>
          </div>

          {/* Processing Time Chart */}
          <div className="bg-card rounded-lg border shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              Processing Time Comparison
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-sm" />
                <YAxis label={{ value: "Time (seconds)", angle: -90, position: "insideLeft" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="time" fill="hsl(217, 91%, 60%)" name="Processing Time (s)" />
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
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-sm" />
                <YAxis label={{ value: "Memory (MB)", angle: -90, position: "insideLeft" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="memory" fill="hsl(25, 95%, 53%)" name="Peak Memory (MB)" />
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
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-sm" />
                <YAxis label={{ value: "CPU (%)", angle: -90, position: "insideLeft" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="cpu" fill="hsl(280, 65%, 60%)" name="Average CPU (%)" />
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
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-sm" />
                <YAxis label={{ value: "Size (KB)", angle: -90, position: "insideLeft" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="outputSize" fill="hsl(142, 76%, 36%)" name="Output Size (KB)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
