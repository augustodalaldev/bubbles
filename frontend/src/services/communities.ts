import type { Bubblegram, Community, CommunityMemberItem, Paginated } from "@/types";
import { api } from "./api";

export async function listCommunities(params: { search?: string; mine?: boolean; page?: number }) {
  const { data } = await api.get<Paginated<Community>>("/communities/", {
    params: { search: params.search || undefined, mine: params.mine ? "true" : undefined, page: params.page },
  });
  return data;
}

export async function getCommunity(commname: string): Promise<Community> {
  const { data } = await api.get<Community>(`/communities/${commname}/`);
  return data;
}

export interface CreateCommunityInput {
  commname: string;
  name: string;
  description: string;
  guidelines: string;
  communityPhoto?: File | null;
}

export async function createCommunity(input: CreateCommunityInput): Promise<Community> {
  const form = new FormData();
  form.append("commname", input.commname);
  form.append("name", input.name);
  form.append("description", input.description);
  form.append("guidelines", input.guidelines);
  if (input.communityPhoto) form.append("community_photo", input.communityPhoto);
  const { data } = await api.post<Community>("/communities/", form);
  return data;
}

export async function updateCommunityPhoto(commname: string, photo: File): Promise<Community> {
  const form = new FormData();
  form.append("community_photo", photo);
  const { data } = await api.patch<Community>(`/communities/${commname}/`, form);
  return data;
}

export interface UpdateCommunityInput {
  name: string;
  description: string;
  photo?: File | null;
  removePhoto?: boolean;
}

export async function updateCommunity(commname: string, input: UpdateCommunityInput): Promise<Community> {
  const form = new FormData();
  form.append("name", input.name);
  form.append("description", input.description);
  if (input.photo) form.append("community_photo", input.photo);
  else if (input.removePhoto) form.append("remove_community_photo", "true");
  const { data } = await api.patch<Community>(`/communities/${commname}/`, form);
  return data;
}

export async function deleteCommunity(commname: string, confirmCommname: string): Promise<void> {
  await api.delete(`/communities/${commname}/`, { data: { confirm_commname: confirmCommname } });
}

export async function transferLeadership(commname: string, newLeaderUsername: string): Promise<void> {
  await api.post(`/communities/${commname}/transfer-leadership/`, { new_leader_username: newLeaderUsername });
}

export async function updateGuidelines(commname: string, guidelines: string): Promise<Community> {
  const { data } = await api.patch<Community>(`/communities/${commname}/guidelines/`, { guidelines });
  return data;
}

export async function joinCommunity(commname: string): Promise<CommunityMemberItem> {
  const { data } = await api.post<CommunityMemberItem>(`/communities/${commname}/join/`);
  return data;
}

export async function leaveCommunity(commname: string): Promise<void> {
  await api.post(`/communities/${commname}/leave/`);
}

export async function listMembers(commname: string, page = 1) {
  const { data } = await api.get<Paginated<CommunityMemberItem>>(`/communities/${commname}/members/`, {
    params: { page },
  });
  return data;
}

export async function listCommunityBubblegrams(commname: string, page = 1) {
  const { data } = await api.get<Paginated<Bubblegram>>(`/communities/${commname}/bubblegrams/`, {
    params: { page },
  });
  return data;
}

/** Only available to the community's leader/admins (see `permissions.can_view_wallet`). */
export async function getCommunityWallet(commname: string): Promise<{ soap_balance: number }> {
  const { data } = await api.get<{ soap_balance: number }>(`/communities/${commname}/wallet/`);
  return data;
}
