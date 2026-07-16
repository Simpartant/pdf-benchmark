"use client";

import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react";
import { useEffect, useState } from "react";

export type ToastType = "success" | "error" | "warning" | "info";

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose?: () => void;
}

/**
 * Toast notification component
 * Displays temporary messages to the user
 */
export function Toast({ 
  message, 
  type = "info", 
  duration = 5000,
  onClose 
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  if (!isVisible) return null;

  const styles = {
    success: {
      bg: "bg-green-500/10 border-green-500/20",
      text: "text-green-500",
      icon: CheckCircle,
    },
    error: {
      bg: "bg-red-500/10 border-red-500/20",
      text: "text-red-500",
      icon: AlertCircle,
    },
    warning: {
      bg: "bg-yellow-500/10 border-yellow-500/20",
      text: "text-yellow-500",
      icon: AlertTriangle,
    },
    info: {
      bg: "bg-blue-500/10 border-blue-500/20",
      text: "text-blue-500",
      icon: Info,
    },
  };

  const style = styles[type];
  const Icon = style.icon;

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 ${style.bg} border rounded-lg shadow-lg p-4 max-w-md animate-in slide-in-from-bottom-5`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 ${style.text} shrink-0 mt-0.5`} />
        <p className="flex-1 text-sm">{message}</p>
        <button
          onClick={() => {
            setIsVisible(false);
            onClose?.();
          }}
          className="shrink-0 hover:bg-muted/50 rounded p-1 transition-colors"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

/**
 * Toast container for managing multiple toasts
 */
interface ToastContainerProps {
  toasts: Array<{
    id: string;
    message: string;
    type: ToastType;
  }>;
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => onRemove(toast.id)}
        />
      ))}
    </div>
  );
}
