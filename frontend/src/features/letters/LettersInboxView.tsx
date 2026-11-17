import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Letter, User } from "@/types";
import { Avatar } from "@/components/Avatar";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { errorMessage } from "@/services/errors";
import { listInbox, listSent, openLetter } from "@/services/letters";
import { listFollowing } from "@/services/users";
import { LetterComposeModal } from "./LetterComposeModal";
import { LetterDetailModal } from "./LetterDetailModal";
import { 
  Mail, 
  Send, 
  Inbox, 
  Plus, 
  Search, 
  CheckCheck, 
  Image as ImageIcon, 
  Compass, 
  User as UserIcon, 
  Store,
  Layers
} from "lucide-react";

interface LettersInboxViewProps {
  onNavigateToView?: (view: string) => void;
  onNavigateToProfile?: () => void;
  /** Opens the composer addressed to this username (used by the profile "Carta" button). */
  composeTo?: string | null;
}

type Box = {
  letters: Letter[];
  next: number | null;
  status: "loading" | "ready" | "error";
  error: string | null;
};
const emptyBox: Box = { letters: [], next: null, status: "loading", error: null };

export const LettersInboxView: React.FC<LettersInboxViewProps> = ({
  onNavigateToView,
  onNavigateToProfile,
  composeTo,
}) => {
  const currentUser = useAuthStore((s) => s.user)!;
  const [inbox, setInbox] = useState<Box>(emptyBox);
  const [sent, setSent] = useState<Box>(emptyBox);
  const [following, setFollowing] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState<"inbox" | "sent">("inbox");
  const [activeFilter, setActiveFilter] = useState<"all" | "unread">("all");
  const [searchTerm, setSearchTerm] = useState("");

  const [selectedLetter, setSelectedLetter] = useState<Letter | null>(null);
  const [openError, setOpenError] = useState<string | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [replyToLetter, setReplyToLetter] = useState<Letter | null>(null);
  const [initialRecipient, setInitialRecipient] = useState<string>("");

  const loadBox = useCallback(async (which: "inbox" | "sent", page: number, reset: boolean) => {
    const set = which === "inbox" ? setInbox : setSent;
    if (reset) set((prev) => ({ ...prev, status: "loading", error: null }));
    try {
      const data = await (which === "inbox" ? listInbox(page) : listSent(page));
      set((prev) => ({
        letters: reset ? data.results : [...prev.letters, ...data.results],
        next: data.next ? page + 1 : null,
        status: "ready",
        error: null,
      }));
    } catch (err) {
      set((prev) => ({ ...prev, status: reset ? "error" : prev.status, error: errorMessage(err) }));
    }
  }, []);

  useEffect(() => {
    void loadBox("inbox", 1, true);
    void loadBox("sent", 1, true);
    listFollowing(currentUser.username, 1)
      .then((data) => setFollowing(data.results.slice(0, 4).map((item) => item.user)))
      .catch(() => setFollowing([]));
  }, [loadBox, currentUser.username]);

  useEffect(() => {
    if (composeTo) {
      setReplyToLetter(null);
      setInitialRecipient(composeTo);
      setIsComposeOpen(true);
    }
  }, [composeTo]);

  const unreadCount = inbox.letters.filter((l) => !l.is_read).length;

  // Opening as the recipient marks the letter as read on the server.
  const handleOpen = async (letter: Letter) => {
    setSelectedLetter(letter);
    setOpenError(null);
    if (letter.recipient.id === currentUser.id && !letter.is_read) {
      try {
        const opened = await openLetter(letter.id);
        setInbox((prev) => ({ ...prev, letters: prev.letters.map((l) => (l.id === opened.id ? opened : l)) }));
        setSelectedLetter(opened);
      } catch (err) {
        setOpenError(errorMessage(err));
      }
    }
  };

  const handleLetterSent = (letter: Letter) => {
    setSent((prev) => ({ ...prev, letters: [letter, ...prev.letters] }));
  };

  const box = activeTab === "inbox" ? inbox : sent;

  const filteredLetters = useMemo(() => {
    let list = box.letters;
    if (activeTab === "inbox" && activeFilter === "unread") list = list.filter((l) => !l.is_read);
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      list = list.filter((l) => {
        const other = activeTab === "inbox" ? l.sender : l.recipient;
        return (
          other.name.toLowerCase().includes(term) ||
          other.username.toLowerCase().includes(term) ||
          l.text.toLowerCase().includes(term)
        );
      });
    }
    return list;
  }, [box.letters, activeTab, activeFilter, searchTerm]);

  const formatTime = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 h-[calc(100vh-3.5rem)] overflow-hidden">
      
      {/* 3-Column Classic Grid (Left 3 cols, Center 6 cols, Right 3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start h-full">
        
        {/* Left Column (3 Cols) - Static Sidebar */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Compose Primary Action Button */}
          <button
            onClick={() => {
              setReplyToLetter(null);
              setInitialRecipient("");
              setIsComposeOpen(true);
            }}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-pink-600 hover:bg-pink-700 text-white text-xs font-bold rounded-sm shadow-xs transition-all cursor-pointer active:scale-95"
          >
            <Plus className="w-4 h-4 stroke-[2.5]" />
            <span>Escrever nova carta</span>
          </button>

          {/* Mailbox Status Box */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">
                Pastas de correspondência
              </span>
            </div>
            <div className="p-1 text-xs">
              
              <button
                onClick={() => {
                  setActiveTab("inbox");
                  setActiveFilter("all");
                }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-sm transition-colors cursor-pointer text-left ${
                  activeTab === "inbox"
                    ? "bg-pink-50 text-pink-700 font-bold"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Inbox className="w-4 h-4 text-pink-600" />
                  <span>Recebidas</span>
                </div>
                {unreadCount > 0 ? (
                  <span className="px-1.5 py-0.2 bg-pink-600 text-white text-[10px] font-bold rounded-sm">
                    {unreadCount} não lida{unreadCount > 1 ? "s" : ""}
                  </span>
                ) : (
                  <span className="text-slate-400 font-mono text-[11px]">
                    {inbox.letters.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => {
                  setActiveTab("sent");
                  setActiveFilter("all");
                }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-sm transition-colors cursor-pointer text-left ${
                  activeTab === "sent"
                    ? "bg-pink-50 text-pink-700 font-bold"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Send className="w-4 h-4 text-slate-400" />
                  <span>Enviadas</span>
                </div>
                <span className="text-slate-400 font-mono text-[11px]">
                  {sent.letters.length}
                </span>
              </button>

            </div>
          </div>

          {/* Quick Navigation */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">
                Navegação
              </span>
            </div>
            <div className="p-1 text-xs">
              <button
                onClick={() => onNavigateToView?.("feed")}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <Compass className="w-4 h-4 text-slate-400" />
                <span>Início (feed)</span>
              </button>
              <button
                onClick={onNavigateToProfile}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <UserIcon className="w-4 h-4 text-slate-400" />
                <span>Meu perfil</span>
              </button>
              <button
                onClick={() => onNavigateToView?.("communities")}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <Layers className="w-4 h-4 text-slate-400" />
                <span>Comunidades</span>
              </button>
              <button
                onClick={() => onNavigateToView?.("store")}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left cursor-pointer"
              >
                <Store className="w-4 h-4 text-slate-400" />
                <span>Loja de soap</span>
              </button>
            </div>
          </div>

        </div>

        {/* Center Lane (6 Cols) - THE ONLY SCROLLABLE AREA */}
        <div className="lg:col-span-6 min-w-0 h-full overflow-y-auto pr-1.5 scrollbar-thin">
          
          {/* Top Mailbox Header Card */}
          <div className="panel-classic mb-4">
            <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4 text-pink-600" />
                  <h1 className="text-sm font-bold text-slate-900 tracking-tight">
                    Caixa Postal de Cartas
                  </h1>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Mensagens diretas e correspondências particulares entre usuários.
                </p>
              </div>

              {/* Unread pill */}
              {unreadCount > 0 && (
                <span className="px-2.5 py-1 bg-pink-100 border border-pink-300 text-pink-900 text-xs font-bold rounded-sm self-start sm:self-auto">
                  {unreadCount} nova{unreadCount > 1 ? "s" : ""}
                </span>
              )}
            </div>

            {/* Filter and Search Bar */}
            <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
              
              {/* Tab Switcher & Sub-filter */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => {
                    setActiveTab("inbox");
                    setActiveFilter("all");
                  }}
                  className={`px-3 py-1 text-xs font-bold rounded-sm transition-all ${
                    activeTab === "inbox" && activeFilter === "all"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  Recebidas ({inbox.letters.length})
                </button>

                {activeTab === "inbox" && unreadCount > 0 && (
                  <button
                    onClick={() => setActiveFilter(activeFilter === "unread" ? "all" : "unread")}
                    className={`px-2.5 py-1 text-xs font-bold rounded-sm transition-all ${
                      activeFilter === "unread"
                        ? "bg-pink-600 text-white shadow-xs"
                        : "bg-pink-50 border border-pink-200 text-pink-700 hover:bg-pink-100"
                    }`}
                  >
                    Não lidas ({unreadCount})
                  </button>
                )}

                <button
                  onClick={() => {
                    setActiveTab("sent");
                    setActiveFilter("all");
                  }}
                  className={`px-3 py-1 text-xs font-bold rounded-sm transition-all ${
                    activeTab === "sent"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  Enviadas ({sent.letters.length})
                </button>
              </div>

              {/* Search Bar */}
              <div className="relative w-full sm:w-56">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Buscar cartas..."
                  className="w-full pl-8 pr-3 py-1 text-xs bg-white border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 text-slate-800 placeholder-slate-400"
                />
              </div>

            </div>
          </div>

          {/* Letters Stream */}
          <div className="space-y-3">
            {box.status === "loading" ? (
              <LoadingState label="Carregando cartas..." />
            ) : box.status === "error" ? (
              <ErrorState message={box.error ?? "Não foi possível carregar as cartas."} onRetry={() => void loadBox(activeTab, 1, true)} />
            ) : filteredLetters.length > 0 ? (
              filteredLetters.map((letter) => {
                const otherPerson = activeTab === "inbox" ? letter.sender : letter.recipient;
                const isUnread = !letter.is_read && activeTab === "inbox";

                return (
                  <article
                    key={letter.id}
                    onClick={() => void handleOpen(letter)}
                    className={`panel-classic p-3.5 transition-all hover:shadow-md cursor-pointer border ${
                      isUnread
                        ? "bg-pink-50/40 border-pink-200"
                        : "bg-white border-slate-200"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      
                      {/* Avatar with BubbleOverlay */}
                      <div className="relative w-11 h-11 rounded-full overflow-hidden flex-shrink-0 border border-slate-200">
                        <Avatar user={otherPerson} className="w-full h-full" />
                        <BubbleOverlay opacity={0.4} />
                      </div>

                      {/* Content */}
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                            <span className="text-xs font-bold text-slate-900 truncate">
                              {otherPerson.name}
                            </span>
                            <span className="text-[11px] text-slate-400 font-mono">
                              @{otherPerson.username}
                            </span>
                            {isUnread && (
                              <span className="w-2 h-2 rounded-full bg-pink-600 flex-shrink-0" title="Não lida" />
                            )}
                          </div>

                          <span className="text-[10px] text-slate-400 flex-shrink-0">
                            {formatTime(letter.sent_at)}
                          </span>
                        </div>

                        {/* Letter Excerpt */}
                        <p className={`text-xs leading-relaxed line-clamp-2 ${
                          isUnread ? "text-slate-900 font-medium" : "text-slate-600"
                        }`}>
                          {letter.text}
                        </p>

                        {/* Badges footer: Image attachment indicator & Read receipt */}
                        <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                          {letter.image ? (
                            <span className="inline-flex items-center gap-1 font-semibold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200">
                              <ImageIcon className="w-3 h-3" />
                              Foto em anexo
                            </span>
                          ) : (
                            <span />
                          )}

                          {activeTab === "sent" && (
                            <span className="inline-flex items-center gap-0.5 text-slate-400">
                              {letter.read_at ? (
                                <>
                                  <CheckCheck className="w-3 h-3 text-emerald-600" />
                                  <span>Lida</span>
                                </>
                              ) : (
                                <span>Entregue</span>
                              )}
                            </span>
                          )}
                        </div>

                      </div>
                    </div>
                  </article>
                );
              })
            ) : (
              <div className="panel-classic p-8 text-center text-slate-500">
                <Mail className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-700">
                  {activeTab === "inbox"
                    ? activeFilter === "unread"
                      ? "Você não possui cartas não lidas."
                      : "Sua caixa postal está vazia."
                    : "Você ainda não enviou nenhuma carta."}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Cartas só podem ser iniciadas com pessoas que você segue.
                </p>
              </div>
            )}
          </div>

          {openError && (
            <p role="alert" className="mt-2 text-[11px] text-red-700">
              {openError}
            </p>
          )}

          {box.status === "ready" && box.next !== null && (
            <div className="text-center my-4">
              <button
                onClick={() => void loadBox(activeTab, box.next as number, false)}
                className="btn-outline px-4 py-1.5 text-xs font-semibold"
              >
                Carregar mais
              </button>
            </div>
          )}

          {/* Footer note inside the scrollable stream at the bottom */}
          <div className="py-6 text-center text-[11px] text-slate-400">
            Bubbles • Caixa Postal de Cartas
          </div>

        </div>

        {/* Right Column (3 Cols) - Static Sidebar */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Quick Contacts to Send Letter */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">
                Quem você segue
              </span>
            </div>
            <div className="p-2 divide-y divide-slate-100">
              {following.map((friend) => (
                <div
                  key={friend.id}
                  className="py-2 px-1 flex items-center justify-between gap-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Avatar user={friend} className="w-7 h-7 flex-shrink-0" />
                    <div className="min-w-0">
                      <span className="text-xs font-bold text-slate-800 block truncate">
                        {friend.name}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono block">
                        @{friend.username}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setReplyToLetter(null);
                      setInitialRecipient(friend.username);
                      setIsComposeOpen(true);
                    }}
                    className="text-[10px] text-pink-600 hover:text-pink-700 font-semibold px-2 py-0.5 border border-pink-200 rounded-sm hover:bg-pink-50 transition-colors flex-shrink-0 cursor-pointer"
                  >
                    Escrever
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Philosophy of Letters Box */}
          <div className="panel-classic bg-slate-50/50">
            <div className="p-3">
              <span className="text-xs font-bold text-slate-800 block mb-1">
                A Filosofia das Cartas
              </span>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Cartas são correspondências privadas e deliberadas. Cada mensagem enviada é imutável e preserva a intimidade entre você e quem você admira.
              </p>
            </div>
          </div>

        </div>

      </div>

      {/* Compose Letter Modal */}
      {isComposeOpen && (
        <LetterComposeModal
          currentUser={currentUser}
          replyToLetter={replyToLetter}
          initialRecipientUsername={initialRecipient}
          onClose={() => {
            setIsComposeOpen(false);
            setReplyToLetter(null);
            setInitialRecipient("");
          }}
          onLetterSent={handleLetterSent}
        />
      )}

      {/* Detail Letter Inspection Modal */}
      {selectedLetter && (
        <LetterDetailModal
          letter={selectedLetter}
          currentUser={currentUser}
          onClose={() => setSelectedLetter(null)}
          onReply={(letterToReply) => {
            setReplyToLetter(letterToReply);
            setIsComposeOpen(true);
          }}
        />
      )}

    </div>
  );
};
