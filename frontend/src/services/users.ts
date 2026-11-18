import type { Bubblegram, Bubblepop, FollowItem, Paginated, SearchResult, User } from "@/types";
import { api } from "./api";

export async function getProfile(username: string): Promise<User> {
  const { data } = await api.get<User>(`/users/${username}/`);
  return data;
}

export async function listUserBubblegrams(username: string, page = 1) {
  const { data } = await api.get<Paginated<Bubblegram>>(`/users/${username}/bubblegrams/`, {
    params: { page },
  });
  return data;
}

export async function listUserBubblepops(username: string): Promise<Bubblepop[]> {
  const { data } = await api.get<Bubblepop[]>(`/users/${username}/bubblepops/`);
  return data;
}

export async function listFollowers(username: string, page = 1) {
  const { data } = await api.get<Paginated<FollowItem>>(`/users/${username}/followers/`, {
    params: { page },
  });
  return data;
}

export async function listFollowing(username: string, page = 1) {
  const { data } = await api.get<Paginated<FollowItem>>(`/users/${username}/following/`, {
    params: { page },
  });
  return data;
}

export async function followUser(username: string): Promise<void> {
  await api.post(`/users/${username}/follow/`);
}

export async function unfollowUser(username: string): Promise<void> {
  await api.delete(`/users/${username}/follow/`);
}

export async function search(q: string): Promise<SearchResult> {
  const { data } = await api.get<SearchResult>("/search/", { params: { q } });
  return data;
}
