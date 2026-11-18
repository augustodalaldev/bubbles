import React, { useState, useRef } from "react";
import { Community } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { useAuthStore } from "@/features/auth/authStore";
import { createCommunity } from "@/services/communities";
import { errorMessage, fieldErrors } from "@/services/errors";
import { X, UploadCloud, Users, AlertCircle } from "lucide-react";

interface CreateCommunityModalProps {
  onClose: () => void;
  onCommunityCreated: (community: Community) => void;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // mirrors the server limit, only to fail fast

export const CreateCommunityModal: React.FC<CreateCommunityModalProps> = ({
  onClose,
  onCommunityCreated,
}) => {
  const economy = useAuthStore((s) => s.economy);
  const balance = useAuthStore((s) => s.user?.soap_balance ?? 0);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const [commname, setCommname] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [guidelines, setGuidelines] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoDataUrl, setPhotoDataUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSizeStr, setFileSizeStr] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const cost = economy?.founding_cost;
  const cannotAfford = cost !== undefined && balance < cost;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_FILE_SIZE) {
      setError(`O arquivo possui ${(file.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setPhoto(file);
    setFileName(file.name);
    setFileSizeStr((file.size / (1024 * 1024)).toFixed(2) + " MB");
    const reader = new FileReader();
    reader.onload = () => setPhotoDataUrl(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setErrors({});

    const cleanCommname = commname.trim().toLowerCase();
    if (!cleanCommname || !name.trim()) {
      setError("Informe o identificador e o nome da comunidade.");
      return;
    }

    setLoading(true);
    try {
      const community = await createCommunity({
        commname: cleanCommname,
        name: name.trim(),
        description: description.trim(),
        guidelines: guidelines.trim(),
        communityPhoto: photo,
      });
      await refreshUser();
      onCommunityCreated(community);
      onClose();
    } catch (err) {
      setErrors(fieldErrors(err));
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
            <Users className="w-4 h-4 text-pink-600" />
            <h2 className="text-xs font-bold text-slate-900">
              Criar nova comunidade
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1 rounded-sm"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="px-4 py-2 bg-pink-50/70 border-b border-pink-100 flex items-center justify-between text-[11px]">
          <span className="flex items-center gap-1.5 text-pink-900 font-semibold">
            <SoapIcon size={14} />
            Custo de fundação: {cost ?? "..."} soap (vai para a carteira da comunidade)
          </span>
          <span className={cannotAfford ? "text-red-700 font-semibold" : "text-slate-500"}>
            Saldo: {balance} soap
          </span>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3.5">
          {cannotAfford && (
            <div role="alert" className="p-2.5 bg-amber-50 border border-amber-300 text-amber-900 text-xs rounded-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-amber-600" />
              <span>
                Saldo insuficiente: você tem {balance} soap e a fundação custa {cost} soap.
              </span>
            </div>
          )}
          {error && (
            <div role="alert" className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Nome da Comunidade */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Nome da Comunidade *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={60}
              placeholder="Ex: Entusiastas de Vidro Líquido"
              className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
            />
              {errors.name && <p className="mt-0.5 text-[11px] text-red-700">{errors.name}</p>}
          </div>

          {/* Identificador commname */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Identificador (@commname) *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-mono text-slate-400">
                @
              </span>
              <input
                type="text"
                value={commname}
                onChange={(e) => setCommname(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ""))}
                maxLength={21}
                placeholder="vidro_liquido"
                className="w-full pl-7 pr-3 py-1.5 text-xs font-mono bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
              />
              {errors.commname && <p className="mt-0.5 text-[11px] text-red-700">{errors.commname}</p>}
            </div>
            <span className="text-[10px] text-slate-400 mt-0.5 block">
              De 3 a 21 caracteres em minúsculo, números e sublinhados.
            </span>
          </div>

          {/* Descrição */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Descrição
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
              rows={2}
              placeholder="Explique o propósito deste espaço e o que os membros irão encontrar..."
              className="w-full p-2.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none"
            />
            <div className="text-right text-[10px] text-slate-400 font-mono">
              {description.length}/500
            </div>
          </div>

          {/* Diretrizes */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Diretrizes e Regras de Convivência
            </label>
            <textarea
              value={guidelines}
              onChange={(e) => setGuidelines(e.target.value)}
              maxLength={2000}
              rows={3}
              placeholder="1. Tratar todos com respeito mútuo.&#10;2. Manter publicações pertinentes ao tema.&#10;3. Apoiar criadores com soap..."
              className="w-full p-2.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none"
            />
          </div>

          {/* Upload de Imagem de até 10MB */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Foto de Apresentação (Até 10 MB)
            </label>
            <input
              type="file"
              ref={fileInputRef}
              accept="image/png,image/jpeg,image/webp,image/gif"
              onChange={handleFileChange}
              className="hidden"
            />

            {!photoDataUrl ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 p-3 text-center cursor-pointer rounded-sm transition-colors"
              >
                <UploadCloud className="w-5 h-5 text-slate-400 mx-auto mb-1" />
                <span className="text-xs font-semibold text-slate-700 block">
                  Escolher foto da comunidade
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  Suporte a imagens de até <strong>10 MB</strong> (PNG, JPEG, WebP, GIF)
                </span>
              </div>
            ) : (
              <div className="border border-slate-200 rounded-sm p-2 bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <img
                    src={photoDataUrl}
                    alt="Preview"
                    className="w-10 h-10 rounded-full object-cover border border-slate-300"
                  />
                  <div>
                    <span className="text-xs font-bold text-slate-800 block truncate max-w-[220px]">
                      {fileName}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {fileSizeStr}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setPhoto(null);
                    setPhoto(null);
                    setPhotoDataUrl(null);
                    setFileName(null);
                    setFileSizeStr(null);
                  }}
                  className="text-slate-400 hover:text-red-600 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 rounded-sm"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || cannotAfford}
              className="px-4 py-1.5 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs active:scale-95 transition-all"
            >
              {loading ? "Criando..." : "Criar Comunidade"}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
