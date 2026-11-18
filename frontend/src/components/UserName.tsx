import React from "react";
import type { User } from "@/types";
import { badgesOf, nameColor } from "@/utils/theme";

interface UserNameProps {
  user: Pick<User, "name" | "customization_json">;
  className?: string;
  showBadge?: boolean;
}

/** A person's name with their equipped name color and badge. */
export const UserName: React.FC<UserNameProps> = ({ user, className = "", showBadge = true }) => {
  const badges = showBadge ? badgesOf(user) : [];
  return (
    <span className="inline-flex items-center gap-1.5 min-w-0">
      <span className={className} style={{ color: nameColor(user) }}>
        {user.name}
      </span>
      {badges.map((badge, index) => (
        <span
          key={index}
          className="px-1.5 py-px text-[10px] font-bold rounded-sm flex-shrink-0"
          style={{ backgroundColor: badge.background, color: badge.color }}
        >
          {badge.label}
        </span>
      ))}
    </span>
  );
};
