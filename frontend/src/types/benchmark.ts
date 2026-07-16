export type ExtractionMethod = "pypdf" | "pdfplumber" | "pymupdf";

export interface BenchmarkConfig {
  pdfId: string;
  methods: ExtractionMethod[];
  options: BenchmarkOptions;
}

export interface BenchmarkOptions {
  extractImages: boolean;
  extractTables: boolean;
}

export interface BenchmarkStatus {
  benchmarkId: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  startedAt: string;
  completedAt?: string;
}
