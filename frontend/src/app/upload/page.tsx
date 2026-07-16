"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Upload, File, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { useUploadBenchmark } from "@/hooks/useBenchmark";
import type { BenchmarkResponse } from "@/lib/api/types";

export default function UploadPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileInfo, setFileInfo] = useState<{
    name: string;
    size: string;
    pages: number | null;
  } | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedLibrary, setSelectedLibrary] = useState<string>("docling");
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkResponse | null>(null);
  
  // Use React Query mutation for upload
  const uploadMutation = useUploadBenchmark();

  const libraries = [
    {
      id: "pypdf",
      name: "PyPDF",
      description: "Pure Python PDF library",
    },
    {
      id: "pdfplumber",
      name: "PDFPlumber",
      description: "Text and table extraction",
    },
    {
      id: "pymupdf",
      name: "PyMuPDF",
      description: "Fast C-based library",
    },
    {
      id: "docling",
      name: "Docling",
      description: "Document understanding",
    },
    {
      id: "mineru",
      name: "MinerU",
      description: "Layout analysis + OCR",
    },
    {
      id: "unstructured",
      name: "Unstructured",
      description: "Element-based extraction",
    },
    {
      id: "opendataloader",
      name: "OpenDataLoader",
      description: "Unified data loading",
    },
  ];

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  const handleFileSelect = useCallback((file: File) => {
    if (file.type !== "application/pdf") {
      return;
    }

    setSelectedFile(file);
    setFileInfo({
      name: file.name,
      size: formatFileSize(file.size),
      pages: null,
    });
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        handleFileSelect(files[0]);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFileSelect(files[0]);
      }
    },
    [handleFileSelect]
  );

  const handleRunBenchmark = async () => {
    if (!selectedFile) {
      return;
    }

    uploadMutation.mutate(
      {
        file: selectedFile,
        library: selectedLibrary,
      },
      {
        onSuccess: (data) => {
          setBenchmarkResult(data);
          // Store in session storage for results page
          sessionStorage.setItem(`benchmark_${data.benchmark_id}`, JSON.stringify(data));
          // Redirect after success
          setTimeout(() => {
            router.push(`/results?id=${data.benchmark_id}`);
          }, 1500);
        },
      }
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            PDF Extraction Benchmark
          </h1>
          <p className="text-muted-foreground">
            Upload a PDF and select an extraction library to test
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-card rounded-lg border shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-4">Upload PDF</h2>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`
                  border-2 border-dashed rounded-lg p-8 md:p-12 text-center
                  transition-all duration-200 cursor-pointer
                  ${
                    isDragging
                      ? "border-primary bg-primary/5"
                      : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
                  }
                `}
              >
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileInputChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center gap-4"
                >
                  <div
                    className={`
                    w-16 h-16 rounded-full flex items-center justify-center
                    ${
                      isDragging
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }
                  `}
                  >
                    <Upload className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="text-lg font-medium mb-1">
                      {isDragging
                        ? "Drop your PDF here"
                        : "Drag & drop PDF file here"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      or click to browse
                    </p>
                  </div>
                </label>
              </div>

              {uploadMutation.isError && (
                <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
                  <p className="text-sm text-destructive">
                    {uploadMutation.error instanceof Error
                      ? uploadMutation.error.message
                      : "Failed to upload file. Please try again."}
                  </p>
                </div>
              )}
              
              {uploadMutation.isSuccess && benchmarkResult && (
                <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-green-500 font-medium mb-1">
                      Benchmark completed successfully!
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Redirecting to results...
                    </p>
                  </div>
                </div>
              )}
            </div>

            {fileInfo && (
              <div className="bg-card rounded-lg border shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-4">
                  File Information
                </h2>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
                    <File className="w-5 h-5 text-primary mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {fileInfo.name}
                      </p>
                      <div className="flex flex-wrap gap-4 mt-2 text-sm text-muted-foreground">
                        <span>Size: {fileInfo.size}</span>
                        {fileInfo.pages && <span>Pages: {fileInfo.pages}</span>}
                      </div>
                    </div>
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg border shadow-sm p-6 sticky top-4">
              <h2 className="text-xl font-semibold mb-4">
                Select Library
              </h2>
              <p className="text-sm text-muted-foreground mb-4">
                Choose which extraction library to benchmark
              </p>

              <div className="space-y-2 mb-6">
                {libraries.map((library) => (
                  <label
                    key={library.id}
                    className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all border-2 ${
                      selectedLibrary === library.id
                        ? "border-primary bg-primary/5"
                        : "border-transparent hover:bg-muted/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="library"
                      value={library.id}
                      checked={selectedLibrary === library.id}
                      onChange={(e) => setSelectedLibrary(e.target.value)}
                      className="mt-1 w-4 h-4 text-primary focus:ring-primary focus:ring-offset-0"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">{library.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {library.description}
                      </p>
                    </div>
                  </label>
                ))}
              </div>

              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-4">
                  Selected: <span className="font-medium">{libraries.find(l => l.id === selectedLibrary)?.name}</span>
                </p>
                <button
                  onClick={handleRunBenchmark}
                  disabled={!selectedFile || uploadMutation.isPending}
                  className={`
                    w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2
                    ${
                      !selectedFile || uploadMutation.isPending
                        ? "bg-muted text-muted-foreground cursor-not-allowed"
                        : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm hover:shadow"
                    }
                  `}
                >
                  {uploadMutation.isPending ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : uploadMutation.isSuccess ? (
                    <>
                      <CheckCircle2 className="w-5 h-5" />
                      Completed!
                    </>
                  ) : (
                    "Run Benchmark"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card rounded-lg border p-4">
            <h3 className="font-semibold text-sm mb-1">Real-Time Extraction</h3>
            <p className="text-xs text-muted-foreground">
              Upload PDF and get immediate results
            </p>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <h3 className="font-semibold text-sm mb-1">Performance Metrics</h3>
            <p className="text-xs text-muted-foreground">
              Track speed, memory usage, CPU, and extraction quality
            </p>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <h3 className="font-semibold text-sm mb-1">Comprehensive Results</h3>
            <p className="text-xs text-muted-foreground">
              View detailed extraction metrics and outputs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
