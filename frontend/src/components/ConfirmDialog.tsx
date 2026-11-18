import React, { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";

interface ConfirmDialogProps {
  title: string;
  children: React.ReactNode;
  confirmLabel: string;
  /** When set, the confirm button only works after this exact text is typed. */
  requireText?: string;
  busy?: boolean;
  error?: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Modal for destructive actions: states the consequences and (optionally) asks to type a word. */
export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  title,
  children,
  confirmLabel,
  requireText,
  busy = false,
  error,
  onConfirm,
  onCancel,
}) => {
  const [typed, setTyped] = useState("");
  const ready = !requireText || typed.trim().toLowerCase() === requireText.toLowerCase();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && !busy && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onCancel]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40">
      <div role="alertdialog" aria-modal="true" aria-label={title} className="w-full max-w-md panel-classic bg-white shadow-2xl">
        <div className="panel-classic-header flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-600" />
          <h2 className="text-xs font-bold text-slate-900">{title}</h2>
        </div>
        <div className="p-4 space-y-3 text-xs text-slate-700 leading-relaxed">
          {children}
          {requireText && (
            <label className="block">
              <span className="block mb-1 font-semibold text-slate-800">
                Para confirmar, digite <span className="font-mono text-red-700">{requireText}</span>
              </span>
              <input
                autoFocus
                value={typed}
                onChange={(e) => setTyped(e.target.value)}
                autoComplete="off"
                aria-label={`Digite ${requireText} para confirmar`}
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-red-500"
              />
            </label>
          )}
          {error && (
            <p role="alert" className="text-red-700 font-semibold">
              {error}
            </p>
          )}
        </div>
        <div className="p-3 bg-slate-50 border-t border-slate-200 flex justify-end gap-2">
          <button onClick={onCancel} disabled={busy} className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 disabled:opacity-60">
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            disabled={!ready || busy}
            className="px-3 py-1.5 text-xs font-bold rounded-sm bg-red-600 text-white hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {busy ? "Aguarde..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};
