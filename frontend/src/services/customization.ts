import type { CustomizationItem, Paginated, User, UserInventoryItem } from "@/types";
import { api } from "./api";

export async function listItems(page = 1) {
  const { data } = await api.get<Paginated<CustomizationItem>>("/customization/items/", {
    params: { page, page_size: 100 },
  });
  return data;
}

export async function listInventory(page = 1) {
  const { data } = await api.get<Paginated<UserInventoryItem>>("/customization/inventory/", {
    params: { page, page_size: 100 },
  });
  return data;
}

export async function purchaseItem(
  id: number
): Promise<{ inventory_item: UserInventoryItem; remaining_soap: number }> {
  const { data } = await api.post(`/customization/items/${id}/purchase/`);
  return data;
}

/** Slot names are the lower-cased item types, e.g. "avatar_frame". Pass null to unequip a slot. */
export async function equipSlots(slots: Record<string, number | null>) {
  const { data } = await api.post<User["customization_json"]>("/customization/equip/", { slots });
  return data;
}
