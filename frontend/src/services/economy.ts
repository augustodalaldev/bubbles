import type { EconomySettings } from "@/types";
import { api } from "./api";

export async function getEconomySettings(): Promise<EconomySettings> {
  const { data } = await api.get<EconomySettings>("/economy/settings/");
  return data;
}
