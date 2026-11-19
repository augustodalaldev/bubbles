import React from "react";
import type { User } from "@/types";
import { badgesOf, nameColor } from "@/utils/theme";

interface UserNameProps {
  user: Pick<User, "name" | "customization_json">;
  className?: string;
  showBadge?: boolean;
  /**
   * `compact` (feeds, comments, lists): the name on one line and, below it, only the most
   * valuable badge plus a "+N" for the rest, so a long name or many badges never push it out.
   * `full` (the profile header): every badge, wrapping onto more lines if needed, centered under the photo.
   */
  variant?: "compact" | "full";
}

/** A person's name with their equipped name color and badges (below the name). */
export const UserName: React.FC<UserNameProps> = ({
  user,
  className = "",
  showBadge = true,
  variant = "compact",
}) => {
  const badges = showBadge ? badgesOf(user) : [];
  const shown = variant === "full" ? badges : badges.slice(0, 1);
  const hidden = badges.slice(shown.length);
  const centered = variant === "full";
  return (
    <span className={`inline-flex flex-col min-w-0 max-w-full align-top ${centered ? "items-center text-center" : "items-start"}`}>
      <span className={`${className} max-w-full ${variant === "compact" ? "truncate" : ""}`} style={{ color: nameColor(user) }} title={user.name}>
        {user.name}
      </span>
      {badges.length > 0 && (
        <span className={`mt-0.5 flex flex-wrap items-center gap-1 max-w-full ${centered ? "justify-center" : ""}`}>
          {shown.map((badge, index) => (
            <span
              key={index}
              className="px-1.5 py-px text-[10px] leading-tight font-bold rounded-sm max-w-[9rem] truncate"
              style={{ backgroundColor: badge.background, color: badge.color }}
              title={badge.label}
            >
              {badge.label}
            </span>
          ))}
          {hidden.length > 0 && (
            <span
              className="text-[10px] leading-tight font-semibold text-slate-500"
              title={hidden.map((b) => b.label).join(", ")}
            >
              +{hidden.length}
            </span>
          )}
        </span>
      )}
    </span>
  );
};
