export interface PDFDocument {
  id: string;
  filename: string;
  sizeBytes: number;
  uploadedAt: string;
  status: "uploaded" | "processing" | "completed" | "error";
}
