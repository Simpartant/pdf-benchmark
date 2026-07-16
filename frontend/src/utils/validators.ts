// Input validation utilities

import { UPLOAD_CONFIG } from "@/constants/config";

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validate PDF file
 * @param file - File to validate
 * @returns Validation result
 */
export function validatePdfFile(file: File): ValidationResult {
  // Check file type
  if (!UPLOAD_CONFIG.ALLOWED_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: "Invalid file type. Please upload a PDF file.",
    };
  }

  // Check file extension
  const extension = `.${file.name.split(".").pop()?.toLowerCase()}`;
  if (!UPLOAD_CONFIG.ALLOWED_EXTENSIONS.includes(extension)) {
    return {
      valid: false,
      error: "Invalid file extension. Only .pdf files are allowed.",
    };
  }

  // Check file size
  if (file.size > UPLOAD_CONFIG.MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File size exceeds ${UPLOAD_CONFIG.MAX_FILE_SIZE / (1024 * 1024)}MB limit.`,
    };
  }

  // Check file is not empty
  if (file.size === 0) {
    return {
      valid: false,
      error: "File is empty. Please upload a valid PDF file.",
    };
  }

  return { valid: true };
}

/**
 * Validate benchmark ID format
 * @param id - Benchmark ID to validate
 * @returns Validation result
 */
export function validateBenchmarkId(id: string | null): ValidationResult {
  if (!id) {
    return {
      valid: false,
      error: "Benchmark ID is required.",
    };
  }

  // Basic format check
  if (id.length < 5) {
    return {
      valid: false,
      error: "Invalid benchmark ID format.",
    };
  }

  return { valid: true };
}

/**
 * Validate library selection
 * @param libraries - Array of library IDs
 * @returns Validation result
 */
export function validateLibrarySelection(libraries: string[]): ValidationResult {
  if (libraries.length === 0) {
    return {
      valid: false,
      error: "Please select at least one library.",
    };
  }

  return { valid: true };
}
