import { useContext } from "react";
import { ToastContext, type Toast } from "../context/ToastContext";

/**
 * ToastContainer - Displays toast notifications
 * Features:
 * - Enter animation: slide in from right + fade in
 * - Exit animation: slide out to right + fade out
 * - 3 types: success (green), error (red), info (blue)
 * - Auto-dismiss after 3.5 seconds
 * - Stacked queue layout
 */
export default function ToastContainer() {
  // Access context directly to get full context including toasts and removeToast
  const context = useContext(ToastContext);

  if (!context) {
    return null;
  }

  const { toasts, removeToast } = context;

  const getStyles = (type: string) => {
    switch (type) {
      case "success":
        return {
          bg: "bg-green-500",
          icon: "✓",
          border: "border-green-600",
        };
      case "error":
        return {
          bg: "bg-red-500",
          icon: "✕",
          border: "border-red-600",
        };
      case "info":
      default:
        return {
          bg: "bg-blue-500",
          icon: "ℹ",
          border: "border-blue-600",
        };
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
      {toasts.map((toast: Toast) => {
        const styles = getStyles(toast.type);
        return (
          <div
            key={toast.id}
            onClick={() => removeToast(toast.id)}
            className={`
              ${styles.bg} ${styles.border}
              text-white rounded-lg shadow-xl p-4 flex items-center gap-3
              border border-opacity-30
              pointer-events-auto cursor-pointer
              animate-in fade-in slide-in-from-right-8 duration-300
              hover:shadow-2xl transition-shadow
              max-w-sm
              group
            `}
            style={{
              animation: `slideInRight 0.3s ease-out`,
            }}
          >
            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-white bg-opacity-20 flex-shrink-0">
              <span className="font-bold text-sm">{styles.icon}</span>
            </div>
            <p className="text-sm font-medium flex-1">{toast.message}</p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeToast(toast.id);
              }}
              className="text-white opacity-60 hover:opacity-100 transition flex-shrink-0 text-lg leading-none"
            >
              ✕
            </button>
          </div>
        );
      })}
      <style>{`
        @keyframes slideInRight {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOutRight {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
