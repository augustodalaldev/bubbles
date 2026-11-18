import React, { useState, useRef } from "react";
import { Bubblegram, Bubblepop } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { useAuthStore } from "@/features/auth/authStore";
import { createBubblegram, createBubblepop } from "@/services/content";
import { errorMessage } from "@/services/errors";
import { Plus, X, Image as ImageIcon, FileText, UploadCloud, AlertCircle, Check, Clock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface CreateBubblePopupProps {
  onPostCreated: (post: Bubblegram) => void;
  /** Called when a bubblepop (temporary post) was created from the same panel. */
  onPopCreated?: (pop: Bubblepop) => void;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // mirrors the server limit, only to fail fast

export const CreateBubblePopup: React.FC<CreateBubblePopupProps> = ({ onPostCreated, onPopCreated }) => {
  const userSoap = useAuthStore((s) => s.user?.soap_balance ?? 0);
  const economy = useAuthStore((s) => s.economy);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"text" | "photo" | "pop">("text");
  const [hours, setHours] = useState(24);
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSizeStr, setFileSizeStr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const minHours = economy?.bubblepop_min_hours ?? 1;
  const maxHours = economy?.bubblepop_max_hours ?? 48;
  // Display only: the server computes and charges the real cost.
  const cost =
    activeTab === "pop"
      ? economy
        ? Math.ceil(hours / economy.bubblepop_hours_per_soap)
        : undefined
      : economy?.bubblegram_profile_cost;
  const COST = cost ?? "...";
  const canAfford = cost === undefined || userSoap >= cost;
  const isPop = activeTab === "pop";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const picked = e.target.files?.[0];
    if (!picked) return;

    if (picked.size > MAX_FILE_SIZE) {
      setError(`O arquivo possui ${(picked.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setFile(picked);
    setFileName(picked.name);
    setFileSizeStr((picked.size / (1024 * 1024)).toFixed(2) + " MB");
    const reader = new FileReader();
    reader.onload = () => setImageDataUrl(reader.result as string);
    reader.readAsDataURL(picked);
  };

  const handleRemoveImage = () => {
    setFile(null);
    setImageDataUrl(null);
    setFileName(null);
    setFileSizeStr(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (isPop) {
      if (!file) {
        setError("Escolha uma imagem de até 10 MB para o bubblepop.");
        return;
      }
      setLoading(true);
      try {
        const pop = await createBubblepop({
          image: file,
          durationHours: Math.min(Math.max(hours, minHours), maxHours),
          description: text.trim().slice(0, 500),
        });
        await refreshUser();
        onPopCreated?.(pop);
        setText("");
        handleRemoveImage();
        setSuccessNotice(true);
        window.setTimeout(() => {
          setSuccessNotice(false);
          setIsOpen(false);
        }, 1000);
      } catch (err) {
        setError(errorMessage(err));
      } finally {
        setLoading(false);
      }
      return;
    }

    if (activeTab === "photo" && !file) {
      setError("Selecione uma imagem de até 10 MB para publicar na aba Foto.");
      return;
    }
    if (!text.trim() && !file) {
      setError("Escreva algo ou anexe uma imagem para publicar sua bolha.");
      return;
    }

    setLoading(true);
    try {
      const created = await createBubblegram({
        text: text.trim(),
        files: activeTab === "photo" && file ? [file] : [],
      });
      await refreshUser();
      onPostCreated(created);
      setText("");
      handleRemoveImage();
      setSuccessNotice(true);
      window.setTimeout(() => {
        setSuccessNotice(false);
        setIsOpen(false);
      }, 1000);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button (Fixed Bottom-Right) */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          title={isOpen ? "Fechar painel de publicação" : "Publicar uma bolha ou um bubblepop"}
          className={`w-13 h-13 rounded-full flex items-center justify-center text-white shadow-xl transition-all duration-200 cursor-pointer ${
            isOpen
              ? "bg-slate-800 hover:bg-slate-900 rotate-45"
              : "bg-pink-600 hover:bg-pink-700 hover:scale-105 active:scale-95 ring-4 ring-pink-100/90"
          }`}
          style={{ width: "52px", height: "52px" }}
        >
          <Plus className="w-6 h-6 stroke-[2.5]" />
        </button>
      </div>

      {/* Floating Popup Form (Positioned directly above the button in bottom-right) */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Click-outside backdrop to easily dismiss */}
            <div
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40 bg-black/10 sm:bg-transparent"
            />

            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
              style={{ transformOrigin: "bottom right" }}
              className="fixed bottom-20 right-6 z-50 w-[380px] sm:w-[420px] max-w-[calc(100vw-2.5rem)] max-h-[calc(100vh-6rem)] overflow-y-auto panel-classic bg-white shadow-2xl border border-slate-300"
            >
            {/* Header */}
            <div className="panel-classic-header flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Plus className="w-3.5 h-3.5 text-pink-600" />
                <h3 className="text-xs font-bold text-slate-900">
                  Publicar
                </h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-sm"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Soap Cost and Policy Note */}
            <div className="px-3 py-2 bg-pink-50/70 border-b border-pink-100 flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5 text-pink-900 font-semibold">
                <SoapIcon size={14} />
                <span>Custo: {COST} soap</span>
              </div>
              <span className="text-[10px] text-slate-500 font-medium">
                Saldo: {userSoap} soap
              </span>
            </div>

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
                  <span>{isPop ? "Bubblepop publicado com sucesso!" : "Bolha publicada com sucesso!"}</span>
                </div>
              )}

              {/* Tabs: Texto, Foto (bubblegram permanente) e Bubblepop (temporário) */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-sm mb-2.5">
                <button
                  type="button"
                  onClick={() => setActiveTab("text")}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeTab === "text"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  Texto
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("photo")}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeTab === "photo"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                  Foto
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("pop")}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeTab === "pop"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Clock className="w-3.5 h-3.5" />
                  Bubblepop
                </button>
              </div>

              {/* Text Input */}
              <div className="relative mb-2.5">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  maxLength={isPop ? 500 : 2000}
                  rows={activeTab === "text" ? 4 : 2}
                  placeholder={
                    isPop
                      ? "Descrição do bubblepop (opcional)..."
                      : activeTab === "photo"
                        ? "Escreva uma legenda para sua foto..."
                        : "O que você gostaria de fixar no seu mural de bolhas hoje?"
                  }
                  className="w-full p-2 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
                />
                <div className="text-right text-[10px] text-slate-400 font-mono">
                  {text.length}/{isPop ? 500 : 2000}
                </div>
              </div>

              {/* Photo Upload Area (when photo tab is active) */}
              {activeTab !== "text" && (
                <div className="mb-3">
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  {!imageDataUrl ? (
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 hover:bg-pink-50/30 p-3 text-center cursor-pointer rounded-sm transition-colors"
                    >
                      <UploadCloud className="w-6 h-6 text-slate-400 mx-auto mb-1" />
                      <span className="text-xs font-semibold text-slate-700 block">
                        Clique para enviar uma foto
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">
                        Suporte a arquivos de até <strong>10 MB</strong> (PNG, JPEG, WebP, GIF)
                      </span>
                    </div>
                  ) : (
                    <div className="relative border border-slate-200 rounded-sm p-1.5 bg-slate-50 flex items-center gap-2.5">
                      <img
                        src={imageDataUrl}
                        alt="Preview"
                        className="w-14 h-14 object-cover rounded-sm border border-slate-200 flex-shrink-0"
                      />
                      <div className="min-w-0 flex-1">
                        <span className="text-xs font-bold text-slate-800 block truncate">
                          {fileName}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono block">
                          {fileSizeStr} • Limite: 10 MB
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={handleRemoveImage}
                        title="Remover imagem"
                        className="text-slate-400 hover:text-red-600 p-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {isPop && (
                <div className="mb-3">
                  <label htmlFor="pop-hours" className="block text-xs font-semibold text-slate-700 mb-1">
                    Duração: {hours} h (some depois disso)
                  </label>
                  <input
                    id="pop-hours"
                    type="range"
                    min={minHours}
                    max={maxHours}
                    value={hours}
                    onChange={(e) => setHours(Number(e.target.value))}
                    className="w-full accent-pink-600"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>{minHours} h</span>
                    <span>{maxHours} h</span>
                  </div>
                </div>
              )}

              {/* Notice about Community posts */}
              <p className="text-[10px] text-slate-400 mb-3 leading-tight">
                * Publicações em comunidades devem ser feitas diretamente na página da comunidade.
              </p>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 rounded-sm"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !canAfford}
                  className={`px-4 py-1.5 rounded-sm text-xs font-bold transition-all shadow-xs ${
                    !canAfford
                      ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                      : "bg-pink-600 text-white hover:bg-pink-700 active:scale-95"
                  }`}
                >
                  {loading ? "Publicando..." : isPop ? "Publicar Bubblepop" : "Publicar Bolha"}
                </button>
              </div>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
    </>
  );
};
