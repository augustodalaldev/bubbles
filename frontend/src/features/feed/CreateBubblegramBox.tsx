import React, { useState } from "react";
import { Bubblegram, Community, User } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { FileText, Image as ImageIcon, Send, AlertCircle, Check } from "lucide-react";

interface CreateBubblegramBoxProps {
  currentUser: User;
  communities: Community[];
  onPostCreated: (post: Bubblegram) => void;
  onDeductSoap?: (amount: number) => void;
}

export const CreateBubblegramBox: React.FC<CreateBubblegramBoxProps> = ({
  currentUser,
  communities,
  onPostCreated,
  onDeductSoap,
}) => {
  const [activeTab, setActiveTab] = useState<"text" | "photo">("text");
  const [text, setText] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [destination, setDestination] = useState<string>("profile"); // "profile" or community id
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState(false);

  const isProfile = destination === "profile";
  const cost = isProfile ? 10 : 0;
  const userSoap = currentUser.soap_balance ?? 0;
  const canAfford = userSoap >= cost;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!text.trim() && !imageUrl.trim()) {
      setError("Escreva algo ou adicione uma imagem para publicar.");
      return;
    }

    if (activeTab === "photo" && !imageUrl.trim()) {
      setError("Informe o link da foto ou imagem para a publicação.");
      return;
    }

    if (!canAfford) {
      setError(`Saldo de soap insuficiente (${userSoap} soap). São necessários ${cost} soap.`);
      return;
    }

    setLoading(true);

    setTimeout(() => {
      let selectedCommunity: Community | null = null;
      if (!isProfile) {
        selectedCommunity = communities.find((c) => c.id.toString() === destination) || null;
      }

      const newPost: Bubblegram = {
        id: Date.now(),
        user: currentUser,
        community: selectedCommunity,
        text: text.trim(),
        type: activeTab === "photo" ? "MEDIA" : "TEXT",
        media: activeTab === "photo" && imageUrl.trim() ? [
          { id: Date.now() + 1, media: imageUrl.trim(), position: 0 }
        ] : [],
        soap_count: 0,
        published_at: new Date().toISOString(),
        is_suggested: false,
        suggestion_reason: null,
        can_delete: true,
      };

      if (cost > 0 && onDeductSoap) {
        onDeductSoap(cost);
      }

      onPostCreated(newPost);
      setText("");
      setImageUrl("");
      setLoading(false);
      setSuccessNotice(true);
      setTimeout(() => setSuccessNotice(false), 3500);
    }, 400);
  };

  return (
    <div className="panel-classic mb-5">
      {/* Header */}
      <div className="panel-classic-header flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-3.5 h-3.5 text-pink-600" />
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Publicar Bolha
          </h2>
        </div>

        {/* Tab Switcher: Texto vs Foto */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-sm">
          <button
            type="button"
            onClick={() => setActiveTab("text")}
            className={`flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-sm transition-all ${
              activeTab === "text"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <FileText className="w-3 h-3" />
            Texto
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("photo")}
            className={`flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-sm transition-all ${
              activeTab === "photo"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <ImageIcon className="w-3 h-3" />
            Foto
          </button>
        </div>
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit} className="p-3">
        {error && (
          <div className="mb-2.5 p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successNotice && (
          <div className="mb-2.5 p-2 bg-green-50 border border-green-200 text-green-700 text-xs rounded-sm flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5 flex-shrink-0" />
            <span>Sua bolha foi publicada com sucesso no feed!</span>
          </div>
        )}

        {/* Text Area */}
        <div className="relative">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={2000}
            rows={3}
            placeholder={
              activeTab === "photo"
                ? "Adicione uma legenda ou descrição para sua imagem..."
                : "O que você está pensando ou criando hoje? Compartilhe com sua rede..."
            }
            className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
          />
          <div className="absolute right-2 bottom-2 text-[10px] text-slate-400 font-mono">
            {text.length}/2000
          </div>
        </div>

        {/* Photo URL Input (when photo tab active) */}
        {activeTab === "photo" && (
          <div className="mt-2">
            <div className="flex items-center gap-2">
              <input
                type="url"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="Insira o link direto da imagem (ex: https://...)"
                className="flex-1 px-2.5 py-1.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
              />
            </div>
            {imageUrl && (
              <div className="mt-2 relative w-24 h-24 rounded-sm overflow-hidden border border-slate-200 bg-slate-100">
                <img
                  src={imageUrl}
                  alt="Pré-visualização"
                  className="w-full h-full object-cover"
                  onError={() => setError("Não foi possível carregar a pré-visualização da imagem.")}
                />
              </div>
            )}
          </div>
        )}

        {/* Bottom Bar: Destination & Action */}
        <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
          
          {/* Destination Selector */}
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-600">
              Destino:
            </span>
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="px-2 py-1 text-xs bg-white border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 cursor-pointer"
            >
              <option value="profile">Meu Perfil (Mural de bolhas)</option>
              {communities.map((c) => (
                <option key={c.id} value={c.id.toString()}>
                  Comunidade: {c.name}
                </option>
              ))}
            </select>

            {/* Cost or Free Badge */}
            {isProfile ? (
              <div 
                title="Custo da publicação no mural pessoal fixo"
                className="flex items-center gap-1 px-1.5 py-0.5 bg-pink-50 border border-pink-200 rounded-sm text-[10px] font-semibold text-pink-900"
              >
                <SoapIcon size={14} />
                <span>Custo: 10 soap</span>
              </div>
            ) : (
              <span className="text-[10px] font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-sm border border-emerald-200">
                Grátis (Membro)
              </span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !canAfford}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-bold transition-all shadow-xs ${
              !canAfford
                ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                : "bg-pink-600 text-white hover:bg-pink-700 active:scale-95"
            }`}
          >
            <Send className="w-3.5 h-3.5" />
            {loading ? "Publicando..." : "Publicar"}
          </button>
        </div>
      </form>
    </div>
  );
};
