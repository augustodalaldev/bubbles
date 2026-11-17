/** Relative time in pt-BR ("há 5 min"), computed against the real clock. */
export function timeAgo(iso: string, now: number = Date.now()): string {
  const diffMin = Math.floor((now - new Date(iso).getTime()) / 60_000);
  if (Number.isNaN(diffMin)) return "";
  if (diffMin < 1) return "agora";
  if (diffMin < 60) return `há ${diffMin} min`;
  const hours = Math.floor(diffMin / 60);
  if (hours < 24) return `há ${hours} h`;
  const days = Math.floor(hours / 24);
  return `há ${days} dia${days > 1 ? "s" : ""}`;
}

/** Time left until `iso`, e.g. "5h" or "<1h" (used by bubblepops). */
export function hoursLeft(iso: string, now: number = Date.now()): string {
  const minutes = Math.floor((new Date(iso).getTime() - now) / 60_000);
  if (Number.isNaN(minutes) || minutes <= 0) return "expirado";
  if (minutes < 60) return "<1h";
  return `${Math.ceil(minutes / 60)}h`;
}
