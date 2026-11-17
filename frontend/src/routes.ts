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
  if (pathname.startsWith("/letters")) return "letters";
  if (ownUsername && pathname.toLowerCase() === paths.profile(ownUsername).toLowerCase()) {
    return "profile";
  }
  return null;
}
