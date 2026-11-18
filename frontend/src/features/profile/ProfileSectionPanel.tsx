import React, { useState } from "react";
import { useAuthStore } from "@/features/auth/authStore";
import { saveProfileSection } from "@/services/customization";
import { errorMessage } from "@/services/errors";
import type { ProfileSection } from "@/types";

interface ProfileSectionPanelProps {
  section: ProfileSection | null | undefined;
  isOwn: boolean;
}

/**
 * The customizable profile section (unlocked in the store). Title and text are plain text:
 * React escapes them, and the server only stores them with bounded lengths.
 */
export const ProfileSectionPanel: React.FC<ProfileSectionPanelProps> = ({ section, isOwn }) => {
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(section?.title ?? "");
  const [text, setText] = useState(section?.text ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const empty = !section || (!section.title && !section.text);
  if (empty && !isOwn) return null;

  const open = () => {
    setTitle(section?.title ?? "");
    setText(section?.text ?? "");
    setError(null);
    setEditing(true);
  };

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await saveProfileSection(title, text);
      await refreshUser();
      setEditing(false);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel-classic" data-testid="profile-section">
      <div className="panel-classic-header">
        <span className="text-sm sm:text-base font-bold text-slate-800 break-words min-w-0">
          {section?.title || "Minha seção"}
        </span>
        {isOwn && !editing && (
          <button onClick={open} className="text-xs text-pink-600 font-semibold hover:underline flex-shrink-0 ml-2">
            Editar
          </button>
        )}
      </div>
      <div className="p-3">
        {editing ? (
          <form onSubmit={save} className="space-y-2">
            <label className="block">
              <span className="block mb-1 text-[11px] font-semibold text-slate-700">Título ({title.length}/40)</span>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={40}
                aria-label="Título da seção"
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500"
              />
            </label>
            <label className="block">
              <span className="block mb-1 text-[11px] font-semibold text-slate-700">Texto ({text.length}/500)</span>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                maxLength={500}
                rows={5}
                aria-label="Texto da seção"
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500"
              />
            </label>
            <p className="text-[10px] text-slate-400">Somente texto simples.</p>
            {error && (
              <p role="alert" className="text-[11px] font-semibold text-red-700">
                {error}
              </p>
            )}
            <div className="flex gap-2">
              <button disabled={busy} className="btn-pink px-3 py-1 text-xs font-bold rounded-sm disabled:opacity-60">
                {busy ? "Salvando..." : "Salvar"}
              </button>
              <button type="button" onClick={() => setEditing(false)} className="px-3 py-1 text-xs text-slate-600 hover:text-slate-900">
                Cancelar
              </button>
            </div>
          </form>
        ) : empty ? (
          <p className="text-xs text-slate-400">Escreva algo sobre você com o botão Editar.</p>
        ) : (
          <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap break-words">{section!.text}</p>
        )}
      </div>
    </div>
  );
};
