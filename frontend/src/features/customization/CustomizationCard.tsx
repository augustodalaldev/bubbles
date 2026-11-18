import React from "react";
import { CustomizationItem } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { Check, ShieldCheck, Sparkles } from "lucide-react";
import { safeColor, safeGlow } from "@/utils/theme";

interface CustomizationCardProps {
  item: CustomizationItem;
  /** Soap available to the buyer: the user's balance or, in a community store, the community's. */
  balance: number;
  previewPhoto?: string | null;
  previewName?: string;
  onPurchase: (item: CustomizationItem) => void;
  onEquipToggle: (item: CustomizationItem) => void;
  busy?: boolean;
}

export const CustomizationCard: React.FC<CustomizationCardProps> = ({
  item,
  balance,
  previewPhoto = null,
  previewName = "?",
  onPurchase,
  onEquipToggle,
  busy = false,
}) => {
  const isOwned = item.is_owned;
  const isEquipped = item.is_equipped;
  const canAfford = balance >= item.price;

  // Render Visual Mini Preview according to item type
  const renderPreview = () => {
    if (item.item_type === "AVATAR_FRAME") {
      const borderColor = safeColor(item.metadata?.border_color) ?? "#F465AC";
      const glow = safeGlow(item.metadata?.glow) ?? "none";

      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <div
            className="w-14 h-14 rounded-full overflow-hidden p-0.5 transition-transform group-hover:scale-105"
            style={{
              border: `3px solid ${borderColor}`,
              boxShadow: glow,
            }}
          >
            {previewPhoto ? (
              <img src={previewPhoto} alt="Prévia" className="w-full h-full object-cover rounded-full" />
            ) : (
              <span className="w-full h-full rounded-full bg-pink-50 text-pink-700 font-bold flex items-center justify-center text-sm">
                {previewName.charAt(0).toUpperCase()}
              </span>
            )}
          </div>
        </div>
      );
    }

    if (item.item_type === "PROFILE_THEME") {
      const primary = safeColor(item.metadata?.primary) ?? "#F465AC";
      const secondary = safeColor(item.metadata?.secondary) ?? "#7B63FF";

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
      const border = safeColor(item.metadata?.border) ?? "#F465AC";
      const tint = safeColor(item.metadata?.tint) ?? "#FCE7F3";

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

    if (item.item_type === "WALLPAPER") {
      return (
        <div className="h-24 border-b border-slate-200 bg-slate-100 overflow-hidden">
          {item.image ? (
            <img src={item.image} alt={`Prévia: ${item.name}`} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-pink-600" />
            </div>
          )}
        </div>
      );
    }

    if (item.item_type === "ACCENT_COLOR" || item.item_type === "NAME_COLOR") {
      const color = safeColor(item.metadata?.color) ?? "#F465AC";
      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center gap-3 p-3 border-b border-slate-200">
          <span className="w-9 h-9 rounded-full border border-slate-300" style={{ backgroundColor: color }} title={color} />
          {item.item_type === "ACCENT_COLOR" ? (
            <span
              className="px-3 py-1 text-xs font-bold rounded-sm border"
              style={{ backgroundColor: color, borderColor: color, color: "#fff", textShadow: "0 0 2px rgba(0,0,0,0.5)" }}
            >
              Botão
            </span>
          ) : (
            <span className="text-sm font-bold" style={{ color }}>
              {previewName}
            </span>
          )}
        </div>
      );
    }

    if (item.item_type === "SECTION") {
      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <div className="w-full max-w-[170px] bg-white border border-slate-200 rounded-sm shadow-2xs">
            <div className="px-2 py-1 border-b border-slate-200 text-[10px] font-bold text-slate-700">Minha seção</div>
            <div className="p-2 space-y-1">
              <span className="block h-1.5 w-full bg-slate-200 rounded-sm" />
              <span className="block h-1.5 w-2/3 bg-slate-200 rounded-sm" />
            </div>
          </div>
        </div>
      );
    }

    if (item.item_type === "BADGE") {
      const badgeColor = safeColor(item.metadata?.badge_color) ?? "#7B63FF";

      return (
        <div className="h-24 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-200">
          <span
            className="inline-flex items-center gap-1 px-3 py-1 rounded-sm text-xs font-bold text-white shadow-xs"
            style={{ backgroundColor: badgeColor }}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            {(item.metadata?.label as string | undefined) ?? item.name}
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
      case "WALLPAPER":
        return "Papel de Parede";
      case "ACCENT_COLOR":
        return "Cor de Destaque";
      case "SECTION":
        return "Seção do Perfil";
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
              disabled={busy}
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
              disabled={busy || !canAfford}
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
