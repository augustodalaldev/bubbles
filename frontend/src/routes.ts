/** Single source of truth for the app's URLs. */
export const paths = {
  home: "/",
  login: "/login",
  register: "/register",
  profile: (username: string) => `/u/${encodeURIComponent(username)}`,
  communities: "/communities",
  community: (commname: string) => `/c/${encodeURIComponent(commname)}`,
  store: "/store",
  letters: "/letters",
  lettersTo: (username: string) => `/letters?to=${encodeURIComponent(username)}`,
  followers: (username: string) => `/u/${encodeURIComponent(username)}/followers`,
  following: (username: string) => `/u/${encodeURIComponent(username)}/following`,
  account: "/conta",
  moderation: (params?: { tab?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.tab) qs.set("tab", params.tab);
    if (params?.q) qs.set("q", params.q);
    const text = qs.toString();
    return text ? `/moderacao?${text}` : "/moderacao";
  },
  communitySettings: (commname: string) => `/c/${encodeURIComponent(commname)}/configuracoes`,
  letter: (id: number) => `/letters/${id}`,
  post: (id: number) => `/p/${id}`,
  search: (term: string) => (term ? `/?q=${encodeURIComponent(term)}` : "/"),
} as const;

/** Names used by the views' `onNavigateToView(view)` callbacks. */
export type AppView = "feed" | "profile" | "communities" | "store" | "letters";

export function viewPath(view: string, ownUsername?: string): string {
  switch (view) {
    case "profile":
      return ownUsername ? paths.profile(ownUsername) : paths.home;
    case "communities":
      return paths.communities;
    case "store":
      return paths.store;
    case "letters":
      return paths.letters;
    default:
      return paths.home;
  }
}

/** Which header tab a pathname belongs to. */
export function viewFromPath(pathname: string, ownUsername?: string): AppView | null {
  if (pathname === "/") return "feed";
  if (pathname.startsWith("/communities") || pathname.startsWith("/c/")) return "communities";
  if (pathname.startsWith("/store")) return "store";
  if (pathname === paths.account) return "profile";
  if (pathname.startsWith("/letters")) return "letters";
  if (ownUsername) {
    const own = paths.profile(ownUsername).toLowerCase();
    const lower = pathname.toLowerCase();
    if (lower === own || lower.startsWith(own + "/")) return "profile";
  }
  return null;
}

/**
 * Where to go after logging in. Only same-origin app paths are accepted (an open redirect would
 * let a crafted `/login?next=https://evil` send people elsewhere), and never the auth screens.
 */
export function safeNext(next: string | null | undefined): string {
  if (!next || !next.startsWith("/") || next.startsWith("//")) return paths.home;
  if (/[\\\u0000-\u001f]/.test(next)) return paths.home;
  if (next === paths.login || next === paths.register) return paths.home;
  if (next.startsWith(paths.login + "?") || next.startsWith(paths.register + "?")) return paths.home;
  return next;
}

/** `/login` (or `/register`) that remembers the page the person wanted. */
export function authPath(base: string, from: { pathname: string; search: string }): string {
  const target = from.pathname + from.search;
  return target === paths.home ? base : `${base}?next=${encodeURIComponent(target)}`;
}

