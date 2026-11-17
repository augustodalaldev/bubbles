import React, { useEffect, useState, useRef } from "react";
import { Letter, User } from "@/types";
import { listFollowing } from "@/services/users";
import { sendLetter } from "@/services/letters";
import { errorMessage } from "@/services/errors";
import { X, Send, UploadCloud, AlertCircle, Mail } from "lucide-react";

interface LetterComposeModalProps {
  currentUser: User;
  replyToLetter?: Letter | null;
  initialRecipientUsername?: string;
  onClose: () => void;
  onLetterSent: (letter: Letter) => void;
}

export const LetterComposeModal: React.FC<LetterComposeModalProps> = ({
  currentUser,
  replyToLetter,
  initialRecipientUsername,
  onClose,
  onLetterSent,
}) => {
  const [recipientUsername, setRecipientUsername] = useState(
    replyToLetter?.sender.username || initialRecipientUsername || ""
  );
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [following, setFollowing] = useState<User[]>([]);
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSizeStr, setFileSizeStr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB limit strictly observed

  const isReply = !!replyToLetter;

  // Letters can only be started with people you follow, so suggest exactly those.
  useEffect(() => {
    if (isReply) return;
    listFollowing(currentUser.username, 1)
      .then((data) => setFollowing(data.results.slice(0, 5).map((item) => item.user)))
      .catch(() => setFollowing([]));
  }, [isReply, currentUser.username]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const picked = e.target.files?.[0];
    if (!picked) return;

    if (picked.size > MAX_FILE_SIZE) {
      setError(`O anexo possui ${(picked.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setFile(picked);
    setFileName(picked.name);
    setFileSizeStr((picked.size / (1024 * 1024)).toFixed(2) + " MB");

    const reader = new FileReader();
    reader.onload = () => {
      setImageDataUrl(reader.result as string);
    };
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

    const targetUser = recipientUsername.trim().toLowerCase();
    if (!targetUser) {
      setError("Informe o destinatário da carta.");
      return;
    }
    if (targetUser === currentUser.username.toLowerCase()) {
      setError("Você não pode enviar uma carta para si mesmo.");
      return;
    }
    if (!text.trim()) {
      setError("Escreva uma mensagem para sua carta.");
      return;
    }

    setLoading(true);
    try {
      const sent = await sendLetter({
        recipientUsername: targetUser,
        text: text.trim(),
        replyToId: replyToLetter?.id ?? null,
        image: file,
      });
      onLetterSent(sent);
      onClose();
    } catch (err) {
      setError(errorMessage(err));
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="w-full max-w-lg panel-classic bg-white shadow-2xl border border-slate-300 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="panel-classic-header flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Mail className="w-4 h-4 text-pink-600" />
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
              {isReply ? `Responder Carta de ${replyToLetter.sender.name}` : "Redigir Nova Carta"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1 rounded-sm cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Reply Context Banner */}
        {isReply && (
          <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs text-slate-600">
            <span className="font-semibold text-slate-800">Em resposta à carta de: </span>
            <span className="text-pink-700 font-bold">{replyToLetter.sender.name}</span>
            <p className="text-[11px] text-slate-500 italic mt-0.5 line-clamp-1">
              "{replyToLetter.text}"
            </p>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-3.5">
          {error && (
            <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Destinatário */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Destinatário (@username) *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-mono text-slate-400">
                @
              </span>
              <input
                type="text"
                value={recipientUsername}
                disabled={isReply}
                onChange={(e) => setRecipientUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ""))}
                placeholder="nome_usuario"
                className={`w-full pl-7 pr-3 py-1.5 text-xs font-mono bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors ${
                  isReply ? "bg-slate-100 text-slate-500 cursor-not-allowed" : ""
                }`}
              />
            </div>

            {/* Quick friend suggestions */}
            {!isReply && following.length > 0 && (
              <div className="mt-1.5 flex items-center gap-1 overflow-x-auto pb-1 text-[11px]">
                <span className="text-slate-400 text-[10px] mr-1">Quem você segue:</span>
                {following.map((friend) => (
                  <button
                    key={friend.id}
                    type="button"
                    onClick={() => setRecipientUsername(friend.username)}
                    className="px-1.5 py-0.5 bg-slate-100 hover:bg-pink-50 hover:text-pink-700 border border-slate-200 rounded-sm text-slate-600 transition-colors cursor-pointer"
                  >
                    {friend.name.split(" ")[0]}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Mensagem da Carta */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Conteúdo da Carta *
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={5000}
              rows={5}
              placeholder="Escreva sua correspondência com tranquilidade. As cartas são mensagens privadas e perenes..."
              className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
            />
            <div className="text-right text-[10px] text-slate-400 font-mono">
              {text.length}/5000
            </div>
          </div>

          {/* Anexo de Imagem (Até 10 MB) */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Anexar Foto ou Mídia (Opcional, até 10 MB)
            </label>
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
                className="border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 p-2.5 text-center cursor-pointer rounded-sm transition-colors"
              >
                <UploadCloud className="w-5 h-5 text-slate-400 mx-auto mb-1" />
                <span className="text-xs font-semibold text-slate-700 block">
                  Clique para anexar uma foto à carta
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  Suporte a imagens de até <strong>10 MB</strong> (PNG, JPEG, WebP, GIF)
                </span>
              </div>
            ) : (
              <div className="border border-slate-200 rounded-sm p-2 bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <img
                    src={imageDataUrl}
                    alt="Anexo"
                    className="w-12 h-12 object-cover rounded-sm border border-slate-300"
                  />
                  <div>
                    <span className="text-xs font-bold text-slate-800 block truncate max-w-[220px]">
                      {fileName}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {fileSizeStr} • Limite: 10 MB
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="text-slate-400 hover:text-red-600 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Footer Action */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[10px] text-slate-400">
              * Cartas são correspondências privadas diretas.
            </span>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 rounded-sm cursor-pointer"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex items-center gap-1.5 px-4 py-1.5 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs active:scale-95 transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{loading ? "Enviando..." : "Enviar Carta"}</span>
              </button>
            </div>
          </div>
        </form>

      </div>
    </div>
  );
};
