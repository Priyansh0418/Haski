import { createContext, useContext, useState, useCallback } from "react";

export type ToastType = "success" | "error" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastAPI {
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}

export interface ToastContextType extends ToastAPI {
  toasts: Toast[];
  removeToast: (id: string) => void;
}

export const ToastContext = createContext<ToastContextType | undefined>(
  undefined
);

/**
 * Toast Provider - Simple queue-based notification system
 * Features:
 * - 3 types: success, error, info
 * - Auto-dismiss after 3.5 seconds
 * - Queue management with enter/exit animations
 * - Zero dependencies (pure React)
 */
export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (message: string, type: ToastType) => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      const toast: Toast = { id, message, type };

      setToasts((prev) => [...prev, toast]);

      // Auto-dismiss after 3.5 seconds
      setTimeout(() => {
        removeToast(id);
      }, 3500);

      return id;
    },
    [removeToast]
  );

  const success = useCallback(
    (message: string) => {
      addToast(message, "success");
    },
    [addToast]
  );

  const error = useCallback(
    (message: string) => {
      addToast(message, "error");
    },
    [addToast]
  );

  const info = useCallback(
    (message: string) => {
      addToast(message, "info");
    },
    [addToast]
  );

  return (
    <ToastContext.Provider
      value={{
        toasts,
        removeToast,
        success,
        error,
        info,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastAPI {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return { success: context.success, error: context.error, info: context.info };
}
