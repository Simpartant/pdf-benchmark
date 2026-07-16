// Comprehensive TypeScript type definitions for the PDF Extraction Benchmark application

// ============================================================================
// Library Types
// ============================================================================

export interface Library {
  id: string;
  name: string;
  displayName: string;
  module: string;
  description: string;
  version?: string;
  status: "available" | "unavailable" | "unknown";
  capabilities: LibraryCapabilities;
  performanceNotes?: string;
}

export interface LibraryCapabilities {
  extractText: boolean;
  extractImages: boolean;
  extractTables: boolean;
  ocr: boolean;
  layoutAnalysis: boolean;
  metadata: boolean;
}

// ============================================================================
// Benchmark Types
// ============================================================================

export interface BenchmarkRequest {
  pdfPath: string;
  libraries: string[];
  options?: BenchmarkOptions;
}

export interface BenchmarkOptions {
  extractImages?: boolean;
  extractTables?: boolean;
  generateReport?: boolean;
}

export interface BenchmarkResponse {
  benchmarkId: string;
  status: BenchmarkStatus;
  message: string;
  startedAt: string;
}

export type BenchmarkStatus = "pending" | "running" | "completed" | "failed";

export interface BenchmarkProgress {
  benchmarkId: string;
  status: BenchmarkStatus;
  currentLibrary: string | null;
  completedLibraries: string[];
  totalLibraries: number;
  elapsedTime: number;
  currentMetrics?: CurrentMetrics;
  logs: LogEntry[];
}

export interface CurrentMetrics {
  cpu: number;
  memory: number;
  page: number;
}

export interface LogEntry {
  timestamp: string;
  level: "info" | "warning" | "error";
  message: string;
}

// ============================================================================
// Results Types
// ============================================================================

export interface BenchmarkResult {
  benchmarkId: string;
  pdfName: string;
  pdfSize: number;
  pdfPages: number;
  executedAt: string;
  totalTime: number;
  status: BenchmarkStatus;
  libraries: LibraryResult[];
}

export interface LibraryResult {
  libraryName: string;
  status: "success" | "failed";
  executionTimeMs: number;
  memoryUsageMb: number;
  cpuUsagePercent: number;
  outputSize: OutputSize;
  outputs: ExtractionOutputs;
  error?: string;
}

export interface OutputSize {
  markdown: number;
  json: number;
  images: number;
  tables: number;
}

export interface ExtractionOutputs {
  markdown: string;
  json: Record<string, any>;
  images: string[];
  tables: TableOutput[];
  metadata: Record<string, any>;
}

export interface TableOutput {
  name: string;
  content: string;
}

// ============================================================================
// Comparison Types
// ============================================================================

export interface LibraryComparison {
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

export interface ComparisonWinners {
  fastest: string;
  leastMemory: string;
  leastCpu: string;
  mostComplete: string;
}

// ============================================================================
// History Types
// ============================================================================

export interface BenchmarkMetadata {
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

export interface BenchmarkHistory {
  benchmarks: BenchmarkMetadata[];
  total: number;
  page: number;
  pageSize: number;
}

// ============================================================================
// Upload Types
// ============================================================================

export interface UploadResponse {
  success: boolean;
  fileId: string;
  fileName: string;
  fileSize: number;
  message: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
}

// ============================================================================
// Chart Types
// ============================================================================

export interface ChartDataPoint {
  name: string;
  time?: number;
  memory?: number;
  cpu?: number;
  outputSize?: number;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  error?: ApiError | null;
}

export type TabType = "markdown" | "json" | "images" | "tables" | "metadata";

export type SortField = "date" | "name" | "size" | "pages" | "time";
export type SortOrder = "asc" | "desc";
