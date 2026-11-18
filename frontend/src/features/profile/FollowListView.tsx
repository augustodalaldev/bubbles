import React, { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Avatar } from "@/components/Avatar";
import { NotFoundView } from "@/components/NotFoundView";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { UserName } from "@/components/UserName";
import { errorMessage, toApiError } from "@/services/errors";
import { listFollowers, listFollowing } from "@/services/users";
import { paths } from "@/routes";
import type { User } from "@/types";

interface FollowListViewProps {
  username: string;
  kind: "followers" | "following";
}

/** Paginated list of a profile's followers, or of the people that profile follows. */
export const FollowListView: React.FC<FollowListViewProps> = ({ username, kind }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [next, setNext] = useState<number | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "notfound">("loading");
  const [error, setError] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = useCallback(
    async (page: number, reset: boolean) => {
      if (reset) setStatus("loading");
      else setLoadingMore(true);
      try {
        const data = await (kind === "followers" ? listFollowers(username, page) : listFollowing(username, page));
        setUsers((prev) => (reset ? [] : prev).concat(data.results.map((item) => item.user)));
        setNext(data.next ? page + 1 : null);
        setStatus("ready");
      } catch (err) {
        if (toApiError(err).status === 404) setStatus("notfound");
        else {
          setError(errorMessage(err));
          if (reset) setStatus("error");
        }
      } finally {
        setLoadingMore(false);
      }
    },
    [kind, username]
  );

  useEffect(() => {
    void load(1, true);
  }, [load]);

  if (status === "notfound") return <NotFoundView message="Este perfil não existe." />;

  const title = kind === "followers" ? "Seguidores" : "Seguindo";
  return (
    <main className="max-w-2xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
      <Link
        to={paths.profile(username)}
        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-pink-700 mb-3"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Voltar ao perfil de @{username}
      </Link>
      <div className="panel-classic">
        <div className="panel-classic-header">
          <h1 className="text-sm sm:text-base font-bold text-slate-800">
            {title} de @{username}
          </h1>
        </div>
        <div className="p-3">
          {status === "loading" ? (
            <LoadingState />
          ) : status === "error" ? (
            <ErrorState message={error ?? "Não foi possível carregar a lista."} onRetry={() => void load(1, true)} />
          ) : users.length === 0 ? (
            <EmptyState message={kind === "followers" ? "Ainda sem seguidores." : "Ainda não segue ninguém."} />
          ) : (
            <ul className="divide-y divide-slate-100">
              {users.map((user) => (
                <li key={user.id}>
                  <Link
                    to={paths.profile(user.username)}
                    className="flex items-center gap-3 py-2.5 px-1 rounded-sm hover:bg-slate-50"
                  >
                    <Avatar user={user} className="w-10 h-10 flex-shrink-0" />
                    <div className="min-w-0">
                      <UserName user={user} className="text-xs font-bold text-slate-900 truncate" />
                      <span className="block text-[11px] text-slate-400 font-mono truncate">@{user.username}</span>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {status === "ready" && next && (
            <button
              onClick={() => void load(next, false)}
              disabled={loadingMore}
              className="btn-pink w-full mt-3 py-1.5 text-xs font-bold rounded-sm disabled:opacity-60"
            >
              {loadingMore ? "Carregando..." : "Carregar mais"}
            </button>
          )}
        </div>
      </div>
    </main>
  );
};
