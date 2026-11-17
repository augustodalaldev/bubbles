import React from "react";
import { User } from "@/types";
import { Avatar } from "@/components/Avatar";
import { SoapIcon } from "@/components/SoapIcon";
import { ShieldCheck, Eye } from "lucide-react";

interface LiveProfilePreviewProps {
  currentUser: User;
}

export const LiveProfilePreview: React.FC<LiveProfilePreviewProps> = ({
  currentUser,
}) => {
  const customization = currentUser.customization_json || {};
  const avatarFrame = customization.avatar_frame;
  const profileTheme = customization.profile_theme;
  const badge = customization.badge;

  const primaryColor = profileTheme?.metadata?.primary || "#F465AC";
  const secondaryColor = profileTheme?.metadata?.secondary || "#7B63FF";

  const borderColor = avatarFrame?.metadata?.border_color || "#E2E8F0";
  const glow = avatarFrame?.metadata?.glow || "none";

  return (
    <div className="panel-classic">
      <div className="panel-classic-header flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Eye className="w-3.5 h-3.5 text-pink-600" />
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Pré-visualização ao Vivo
          </h2>
        </div>
        <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded-sm border border-emerald-200 font-semibold">
          Tempo Real
        </span>
      </div>

      <div className="p-3">
        {/* Sample Profile Header with Theme Gradient */}
        <div
          className="w-full h-12 rounded-t-sm p-2 flex items-center justify-between shadow-2xs"
          style={{
            background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})`,
          }}
        >
          <span className="text-[10px] font-bold text-white tracking-wide uppercase">
            {profileTheme?.name || "Tema Padrão"}
          </span>
          <div className="flex items-center gap-1 bg-white/20 px-1.5 py-0.5 rounded-sm backdrop-blur-xs text-[10px] text-white">
            <SoapIcon size={12} />
            <span>{currentUser.soap_balance ?? 0}</span>
          </div>
        </div>

        {/* Profile Card Body */}
        <div className="bg-white border-x border-b border-slate-200 p-3 pt-0 rounded-b-sm text-center">
          
          {/* Avatar with Equipped Frame */}
          <div className="-mt-6 mb-2 inline-block relative">
            <div
              className="w-16 h-16 rounded-full overflow-hidden p-0.5 mx-auto bg-white transition-all duration-300"
              style={{
                border: `3px solid ${borderColor}`,
                boxShadow: glow,
              }}
            >
              <Avatar user={currentUser} className="w-full h-full border-0" />
            </div>
          </div>

          <div className="flex items-center justify-center gap-1.5">
            <h3 className="text-xs font-bold text-slate-900 truncate">
              {currentUser.name}
            </h3>
            {badge && (
              <span
                className="inline-flex items-center gap-0.5 text-[9px] font-bold text-white px-1 py-0.2 rounded-2xs"
                style={{ backgroundColor: badge.metadata?.badge_color || "#7B63FF" }}
                title={badge.name}
              >
                <ShieldCheck className="w-2.5 h-2.5" />
                {badge.name.split(" ")[0]}
              </span>
            )}
          </div>
          <span className="text-[11px] text-slate-400 block -mt-0.5 mb-2">
            @{currentUser.username}
          </span>

          <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed text-center px-1">
            {currentUser.description}
          </p>

          <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-around text-[10px] text-slate-500">
            <div>
              <span className="font-bold text-slate-900 block text-xs">
                {currentUser.followers_count ?? 0}
              </span>
              seguidores
            </div>
            <div className="h-4 w-px bg-slate-200" />
            <div>
              <span className="font-bold text-slate-900 block text-xs">
                {currentUser.following_count ?? 0}
              </span>
              seguindo
            </div>
          </div>

        </div>

        <p className="text-[10px] text-slate-400 mt-2.5 leading-tight text-center">
          * As alterações equipadas são refletidas instantaneamente em todas as telas da rede.
        </p>
      </div>
    </div>
  );
};
