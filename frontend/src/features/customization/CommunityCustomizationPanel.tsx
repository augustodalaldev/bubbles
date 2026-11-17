import React, { useCallback, useEffect, useState } from "react";
import { Community, CustomizationItem } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import {
  equipCommunitySlots,
  listCommunityItems,
  purchaseCommunityItem,
} from "@/services/customization";
import { errorMessage } from "@/services/errors";
import { Check, AlertCircle, Sparkles } from "lucide-react";
import { CustomizationCard } from "./CustomizationCard";

interface CommunityCustomizationPanelProps {
  community: Community;
  /** Soap in the community wallet (not the user's). */
  walletBalance: number | null;
  /** Called after a purchase or equip so the page can reload the community and its wallet. */
  onChanged: () => void | Promise<void>;
}

export const CommunityCustomizationPanel: React.FC<CommunityCustomizationPanelProps> = ({
  community,
  walletBalance,
  onChanged,
}) => {
  const [items, setItems] = useState<CustomizationItem[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [notice, setNotice] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await listCommunityItems(community.commname);
      setItems(data.results);
      setStatus("ready");
    } catch (err) {
      setLoadError(errorMessage(err));
      setStatus("error");
    }
  }, [community.commname]);

  useEffect(() => {
    void load();
  }, [load]);

  const run = async (item: CustomizationItem, action: () => Promise<string>) => {
    setBusyId(item.id);
    setNotice(null);
    try {
      const message = await action();
      await Promise.all([load(), onChanged()]);
      setNotice({ message, type: "success" });
    } catch (err) {
      setNotice({ message: errorMessage(err), type: "error" });
    } finally {
      setBusyId(null);
    }
  };

  const purchase = (item: CustomizationItem) =>
    run(item, async () => {
      await purchaseCommunityItem(community.commname, item.id);
      return `"${item.name}" foi comprado com o soap da comunidade.`;
    });

  const toggleEquip = (item: CustomizationItem) =>
    run(item, async () => {
      await equipCommunitySlots(community.commname, {
        [item.item_type.toLowerCase()]: item.is_equipped ? null : item.id,
      });
      return item.is_equipped ? `"${item.name}" foi removido da comunidade.` : `"${item.name}" aplicado à comunidade.`;
    });

  return (
    <div className="panel-classic">
      <div className="panel-classic-header flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-pink-600" />
          <h2 className="text-xs font-bold text-slate-900">Personalização da comunidade</h2>
        </div>
        <span
          title="Saldo da carteira da comunidade"
          className="flex items-center gap-1.5 px-2 py-0.5 bg-pink-50 border border-pink-200 rounded-sm text-xs font-bold text-pink-900"
        >
          <SoapIcon size={16} />
          {walletBalance ?? "..."} soap
        </span>
      </div>

      <div className="p-3">
        <p className="text-[11px] text-slate-500 mb-3">
          As compras saem da carteira da comunidade, não da sua. O soap da comunidade vem dos apoios
          recebidos em conteúdo publicado nela.
        </p>

        {notice && (
          <div
            role={notice.type === "error" ? "alert" : "status"}
            className={`mb-3 p-2.5 rounded-sm text-xs font-semibold flex items-center gap-2 border ${
              notice.type === "success"
                ? "bg-green-50 border-green-200 text-green-800"
                : "bg-red-50 border-red-200 text-red-800"
            }`}
          >
            {notice.type === "success" ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{notice.message}</span>
          </div>
        )}

        {status === "loading" ? (
          <LoadingState label="Carregando itens..." />
        ) : status === "error" ? (
          <ErrorState message={loadError ?? "Não foi possível carregar os itens."} onRetry={() => void load()} />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum item disponível para comunidades" hint="O catálogo é mantido pela administração." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {items.map((item) => (
              <CustomizationCard
                key={item.id}
                item={item}
                balance={walletBalance ?? 0}
                previewPhoto={community.community_photo}
                previewName={community.name}
                busy={busyId === item.id}
                onPurchase={(i) => void purchase(i)}
                onEquipToggle={(i) => void toggleEquip(i)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
