export interface BenchmarkResult {
  benchmarkId: string;
  pdfFilename: string;
  methods: MethodResult[];
  summary: ResultSummary;
  createdAt: string;
}

export interface MethodResult {
  method: string;
  executionTimeMs: number;
  memoryUsageMb: number;
  textExtractedLength: number;
  success: boolean;
  error: string | null;
}

export interface ResultSummary {
  fastestMethod: string;
  mostEfficientMemory: string;
  totalDurationMs: number;
}
