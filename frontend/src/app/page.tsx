import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-8">
        <h1 className="text-4xl font-bold text-center">
          PDF Extraction Benchmark
        </h1>
        
        <p className="text-center text-lg text-muted-foreground max-w-2xl">
          Benchmark and compare different PDF extraction methods to find the
          best solution for your needs.
        </p>

        <div className="flex gap-4 mt-8">
          <Link
            href="/upload"
            className="px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Upload & Benchmark
          </Link>
          <Link
            href="/results"
            className="px-6 py-3 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
          >
            View Results
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Upload PDFs</h3>
            <p className="text-sm text-muted-foreground">
              Upload your PDF documents to test different extraction methods.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Run Benchmarks</h3>
            <p className="text-sm text-muted-foreground">
              Compare performance, speed, and accuracy across multiple extraction tools.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Analyze Results</h3>
            <p className="text-sm text-muted-foreground">
              Visualize metrics with charts and detailed performance reports.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
