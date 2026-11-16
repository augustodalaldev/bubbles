import React from "react";
import { CustomizationItem, User } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { Check, ShieldCheck, Sparkles } from "lucide-react";

interface CustomizationCardProps {
  item: CustomizationItem;
  currentUser: User;
  onPurchase: (item: CustomizationItem) => void;
  onEquipToggle: (item: CustomizationItem) => void;
}

export const CustomizationCard: React.FC<CustomizationCardProps> = ({
  item,
  currentUser,
  onPurchase,
  onEquipToggle,
}) => {
  const isOwned = item.is_owned;
  const isEquipped = item.is_equipped;
  const userSoap = currentUser.soap_balance ?? 0;
  const canAfford = userSoap >= item.price;

  // Render Visual Mini Preview according to item type
  const renderPreview = () => {
    if (item.item_type === "AVATAR_FRAME") {
      const borderColor = item.metadata?.border_color || "#F465AC";
      const glow = item.metadata?.glow || "none";

      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <div
            className="w-14 h-14 rounded-full overflow-hidden p-0.5 transition-transform group-hover:scale-105"
            style={{
              border: `3px solid ${borderColor}`,
              boxShadow: glow,
            }}
          >
            <img
              src={currentUser.profile_photo || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"}
              alt="Preview"
              className="w-full h-full object-cover rounded-full"
            />
          </div>
        </div>
      );
    }

    if (item.item_type === "PROFILE_THEME") {
      const primary = item.metadata?.primary || "#F465AC";
      const secondary = item.metadata?.secondary || "#7B63FF";

      return (
        <div className="h-24 bg-slate-50 flex flex-col justify-between p-3 border-b border-slate-200">
          <div
            className="w-full h-7 rounded-sm flex items-center px-2 text-[10px] font-bold text-white shadow-2xs"
            style={{
              background: `linear-gradient(135deg, ${primary}, ${secondary})`,
            }}
          >
            Cabeçalho Orkut Aero
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-4 h-4 rounded-full border border-slate-300"
              style={{ backgroundColor: primary }}
              title="Primária"
            />
            <span
              className="w-4 h-4 rounded-full border border-slate-300"
              style={{ backgroundColor: secondary }}
              title="Secundária"
            />
            <span className="text-[10px] text-slate-500 font-mono ml-auto">
              {primary}
            </span>
          </div>
        </div>
      );
    }

    if (item.item_type === "CHAT_BUBBLE") {
      const border = item.metadata?.border || "#F465AC";
      const tint = item.metadata?.tint || "rgba(244, 101, 172, 0.1)";

      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <div
            className="px-3 py-1.5 rounded-xl text-xs text-slate-800 shadow-2xs text-center max-w-[180px]"
            style={{
              backgroundColor: tint,
              border: `1.5px solid ${border}`,
            }}
          >
            Olá! Bolha personalizada.
          </div>
        </div>
      );
    }

    if (item.item_type === "BADGE") {
      const badgeColor = item.metadata?.badge_color || "#7B63FF";

      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <span
            className="inline-flex items-center gap-1 px-3 py-1 rounded-sm text-xs font-bold text-white shadow-xs"
            style={{ backgroundColor: badgeColor }}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            {item.name}
          </span>
        </div>
      );
    }

    return (
      <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
        <Sparkles className="w-6 h-6 text-pink-600" />
      </div>
    );
  };

  const getCategoryLabel = (type: string) => {
    switch (type) {
      case "AVATAR_FRAME":
        return "Moldura de Avatar";
      case "PROFILE_THEME":
        return "Tema de Perfil";
      case "CHAT_BUBBLE":
        return "Bolha de Chat";
      case "BADGE":
        return "Insígnia";
      case "NAME_COLOR":
        return "Cor de Nome";
      default:
        return "Item";
    }
  };

  return (
    <div className="panel-classic hover:shadow-md transition-all flex flex-col justify-between group">
      <div>
        {/* Visual Preview */}
        {renderPreview()}

        {/* Card Content */}
        <div className="p-3">
          <div className="flex items-center justify-between gap-1 mb-1">
            <span className="text-[10px] font-bold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200">
              {getCategoryLabel(item.item_type)}
            </span>

            {isEquipped && (
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded-sm border border-emerald-200 flex items-center gap-0.5">
                <Check className="w-3 h-3 text-emerald-600" />
                Equipado
              </span>
            )}
          </div>

          <h3 className="text-xs font-bold text-slate-900 group-hover:text-pink-600 transition-colors">
            {item.name}
          </h3>
          <p className="text-[11px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
            {item.description}
          </p>
        </div>
      </div>

      {/* Card Footer: Price & Action */}
      <div className="p-3 pt-2 border-t border-slate-100 bg-white flex items-center justify-between gap-2">
        
        {/* Price in Soap */}
        <div className="flex items-center gap-1.5">
          <SoapIcon size={16} />
          <span className="text-xs font-bold text-slate-900">
            {item.price}
          </span>
          <span className="text-[10px] text-slate-400 font-normal">
            soap
          </span>
        </div>

        {/* Action Button */}
        <div>
          {isOwned ? (
            <button
              onClick={() => onEquipToggle(item)}
              className={`px-3 py-1 text-xs font-bold rounded-sm transition-all shadow-xs ${
                isEquipped
                  ? "border border-slate-300 text-slate-700 hover:bg-slate-100"
                  : "bg-pink-600 text-white hover:bg-pink-700 active:scale-95"
              }`}
            >
              {isEquipped ? "Desequipar" : "Equipar"}
            </button>
          ) : (
            <button
              onClick={() => onPurchase(item)}
              disabled={!canAfford}
              className={`px-3 py-1 text-xs font-bold rounded-sm transition-all shadow-xs ${
                !canAfford
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-slate-900 text-white hover:bg-pink-600 active:scale-95 cursor-pointer"
              }`}
            >
              {canAfford ? "Comprar" : "Sem saldo"}
            </button>
          )}
        </div>

      </div>
    </div>
  );
};
