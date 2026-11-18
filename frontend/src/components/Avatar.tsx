import React from "react";
import type { User } from "@/types";
import { frameStyle } from "@/utils/theme";

interface AvatarProps {
  user: Pick<User, "name" | "username" | "profile_photo" | "customization_json">;
  className?: string;
}

/** Round avatar with the person's equipped frame; falls back to the initial without a photo. */
export const Avatar: React.FC<AvatarProps> = ({ user, className = "w-8 h-8" }) =>
  user.profile_photo ? (
    <img
      src={user.profile_photo}
      alt={user.name}
      style={frameStyle(user)}
      className={`${className} rounded-full object-cover border border-slate-200`}
    />
  ) : (
    <span
      aria-label={user.name}
      style={frameStyle(user)}
      className={`${className} rounded-full border border-slate-200 bg-pink-50 text-pink-700 font-bold flex items-center justify-center text-xs`}
    >
      {(user.name || user.username).charAt(0).toUpperCase()}
    </span>
  );
