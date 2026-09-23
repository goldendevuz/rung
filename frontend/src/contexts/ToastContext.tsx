import React, { createContext, useContext, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastContextType {
  toast: {
    success: (message: string, duration?: number) => void;
    error: (message: string, duration?: number) => void;
    info: (message: string, duration?: number) => void;
    warning: (message: string, duration?: number) => void;
  };
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((type: ToastType, message: string, duration = 4000) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message, duration }]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, [removeToast]);

  const toastMethods = React.useMemo(() => ({
    success: (msg: string, dur?: number) => addToast('success', msg, dur),
    error: (msg: string, dur?: number) => addToast('error', msg, dur),
    info: (msg: string, dur?: number) => addToast('info', msg, dur),
    warning: (msg: string, dur?: number) => addToast('warning', msg, dur),
  }), [addToast]);

  return (
    <ToastContext.Provider value={{ toast: toastMethods }}>
      {children}
      {typeof document !== 'undefined' && createPortal(
        <div 
          className="fixed top-5 right-5 sm:right-6 z-[99999] flex flex-col gap-2.5 max-w-[380px] w-[calc(100vw-32px)] pointer-events-none"
          role="region"
          aria-live="polite"
        >
          {toasts.map((t) => {
            let borderColor = 'rgba(255, 255, 255, 0.12)';
            let iconColor = '#B8F03C';
            let icon = '✓';
            let bg = '#16191D';

            if (t.type === 'error') {
              borderColor = 'rgba(239, 68, 68, 0.35)';
              iconColor = '#EF4444';
              icon = '✕';
              bg = '#1C1417';
            } else if (t.type === 'info') {
              borderColor = 'rgba(59, 130, 246, 0.35)';
              iconColor = '#3B82F6';
              icon = 'ℹ';
              bg = '#141720';
            } else if (t.type === 'warning') {
              borderColor = 'rgba(234, 179, 8, 0.35)';
              iconColor = '#EAB308';
              icon = '⚠';
              bg = '#1A1813';
            } else {
              borderColor = 'rgba(184, 240, 60, 0.35)';
              iconColor = '#B8F03C';
              icon = '✓';
              bg = '#131815';
            }

            return (
              <div
                key={t.id}
                className="pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-2xl transition-all animate-slide-in"
                style={{
                  backgroundColor: bg,
                  border: `1px solid ${borderColor}`,
                  boxShadow: '0 12px 32px rgba(0, 0, 0, 0.6)',
                  animation: 'fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                }}
              >
                <div 
                  className="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5"
                  style={{ backgroundColor: `${iconColor}22`, color: iconColor }}
                >
                  {icon}
                </div>
                <div className="flex-1 text-sm font-medium text-white leading-snug">
                  {t.message}
                </div>
                <button
                  type="button"
                  onClick={() => removeToast(t.id)}
                  className="text-white/40 hover:text-white transition-colors text-xs p-1 -mr-1 -mt-1 rounded-md"
                  aria-label="Yopish"
                >
                  ✕
                </button>
              </div>
            );
          })}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context.toast;
}
