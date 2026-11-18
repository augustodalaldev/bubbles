import React from "react";
import { ShieldAlert } from "lucide-react";

interface ModerationBannerProps {
  title: string;
  until?: string | null;
  reason?: string;
  children?: React.ReactNode;
}

export const formatUntil = (iso: string) =>
  new Date(iso).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });

/** Notice shown to the people affected by a suspension or ban, with the end date and the reason. */
export const ModerationBanner: React.FC<ModerationBannerProps> = ({ title, until, reason, children }) => (
  <div role="status" className="bg-amber-50 border-y border-amber-300 text-amber-900">
    <div className="max-w-7xl mx-auto px-3 sm:px-4 py-2 flex items-start gap-2 text-xs">
      <ShieldAlert className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
      <div className="min-w-0">
        <p className="font-bold">
          {title}
          {until ? ` até ${formatUntil(until)}` : ""}
        </p>
        {reason && <p className="break-words">Motivo: {reason}</p>}
        {children && <p className="mt-0.5">{children}</p>}
      </div>
    </div>
  </div>
);
