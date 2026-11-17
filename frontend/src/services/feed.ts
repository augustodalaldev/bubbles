import type { Bubblegram, Bubblepop, Paginated } from "@/types";
import { api } from "./api";

export async function getFeed(page = 1) {
  const { data } = await api.get<Paginated<Bubblegram>>("/feed/", { params: { page } });
  return data;
}

export async function getFeedBubblepops(): Promise<Bubblepop[]> {
  const { data } = await api.get<Bubblepop[]>("/feed/bubblepops/");
  return data;
}
