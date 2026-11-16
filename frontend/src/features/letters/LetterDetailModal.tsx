import React, { useEffect } from "react";
import { Letter, User } from "@/types";
import { X, Reply, Clock, CheckCheck, Mail } from "lucide-react";

interface LetterDetailModalProps {
  letter: Letter;
  currentUser: User;
  onClose: () => void;
  onReply: (letter: Letter) => void;
  onMarkAsRead?: (letterId: number) => void;
}

export const LetterDetailModal: React.FC<LetterDetailModalProps> = ({
  letter,
  currentUser,
  onClose,
  onReply,
  onMarkAsRead,
}) => {
  const isSender = letter.sender.id === currentUser.id;
  const otherPerson = isSender ? letter.recipient : letter.sender;

  // Mark letter as read on open if recipient is current user and letter is unread
  useEffect(() => {
    if (!isSender && !letter.is_read && onMarkAsRead) {
      onMarkAsRead(letter.id);
    }
  }, [isSender, letter.id, letter.is_read, onMarkAsRead]);

  // Format precise date and time
  const formatDateTime = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="w-full max-w-xl panel-classic bg-white shadow-2xl border border-slate-300 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="panel-classic-header flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-pink-600" />
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
              {isSender ? `Carta enviada para ${otherPerson.name}` : `Carta de ${otherPerson.name}`}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1 rounded-sm cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Sender / Recipient Info Bar */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <img
              src={otherPerson.profile_photo || ""}
              alt={otherPerson.name}
              className="w-10 h-10 rounded-full object-cover border border-slate-200"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-900">
                  {otherPerson.name}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">
                  @{otherPerson.username}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {formatDateTime(letter.sent_at)}
                </span>
              </div>
            </div>
          </div>

          {/* Read Receipt */}
          <div className="text-right">
            {letter.read_at ? (
              <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-sm border border-emerald-200">
                <CheckCheck className="w-3 h-3 text-emerald-600" />
                Lida
              </span>
            ) : (
              <span className="inline-flex items-center text-[10px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-sm border border-amber-200">
                Não lida
              </span>
            )}
          </div>
        </div>

        {/* Letter Body */}
        <div className="p-5 space-y-4">
          <div className="text-xs text-slate-800 leading-relaxed whitespace-pre-line font-sans">
            {letter.text}
          </div>

          {/* Attached Image if present */}
          {letter.image && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide block mb-2">
                Anexo da Carta
              </span>
              <div className="rounded-sm overflow-hidden border border-slate-200 bg-slate-900">
                <img
                  src={letter.image}
                  alt="Anexo da carta"
                  className="w-full max-h-[440px] object-contain"
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[10px] text-slate-400">
            Correspondência privada • {formatDateTime(letter.sent_at)}
          </span>

          <div className="flex items-center gap-2">
            {!isSender && (
              <button
                onClick={() => {
                  onClose();
                  onReply(letter);
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs transition-all active:scale-95 cursor-pointer"
              >
                <Reply className="w-3.5 h-3.5" />
                <span>Responder Carta</span>
              </button>
            )}

            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 rounded-sm cursor-pointer"
            >
              Fechar
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
