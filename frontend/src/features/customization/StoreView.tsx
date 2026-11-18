import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { CustomizationItem } from "@/types";
import { CustomizationCard } from "./CustomizationCard";
import { LiveProfilePreview } from "./LiveProfilePreview";
import { SoapIcon } from "@/components/SoapIcon";
import { ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { equipSlots, listItems, purchaseItem } from "@/services/customization";
import { errorMessage } from "@/services/errors";
import { BADGE_SLOTS } from "@/utils/theme";
import { 
  Store, 
  Compass, 
  User as UserIcon, 
  Check, 
  AlertCircle,
  Package,
  Layers
} from "lucide-react";

interface StoreViewProps {
}

export const StoreView: React.FC<StoreViewProps> = ({
}) => {
  const currentUser = useAuthStore((s) => s.user)!;
  const economy = useAuthStore((s) => s.economy);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const [items, setItems] = useState<CustomizationItem[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"catalog" | "inventory">("catalog");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [notice, setNotice] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const passiveHint = economy
    ? `+${economy.default_passive_earn_rate} a cada ${economy.passive_interval_minutes} min`
    : "";

  const showNotice = (message: string, type: "success" | "error") => {
    setNotice({ message, type });
    window.setTimeout(() => setNotice(null), 3500);
  };

  const loadItems = useCallback(async () => {
    try {
      const data = await listItems();
      setItems(data.results);
      setStatus("ready");
    } catch (err) {
      setLoadError(errorMessage(err));
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    void loadItems();
  }, [loadItems]);

  const handlePurchase = async (item: CustomizationItem) => {
    setBusyId(item.id);
    try {
      await purchaseItem(item.id);
      await Promise.all([loadItems(), refreshUser()]);
      showNotice(`Você adquiriu "${item.name}". O item já está no seu inventário.`, "success");
    } catch (err) {
      showNotice(errorMessage(err), "error");
    } finally {
      setBusyId(null);
    }
  };

  // Slot names are the lower-cased item types; `null` unequips the slot.
  const handleEquipToggle = async (item: CustomizationItem) => {
    // One change at a time: the slot is chosen from the current state, which an in-flight request
    // is about to change.
    if (busyId !== null) return;
    // A profile shows up to three badges (badge, badge_2, badge_3); every other type has one slot.
    const equipped = (useAuthStore.getState().user?.customization_json ?? {}) as Record<string, { id?: number } | undefined>;
    const candidates: string[] = item.item_type === "BADGE" ? [...BADGE_SLOTS] : [item.item_type.toLowerCase()];
    const current = candidates.find((s) => equipped[s]?.id === item.id);
    const free = candidates.find((s) => !equipped[s]);
    const target = item.is_equipped ? (current ?? candidates[0]) : (free ?? (item.item_type === "BADGE" ? null : candidates[0]));
    if (!target) {
      showNotice("Você já exibe 3 selos. Desequipe um antes de equipar outro.", "error");
      return;
    }
    setBusyId(item.id);
    try {
      await equipSlots({ [target]: item.is_equipped ? null : item.id });
      await Promise.all([loadItems(), refreshUser()]);
      showNotice(
        item.is_equipped ? `"${item.name}" foi desequipado.` : `"${item.name}" equipado com sucesso.`,
        "success"
      );
    } catch (err) {
      showNotice(errorMessage(err), "error");
    } finally {
      setBusyId(null);
    }
  };

  const filteredItems = useMemo(() => {
    let list = items;
    if (activeTab === "inventory") list = list.filter((i) => i.is_owned);
    if (selectedCategory !== "ALL") list = list.filter((i) => i.item_type === selectedCategory);
    return list;
  }, [items, activeTab, selectedCategory]);

  const ownedCount = items.filter((i) => i.is_owned).length;
  const equippedCount = items.filter((i) => i.is_equipped).length;

  if (status === "loading") return <LoadingState label="Carregando a loja..." />;
  if (status === "error") {
    return (
      <div className="max-w-xl mx-auto px-4 py-10">
        <ErrorState message={loadError ?? "Não foi possível carregar a loja."} onRetry={() => void loadItems()} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
      
      {/* 3-Column Classic Grid (Left 3 cols, Center 6 cols, Right 3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start lg:h-full">
        
        {/* Left Column (3 Cols) - Static Sidebar */}
        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Soap Wallet Box */}
          <div className="panel-classic">
            <div className="panel-classic-header flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">
                Minha carteira
              </span>
              <span className="text-[10px] font-semibold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200">
                {passiveHint}
              </span>
            </div>
            <div className="p-3">
              <div className="flex items-center gap-2 mb-2">
                <SoapIcon size={24} />
                <div>
                  <span className="text-base font-bold text-pink-900 block leading-tight">
                    {currentUser.soap_balance ?? 0} soap
                  </span>
                  <span className="text-[10px] text-slate-500">
                    Disponível para compras e apoios
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                <span>Itens possuídos:</span>
                <span className="font-bold text-slate-900">{ownedCount}</span>
              </div>
              <div className="pt-1 flex items-center justify-between text-xs text-slate-600">
                <span>Itens equipados:</span>
                <span className="font-bold text-pink-600">{equippedCount}</span>
              </div>
            </div>
          </div>

          {/* Quick Navigation Panel */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">
                Navegação
              </span>
            </div>
            <div className="p-1 text-xs">
              <Link to={paths.home}
                
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <Compass className="w-4 h-4 text-slate-400" />
                <span>Início (feed)</span>
              </Link>
              <Link to={paths.profile(currentUser.username)}
                
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <UserIcon className="w-4 h-4 text-slate-400" />
                <span>Meu perfil</span>
              </Link>
              <Link to={paths.communities}
                
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <Layers className="w-4 h-4 text-slate-400" />
                <span>Comunidades</span>
              </Link>
            </div>
          </div>

          {/* Store Concept Note */}
          <div className="panel-classic bg-slate-50/50">
            <div className="p-3">
              <span className="text-xs font-bold text-slate-800 block mb-1">
                Cosméticos e Identidade
              </span>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Nenhum item da loja concede privilégios abusivos ou quebra a ordem cronológica da rede. Todos os cosméticos são de uso perene.
              </p>
            </div>
          </div>

        </div>

        {/* Center Lane (6 Cols) - THE ONLY SCROLLABLE AREA */}
        <div className="lg:col-span-6 min-w-0 lg:h-full lg:overflow-y-auto pr-1.5 scrollbar-thin">
          
          {/* Notification Feedback Toast */}
          {notice && (
            <div
              className={`mb-4 p-3 rounded-sm text-xs font-semibold flex items-center gap-2 border shadow-xs ${
                notice.type === "success"
                  ? "bg-green-50 border-green-200 text-green-800"
                  : "bg-red-50 border-red-200 text-red-800"
              }`}
            >
              {notice.type === "success" ? (
                <Check className="w-4 h-4 text-green-600 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
              )}
              <span>{notice.message}</span>
            </div>
          )}

          {/* Store Top Card */}
          <div className="panel-classic mb-4">
            <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <Store className="w-4 h-4 text-pink-600" />
                  <h1 className="text-sm font-bold text-slate-900 tracking-tight">
                    Loja de Customizações & Inventário
                  </h1>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Personalize sua presença com molduras, temas, selos (até 3), papéis de parede, cores de destaque e uma seção só sua.
                </p>
              </div>

              {/* Soap Balance Quick Pill */}
              <div className="flex items-center gap-1.5 px-3 py-1 bg-pink-50 border border-pink-200 rounded-sm self-start sm:self-auto">
                <SoapIcon size={16} />
                <span className="text-xs font-bold text-pink-900">
                  {currentUser.soap_balance ?? 0} soap
                </span>
              </div>
            </div>

            {/* Main Tabs: Catálogo vs Meu inventário */}
            <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-2">
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setActiveTab("catalog")}
                  className={`px-3 py-1 text-xs font-bold rounded-sm transition-all ${
                    activeTab === "catalog"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  Catálogo da loja ({items.length})
                </button>
                <button
                  onClick={() => setActiveTab("inventory")}
                  className={`px-3 py-1 text-xs font-bold rounded-sm transition-all ${
                    activeTab === "inventory"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  Meu inventário ({ownedCount})
                </button>
              </div>

              <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
                {activeTab === "catalog" ? "Todos os itens" : "Itens adquiridos"}
              </span>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="panel-classic mb-4">
            <div className="p-2 flex flex-wrap items-center gap-1">
              {[
                { id: "ALL", label: "Todas as Categorias" },
                { id: "AVATAR_FRAME", label: "Molduras de Avatar" },
                { id: "PROFILE_THEME", label: "Temas de Perfil" },
                { id: "CHAT_BUBBLE", label: "Bolhas de Chat" },
                { id: "BADGE", label: "Insígnias" },
                { id: "NAME_COLOR", label: "Cores de Nome" },
                { id: "WALLPAPER", label: "Papéis de Parede" },
                { id: "ACCENT_COLOR", label: "Cores de Destaque" },
                { id: "SECTION", label: "Seção do Perfil" },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-2.5 py-1 text-[11px] font-semibold rounded-sm transition-all ${
                    selectedCategory === cat.id
                      ? "bg-slate-800 text-white shadow-2xs"
                      : "bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Items Grid */}
          {filteredItems.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {filteredItems.map((item) => (
                <CustomizationCard
                  key={item.id}
                  item={item}
                  balance={currentUser.soap_balance ?? 0}
                  previewPhoto={currentUser.profile_photo}
                  previewName={currentUser.name}
                  busy={busyId === item.id}
                  onPurchase={(i) => void handlePurchase(i)}
                  onEquipToggle={(i) => void handleEquipToggle(i)}
                />
              ))}
            </div>
          ) : (
            <div className="panel-classic p-8 text-center text-slate-500">
              <Package className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-700">
                Nenhum item encontrado nesta categoria.
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                {activeTab === "inventory"
                  ? "Explore o catálogo da loja para adquirir novos itens com seu soap!"
                  : "Selecione outra categoria de itens."}
              </p>
            </div>
          )}

          {/* Footer note inside the scrollable stream at the bottom */}
          <div className="py-6 text-center text-[11px] text-slate-400">
            Bubbles • Loja de Customizações
          </div>

        </div>

        {/* Right Column (3 Cols) - Static Sidebar */}
        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Live Profile Preview with Active Equips */}
          <LiveProfilePreview currentUser={currentUser} />

          {/* How Soap Works Box */}
          <div className="panel-classic bg-slate-50/50">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">
                Como conseguir soap
              </span>
            </div>
            <div className="p-3 text-xs text-slate-600 space-y-2">
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-pink-100 text-pink-700 text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  1
                </span>
                <span>
                  <strong>Ganho passivo:</strong> {economy ? `receba ${economy.default_passive_earn_rate} soap a cada ${economy.passive_interval_minutes} minutos de uso, até ${economy.passive_daily_cap} por dia.` : "receba soap enquanto usa a rede."}
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-pink-100 text-pink-700 text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  2
                </span>
                <span>
                  <strong>Apoios Recebidos:</strong> Outros usuários podem enviar 1 soap em reconhecimento às suas publicações.
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-pink-100 text-pink-700 text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  3
                </span>
                <span>
                  <strong>Sem Pay-to-Win:</strong> Soap não pode ser comprado com dinheiro real, valorizando o mérito da comunidade.
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
