"use client";

import { useState, useCallback } from "react";
import { ToastType } from "@/components/Toast";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

/**
 * Custom hook for managing toast notifications
 * @returns Toast state and control functions
 */
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const toast: Toast = { id, message, type };

    setToasts((prev) => [...prev, toast]);

    // Auto-remove after duration
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const success = useCallback((message: string) => {
    showToast(message, "success");
  }, [showToast]);

  const error = useCallback((message: string) => {
    showToast(message, "error");
  }, [showToast]);

  const warning = useCallback((message: string) => {
    showToast(message, "warning");
  }, [showToast]);

  const info = useCallback((message: string) => {
    showToast(message, "info");
  }, [showToast]);

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };
}
