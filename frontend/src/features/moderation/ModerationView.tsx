import React, { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { formatUntil } from "@/components/ModerationBanner";
import { NotFoundView } from "@/components/NotFoundView";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import * as admin from "@/services/admin";
import type { AdminCommunity, AdminUser, AuditLogEntry, ModStatus } from "@/services/admin";
import { errorMessage } from "@/services/errors";
import { paths } from "@/routes";

type Tab = "users" | "communities" | "log";
type Action = "suspend" | "ban" | "restore";

const INPUT =
  "px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 focus:outline-none focus:border-pink-500 focus:bg-white";

const STATUS_LABEL: Record<ModStatus, string> = { ACTIVE: "Ativo", SUSPENDED: "Suspenso", BANNED: "Banido" };
const STATUS_STYLE: Record<ModStatus, string> = {
  ACTIVE: "bg-emerald-50 text-emerald-700 border-emerald-200",
  SUSPENDED: "bg-amber-50 text-amber-800 border-amber-300",
  BANNED: "bg-red-50 text-red-700 border-red-300",
};
const ACTION_LABEL: Record<string, string> = {
  USER_SUSPEND: "Usuário suspenso",
  USER_BAN: "Usuário banido",
  USER_UNBAN: "Usuário reativado",
  COMMUNITY_SUSPEND: "Comunidade suspensa",
  COMMUNITY_BLOCK: "Comunidade banida",
  COMMUNITY_UNBLOCK: "Comunidade reativada",
  CONTENT_DELETE: "Conteúdo removido",
  ECONOMY_ADJUSTMENT: "Ajuste de soap",
  REPORT_RESOLVE: "Denúncia resolvida",
  REPORT_DISMISS: "Denúncia descartada",
};

const StatusBadge: React.FC<{ status: ModStatus; until?: string | null }> = ({ status, until }) => (
  <span className={`inline-block text-[10px] font-bold px-1.5 py-0.5 rounded-sm border ${STATUS_STYLE[status]}`}>
    {STATUS_LABEL[status]}
    {status === "SUSPENDED" && until ? ` até ${formatUntil(until)}` : ""}
  </span>
);

interface Target {
  kind: "user" | "community";
  key: string | number;
  label: string;
  action: Action;
}

/** Reason (and, for a suspension, the duration) are required: they are shown to the person and logged. */
const ActionDialog: React.FC<{ target: Target; onDone: () => void; onCancel: () => void }> = ({ target, onDone, onCancel }) => {
  const [reason, setReason] = useState("");
  const [hours, setHours] = useState(24);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    if (!reason.trim()) {
      setError("Informe o motivo.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const r = reason.trim();
      if (target.kind === "user") {
        const id = target.key as number;
        if (target.action === "suspend") await admin.suspendUser(id, hours, r);
        else if (target.action === "ban") await admin.banUser(id, r);
        else await admin.restoreUser(id, r);
      } else {
        const name = target.key as string;
        if (target.action === "suspend") await admin.suspendCommunity(name, hours, r);
        else if (target.action === "ban") await admin.banCommunity(name, r);
        else await admin.restoreCommunity(name, r);
      }
      onDone();
    } catch (err) {
      setError(errorMessage(err));
      setBusy(false);
    }
  };

  const verb = { suspend: "Suspender", ban: "Banir", restore: "Reativar" }[target.action];
  const effect =
    target.kind === "user"
      ? {
          suspend: "A pessoa continua entrando e lendo, mas não publica, comenta, apoia nem envia cartas. Verá um aviso com o motivo.",
          ban: "A pessoa não consegue mais entrar e o perfil e o conteúdo somem para os outros. Ao tentar entrar, verá o motivo.",
          restore: "A conta volta ao normal.",
        }[target.action]
      : {
          suspend: "A comunidade some das listas e fica somente leitura. Líder e membros veem um aviso com o motivo.",
          ban: "Igual à suspensão, mas sem prazo para terminar.",
          restore: "A comunidade volta ao normal.",
        }[target.action];

  return (
    <ConfirmDialog
      title={`${verb}: ${target.label}`}
      confirmLabel={verb}
      busy={busy}
      error={error}
      onConfirm={() => void run()}
      onCancel={onCancel}
    >
      <p>{effect}</p>
      {target.action === "suspend" && (
        <label className="block">
          <span className="block mb-1 font-semibold text-slate-800">Duração (horas)</span>
          <input
            type="number"
            min={1}
            max={24 * 365}
            value={hours}
            onChange={(e) => setHours(Math.max(1, Number(e.target.value) || 1))}
            aria-label="Duração em horas"
            className={`${INPUT} w-28`}
          />
        </label>
      )}
      <label className="block">
        <span className="block mb-1 font-semibold text-slate-800">Motivo (visível para a pessoa e registrado)</span>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={500}
          rows={3}
          aria-label="Motivo"
          className={`${INPUT} w-full`}
        />
      </label>
    </ConfirmDialog>
  );
};

function useList<T>(fetcher: (page: number) => Promise<{ results: T[]; next: string | null }>, deps: unknown[]) {
  const [items, setItems] = useState<T[]>([]);
  const [next, setNext] = useState<number | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const [more, setMore] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const load = useCallback(async (page: number, reset: boolean) => {
    if (reset) setStatus("loading");
    else setMore(true);
    try {
      const data = await fetcher(page);
      setItems((prev) => (reset ? data.results : [...prev, ...data.results]));
      setNext(data.next ? page + 1 : null);
      setStatus("ready");
    } catch (err) {
      setError(errorMessage(err));
      if (reset) setStatus("error");
    } finally {
      setMore(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    void load(1, true);
  }, [load]);

  return { items, next, status, error, more, reload: () => load(1, true), loadMore: () => (next ? load(next, false) : Promise.resolve()) };
}

const ListFrame: React.FC<{
  list: { status: string; error: string | null; next: number | null; more: boolean; reload: () => void; loadMore: () => void; items: unknown[] };
  empty: string;
  children: React.ReactNode;
}> = ({ list, empty, children }) => {
  if (list.status === "loading") return <LoadingState />;
  if (list.status === "error") return <ErrorState message={list.error ?? "Não foi possível carregar."} onRetry={list.reload} />;
  if (list.items.length === 0) return <EmptyState message={empty} />;
  return (
    <>
      <ul className="divide-y divide-slate-100">{children}</ul>
      {list.next && (
        <button onClick={list.loadMore} disabled={list.more} className="btn-pink w-full mt-3 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60">
          {list.more ? "Carregando..." : "Carregar mais"}
        </button>
      )}
    </>
  );
};

const Btn: React.FC<{ onClick: () => void; danger?: boolean; children: React.ReactNode }> = ({ onClick, danger, children }) => (
  <button
    onClick={onClick}
    className={`px-2 py-1 text-[11px] font-bold rounded-sm border ${
      danger ? "border-red-300 text-red-700 hover:bg-red-50" : "border-slate-300 text-slate-700 hover:bg-slate-100"
    }`}
  >
    {children}
  </button>
);

const UsersTab: React.FC<{ q: string; status: string; onAct: (t: Target) => void; version: number }> = ({ q, status, onAct, version }) => {
  const list = useList((page) => admin.listAdminUsers({ q, status, page }), [q, status, version]);
  return (
    <ListFrame list={list} empty="Nenhum usuário encontrado.">
      {list.items.map((u: AdminUser) => (
        <li key={u.id} className="py-2.5 flex flex-wrap items-center gap-2 justify-between">
          <div className="min-w-0">
            <Link to={paths.profile(u.username)} className="text-xs font-bold text-slate-900 hover:text-pink-700">
              {u.name} <span className="font-mono font-normal text-slate-400">@{u.username}</span>
            </Link>
            <div className="mt-0.5 flex flex-wrap items-center gap-1.5">
              <StatusBadge status={u.status} until={u.suspended_until} />
              {u.is_staff && <span className="text-[10px] font-bold text-purple-700">equipe</span>}
            </div>
            {u.status !== "ACTIVE" && u.moderation_reason && (
              <p className="text-[11px] text-slate-500 break-words">Motivo: {u.moderation_reason}</p>
            )}
          </div>
          {!u.is_staff && (
            <div className="flex gap-1.5">
              {u.status === "ACTIVE" ? (
                <>
                  <Btn onClick={() => onAct({ kind: "user", key: u.id, label: `@${u.username}`, action: "suspend" })}>Suspender</Btn>
                  <Btn danger onClick={() => onAct({ kind: "user", key: u.id, label: `@${u.username}`, action: "ban" })}>Banir</Btn>
                </>
              ) : (
                <>
                  {u.status === "SUSPENDED" && (
                    <Btn danger onClick={() => onAct({ kind: "user", key: u.id, label: `@${u.username}`, action: "ban" })}>Banir</Btn>
                  )}
                  <Btn onClick={() => onAct({ kind: "user", key: u.id, label: `@${u.username}`, action: "restore" })}>Reativar</Btn>
                </>
              )}
            </div>
          )}
        </li>
      ))}
    </ListFrame>
  );
};

const CommunitiesTab: React.FC<{ q: string; status: string; onAct: (t: Target) => void; version: number }> = ({ q, status, onAct, version }) => {
  const list = useList((page) => admin.listAdminCommunities({ q, status, page }), [q, status, version]);
  return (
    <ListFrame list={list} empty="Nenhuma comunidade encontrada.">
      {list.items.map((c: AdminCommunity) => {
        const t = (action: Action): Target => ({ kind: "community", key: c.commname, label: `@${c.commname}`, action });
        return (
          <li key={c.id} className="py-2.5 flex flex-wrap items-center gap-2 justify-between">
            <div className="min-w-0">
              <div className="text-xs font-bold text-slate-900">
                {c.name} <span className="font-mono font-normal text-slate-400">@{c.commname}</span>
              </div>
              <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-slate-500">
                <StatusBadge status={c.status} until={c.suspended_until} />
                <span>{c.member_count} membros</span>
              </div>
              {c.status !== "ACTIVE" && c.moderation_reason && (
                <p className="text-[11px] text-slate-500 break-words">Motivo: {c.moderation_reason}</p>
              )}
            </div>
            <div className="flex gap-1.5">
              {c.status === "ACTIVE" ? (
                <>
                  <Btn onClick={() => onAct(t("suspend"))}>Suspender</Btn>
                  <Btn danger onClick={() => onAct(t("ban"))}>Banir</Btn>
                </>
              ) : (
                <>
                  {c.status === "SUSPENDED" && <Btn danger onClick={() => onAct(t("ban"))}>Banir</Btn>}
                  <Btn onClick={() => onAct(t("restore"))}>Reativar</Btn>
                </>
              )}
            </div>
          </li>
        );
      })}
    </ListFrame>
  );
};

const LogTab: React.FC<{ version: number }> = ({ version }) => {
  const list = useList((page) => admin.listAuditLogs(page), [version]);
  return (
    <ListFrame list={list} empty="Nenhuma ação registrada ainda.">
      {list.items.map((e: AuditLogEntry) => (
        <li key={e.id} className="py-2 text-xs">
          <span className="font-bold text-slate-900">{ACTION_LABEL[e.action] ?? e.action}</span>{" "}
          <span className="font-mono text-slate-500">{e.target_id}</span>
          <div className="text-[11px] text-slate-500">
            por @{e.actor_username ?? "?"} · {formatUntil(e.created_at)}
            {e.reason ? ` · ${e.reason}` : ""}
          </div>
        </li>
      ))}
    </ListFrame>
  );
};

export const ModerationView: React.FC = () => {
  const isStaff = useAuthStore((s) => s.user?.is_staff);
  const [params, setParams] = useSearchParams();
  const tab = (params.get("tab") as Tab) || "users";
  const q = params.get("q") ?? "";
  const status = params.get("status") ?? "";
  const [target, setTarget] = useState<Target | null>(null);
  const [version, setVersion] = useState(0);
  const [search, setSearch] = useState(q);

  useEffect(() => setSearch(q), [q]);

  if (!isStaff) return <NotFoundView />;

  const update = (next: Record<string, string>) => {
    const merged = new URLSearchParams(params);
    for (const [k, v] of Object.entries(next)) v ? merged.set(k, v) : merged.delete(k);
    setParams(merged, { replace: true });
  };
  const tabs: { id: Tab; label: string }[] = [
    { id: "users", label: "Usuários" },
    { id: "communities", label: "Comunidades" },
    { id: "log", label: "Histórico" },
  ];

  return (
    <main className="max-w-3xl mx-auto px-3 sm:px-4 py-4 sm:py-6 space-y-3">
      <h1 className="text-base font-bold text-slate-900">Moderação</h1>
      <div className="p-1 flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-sm overflow-x-auto" role="tablist">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => update({ tab: t.id, q: "", status: "" })}
            className={`px-3 py-1 text-xs font-semibold rounded-sm whitespace-nowrap ${
              tab === t.id ? "bg-white text-slate-900 shadow-xs" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="panel-classic">
        {tab !== "log" && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              update({ q: search.trim() });
            }}
            className="p-3 border-b border-slate-100 flex flex-wrap gap-2"
          >
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={tab === "users" ? "Buscar por nome ou @usuário" : "Buscar por nome ou @comunidade"}
              aria-label="Buscar"
              className={`${INPUT} flex-1 min-w-[10rem]`}
            />
            <select value={status} onChange={(e) => update({ status: e.target.value })} aria-label="Situação" className={INPUT}>
              <option value="">Todas as situações</option>
              <option value="ACTIVE">Ativos</option>
              <option value="SUSPENDED">Suspensos</option>
              <option value="BANNED">Banidos</option>
            </select>
            <button className="btn-pink px-3 py-1.5 text-xs font-bold rounded-sm">Buscar</button>
          </form>
        )}
        <div className="p-3">
          {tab === "users" && <UsersTab q={q} status={status} onAct={setTarget} version={version} />}
          {tab === "communities" && <CommunitiesTab q={q} status={status} onAct={setTarget} version={version} />}
          {tab === "log" && <LogTab version={version} />}
        </div>
      </div>

      {target && (
        <ActionDialog
          target={target}
          onCancel={() => setTarget(null)}
          onDone={() => {
            setTarget(null);
            setVersion((v) => v + 1);
          }}
        />
      )}
    </main>
  );
};
