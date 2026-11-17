import React, { useRef, useState } from "react";
import { Bubblepop } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { useAuthStore } from "@/features/auth/authStore";
import { createBubblepop } from "@/services/content";
import { errorMessage } from "@/services/errors";
import { AlertCircle, UploadCloud, X } from "lucide-react";

interface CreateBubblepopModalProps {
  onClose: () => void;
  onCreated: (pop: Bubblepop) => void;
}

export const CreateBubblepopModal: React.FC<CreateBubblepopModalProps> = ({ onClose, onCreated }) => {
  const economy = useAuthStore((s) => s.economy);
  const balance = useAuthStore((s) => s.user?.soap_balance ?? 0);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const minHours = economy?.bubblepop_min_hours ?? 1;
  const maxHours = economy?.bubblepop_max_hours ?? 48;
  const [hours, setHours] = useState(Math.min(24, maxHours));
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Display only: the server computes and charges the real cost.
  const cost = economy ? Math.ceil(hours / economy.bubblepop_hours_per_soap) : null;

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0] ?? null;
    setFile(picked);
    setPreview(picked ? URL.createObjectURL(picked) : null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Escolha uma imagem para o bubblepop.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const pop = await createBubblepop({ image: file, durationHours: hours, description: description.trim() });
      await refreshUser();
      onCreated(pop);
      onClose();
    } catch (err) {
      setError(errorMessage(err));
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Novo bubblepop"
    >
      <form
        onSubmit={handleSubmit}
        onClick={(e) => e.stopPropagation()}
        className="panel-classic bg-white w-full max-w-sm shadow-2xl"
      >
        <div className="panel-classic-header flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-900">Novo bubblepop</h3>
          <button type="button" onClick={onClose} aria-label="Fechar" className="text-slate-400 hover:text-slate-700 p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="px-3 py-2 bg-pink-50/70 border-b border-pink-100 flex items-center justify-between text-[11px]">
          <span className="flex items-center gap-1.5 text-pink-900 font-semibold">
            <SoapIcon size={14} />
            Custo: {cost ?? "..."} soap
          </span>
          <span className="text-slate-500">Saldo: {balance} soap</span>
        </div>

        <div className="p-3 space-y-3">
          {error && (
            <div role="alert" className="p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <input ref={inputRef} type="file" accept="image/png,image/jpeg,image/webp,image/gif" onChange={handleFile} className="hidden" />
          {preview ? (
            <img src={preview} alt="Prévia" className="w-full max-h-48 object-cover rounded-sm border border-slate-200" />
          ) : (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="w-full border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 p-4 text-center rounded-sm"
            >
              <UploadCloud className="w-6 h-6 text-slate-400 mx-auto mb-1" />
              <span className="text-xs font-semibold text-slate-700 block">Escolher imagem</span>
              <span className="text-[10px] text-slate-400">PNG, JPEG, WebP ou GIF, até 10 MB</span>
            </button>
          )}
          {preview && (
            <button type="button" onClick={() => inputRef.current?.click()} className="text-[11px] text-pink-600 hover:underline">
              Trocar imagem
            </button>
          )}

          <div>
            <label htmlFor="pop-hours" className="block text-xs font-semibold text-slate-700 mb-1">
              Duração: {hours} h
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

          <div>
            <label htmlFor="pop-desc" className="block text-xs font-semibold text-slate-700 mb-1">
              Descrição (opcional)
            </label>
            <textarea
              id="pop-desc"
              rows={2}
              maxLength={500}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 text-xs bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white resize-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-3 border-t border-slate-100">
          <button type="button" onClick={onClose} className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900">
            Cancelar
          </button>
          <button type="submit" disabled={loading || !file} className="px-4 py-1.5 rounded-sm text-xs font-bold bg-pink-600 text-white hover:bg-pink-700 disabled:opacity-50">
            {loading ? "Publicando..." : "Publicar bubblepop"}
          </button>
        </div>
      </form>
    </div>
  );
};
