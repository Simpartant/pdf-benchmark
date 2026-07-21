// Application configuration constants

export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  API_VERSION: "v1",
  TIMEOUT: 30000, // 30 seconds
} as const;

export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
  ALLOWED_TYPES: ["application/pdf"] as readonly string[],
  ALLOWED_EXTENSIONS: [".pdf"] as readonly string[],
} as const;

export const POLLING_CONFIG = {
  INTERVAL: 1000, // 1 second
  MAX_RETRIES: 3,
  RETRY_DELAY: 2000, // 2 seconds
} as const;

export const UI_CONFIG = {
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 5000,
  ANIMATION_DURATION: 200,
} as const;
