import React from "react";
import { AlertCircle, Inbox, Loader2 } from "lucide-react";

export const LoadingState: React.FC<{ label?: string }> = ({ label = "Carregando..." }) => (
  <div className="flex items-center justify-center gap-2 py-10 text-xs text-slate-500" role="status">
    <Loader2 className="w-4 h-4 animate-spin" />
    <span>{label}</span>
  </div>
);

export const ErrorState: React.FC<{ message: string; onRetry?: () => void }> = ({
  message,
  onRetry,
}) => (
  <div className="flex flex-col items-center gap-2 py-10 text-center" role="alert">
    <AlertCircle className="w-5 h-5 text-pink-600" />
    <p className="text-xs text-slate-700">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="btn-pink px-3 py-1 text-xs font-bold rounded-sm">
        Tentar novamente
      </button>
    )}
  </div>
);

export const EmptyState: React.FC<{ message: string; hint?: string }> = ({ message, hint }) => (
  <div className="flex flex-col items-center gap-1 py-10 text-center">
    <Inbox className="w-5 h-5 text-slate-400" />
    <p className="text-xs font-semibold text-slate-700">{message}</p>
    {hint && <p className="text-[11px] text-slate-500">{hint}</p>}
  </div>
);
