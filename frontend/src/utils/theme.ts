import type { User } from "@/types";

/**
 * Customization tokens come from the API (catalog items bought with soap) and end up in inline styles.
 * Nothing is trusted: colors must be hex, shadows must match a strict pattern, text is escaped by React.
 */
const HEX = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;
const GLOW = /^0 0 (?:[0-9]|[1-2][0-9])px #(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;

export function safeColor(value: unknown): string | null {
  return typeof value === "string" && HEX.test(value) ? value : null;
}

export function safeGlow(value: unknown): string | null {
  return typeof value === "string" && GLOW.test(value) ? value : null;
}

/** Text color (white or near-black) that stays readable on top of `hex`. */
export function contrastText(hex: string): string {
  const full = hex.length === 4 ? "#" + [...hex.slice(1)].map((c) => c + c).join("") : hex;
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(full.slice(i, i + 2), 16) / 255);
  const lin = (c: number) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  const luminance = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  return luminance > 0.4 ? "#0F172A" : "#FFFFFF";
}

type Equipped = { metadata?: Record<string, unknown> } | undefined;
type WithCustomization = Pick<User, "customization_json"> | null | undefined;

function slot(user: WithCustomization, name: string): Equipped {
  const entry = user?.customization_json?.[name];
  return entry && typeof entry === "object" ? (entry as Equipped) : undefined;
}

export function frameStyle(user: WithCustomization): React.CSSProperties | undefined {
  const meta = slot(user, "avatar_frame")?.metadata;
  const color = safeColor(meta?.border_color);
  if (!color) return undefined;
  const glow = safeGlow(meta?.glow);
  return { boxShadow: `0 0 0 3px ${color}${glow ? `, ${glow}` : ""}` };
}

export function nameColor(user: WithCustomization): string | undefined {
  return safeColor(slot(user, "name_color")?.metadata?.color) ?? undefined;
}

export interface Badge {
  label: string;
  background: string;
  color: string;
}

export function badgeOf(user: WithCustomization): Badge | null {
  const meta = slot(user, "badge")?.metadata;
  const label = typeof meta?.label === "string" ? meta.label.trim().slice(0, 24) : "";
  if (!label) return null;
  const background = safeColor(meta?.badge_color) ?? "#7B63FF";
  return { label, background, color: contrastText(background) };
}

export function themeColors(user: WithCustomization): { primary: string; secondary: string } | null {
  const meta = slot(user, "profile_theme")?.metadata;
  const primary = safeColor(meta?.primary);
  const secondary = safeColor(meta?.secondary);
  return primary && secondary ? { primary, secondary } : null;
}
