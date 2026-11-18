import type { Paginated } from "@/types";
import { api } from "./api";

export type ModStatus = "ACTIVE" | "SUSPENDED" | "BANNED";

export interface AdminUser {
  id: number;
  username: string;
  name: string;
  email: string;
  profile_photo: string | null;
  is_staff: boolean;
  status: ModStatus;
  suspended_until: string | null;
  moderation_reason: string;
  created_at: string;
}

export interface AdminCommunity {
  id: number;
  commname: string;
  name: string;
  member_count: number;
  is_archived: boolean;
  status: ModStatus;
  suspended_until: string | null;
  blocked_at: string | null;
  moderation_reason: string;
  created_at: string;
}

export interface AuditLogEntry {
  id: number;
  actor_username: string | null;
  action: string;
  target_type: string;
  target_id: string;
  reason: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

interface ListParams {
  q?: string;
  status?: string;
  page?: number;
}

const clean = (p: ListParams) => ({ q: p.q || undefined, status: p.status || undefined, page: p.page });

export async function listAdminUsers(params: ListParams) {
  const { data } = await api.get<Paginated<AdminUser>>("/admin/users/", { params: clean(params) });
  return data;
}

export async function listAdminCommunities(params: ListParams) {
  const { data } = await api.get<Paginated<AdminCommunity>>("/admin/communities/", { params: clean(params) });
  return data;
}

export async function listAuditLogs(page = 1) {
  const { data } = await api.get<Paginated<AuditLogEntry>>("/admin/audit-logs/", { params: { page } });
  return data;
}

export const suspendUser = (id: number, durationHours: number, reason: string) =>
  api.post(`/admin/users/${id}/suspend/`, { duration_hours: durationHours, reason });
export const banUser = (id: number, reason: string) => api.post(`/admin/users/${id}/ban/`, { reason });
/** Lifts a suspension or a ban. */
export const restoreUser = (id: number, reason: string) => api.post(`/admin/users/${id}/unban/`, { reason });

export const suspendCommunity = (commname: string, durationHours: number, reason: string) =>
  api.post(`/admin/communities/${commname}/suspend/`, { duration_hours: durationHours, reason });
export const banCommunity = (commname: string, reason: string) =>
  api.post(`/admin/communities/${commname}/block/`, { reason });
/** Lifts a suspension or a ban. */
export const restoreCommunity = (commname: string, reason: string) =>
  api.post(`/admin/communities/${commname}/unblock/`, { reason });
