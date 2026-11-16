import React, { useState, useRef } from "react";
import { Bubblegram, User } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { Plus, X, Image as ImageIcon, FileText, UploadCloud, AlertCircle, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface CreateBubblePopupProps {
  currentUser: User;
  onPostCreated: (post: Bubblegram) => void;
  onDeductSoap?: (amount: number) => void;
}

export const CreateBubblePopup: React.FC<CreateBubblePopupProps> = ({
  currentUser,
  onPostCreated,
  onDeductSoap,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"text" | "photo">("text");
  const [text, setText] = useState("");
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSizeStr, setFileSizeStr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const COST = 10;
  const userSoap = currentUser.soap_balance ?? 0;
  const canAfford = userSoap >= COST;
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 Megabytes strictly supported

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate 10MB file limit
    if (file.size > MAX_FILE_SIZE) {
      setError(`O arquivo possui ${(file.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite máximo permitido de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setFileName(file.name);
    setFileSizeStr((file.size / (1024 * 1024)).toFixed(2) + " MB");

    const reader = new FileReader();
    reader.onload = () => {
      setImageDataUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setImageDataUrl(null);
    setFileName(null);
    setFileSizeStr(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!text.trim() && !imageDataUrl) {
      setError("Escreva algo ou anexe uma imagem para publicar sua bolha.");
      return;
    }

    if (activeTab === "photo" && !imageDataUrl) {
      setError("Selecione uma imagem de até 10 MB para publicar na aba Foto.");
      return;
    }

    if (!canAfford) {
      setError(`Saldo insuficiente (${userSoap} soap). São necessários 10 soap para fixar no mural.`);
      return;
    }

    setLoading(true);

    setTimeout(() => {
      const newPost: Bubblegram = {
        id: Date.now(),
        user: currentUser,
        community: null, // Posts from feed are strictly for user's profile mural
        text: text.trim(),
        type: activeTab === "photo" && imageDataUrl ? "MEDIA" : "TEXT",
        media: imageDataUrl ? [
          { id: Date.now() + 1, media: imageDataUrl, position: 0 }
        ] : [],
        soap_count: 0,
        published_at: new Date().toISOString(),
        is_suggested: false,
        suggestion_reason: null,
        can_delete: true,
      };

      if (onDeductSoap) {
        onDeductSoap(COST);
      }

      onPostCreated(newPost);
      setText("");
      handleRemoveImage();
      setLoading(false);
      setSuccessNotice(true);
      setTimeout(() => {
        setSuccessNotice(false);
        setIsOpen(false);
      }, 1000);
    }, 400);
  };

  return (
    <>
      {/* Floating Action Button (Fixed Bottom-Left) */}
      <div className="fixed bottom-6 left-6 z-40">
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          title={isOpen ? "Fechar painel de publicação" : "Publicar nova bolha no mural"}
          className={`w-13 h-13 rounded-full flex items-center justify-center text-white shadow-lg transition-all duration-200 ${
            isOpen
              ? "bg-slate-700 hover:bg-slate-800 rotate-45"
              : "bg-pink-600 hover:bg-pink-700 hover:scale-105 active:scale-95 ring-4 ring-pink-100"
          }`}
          style={{ width: "52px", height: "52px" }}
        >
          <Plus className="w-6 h-6 stroke-[2.5]" />
        </button>
      </div>

      {/* Floating Popup Form (Positioned above the button in bottom-left) */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 15, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 15, scale: 0.95 }}
            transition={{ duration: 0.18 }}
            className="fixed bottom-22 left-6 z-50 w-[380px] sm:w-[420px] max-w-[calc(100vw-3rem)] panel-classic bg-white shadow-2xl border border-slate-300"
          >
            {/* Header */}
            <div className="panel-classic-header flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Plus className="w-3.5 h-3.5 text-pink-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                  Publicar no Mural
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
                  <span>Bolha publicada com sucesso!</span>
                </div>
              )}

              {/* Tabs: Texto vs Foto */}
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
                  Foto (Até 10 MB)
                </button>
              </div>

              {/* Text Input */}
              <div className="relative mb-2.5">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  maxLength={2000}
                  rows={activeTab === "photo" ? 2 : 4}
                  placeholder={
                    activeTab === "photo"
                      ? "Escreva uma legenda para sua foto..."
                      : "O que você gostaria de fixar no seu mural de bolhas hoje?"
                  }
                  className="w-full p-2 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
                />
                <div className="text-right text-[10px] text-slate-400 font-mono">
                  {text.length}/2000
                </div>
              </div>

              {/* Photo Upload Area (when photo tab is active) */}
              {activeTab === "photo" && (
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
                  {loading ? "Publicando..." : "Publicar Bolha"}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
