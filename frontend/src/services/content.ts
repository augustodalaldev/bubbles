import type { Bubblegram, Bubblepop, Comment, Paginated } from "@/types";
import { api } from "./api";

export interface CreateBubblegramInput {
  text: string;
  files?: File[];
  /** Community handle; omit to publish on the personal profile. */
  commname?: string;
}

export async function createBubblegram(input: CreateBubblegramInput): Promise<Bubblegram> {
  const form = new FormData();
  form.append("text", input.text);
  form.append("type", input.files && input.files.length > 0 ? "MEDIA" : "TEXT");
  if (input.commname) form.append("commname", input.commname);
  input.files?.forEach((file) => form.append("media_files", file));
  const { data } = await api.post<Bubblegram>("/bubblegrams/", form);
  return data;
}

export async function getBubblegram(id: number): Promise<Bubblegram> {
  const { data } = await api.get<Bubblegram>(`/bubblegrams/${id}/`);
  return data;
}

export async function deleteBubblegram(id: number): Promise<void> {
  await api.delete(`/bubblegrams/${id}/`);
}

export async function supportBubblegram(id: number): Promise<{ soap_count: number }> {
  const { data } = await api.post<{ soap_count: number }>(`/bubblegrams/${id}/support/`);
  return data;
}

export async function listComments(bubblegramId: number, page = 1) {
  const { data } = await api.get<Paginated<Comment>>(`/bubblegrams/${bubblegramId}/comments/`, {
    params: { page },
  });
  return data;
}

export async function createComment(
  bubblegramId: number,
  text: string,
  parentId: number | null = null
): Promise<Comment> {
  const { data } = await api.post<Comment>(`/bubblegrams/${bubblegramId}/comments/`, {
    text,
    parent_id: parentId,
  });
  return data;
}

export async function deleteComment(id: number): Promise<void> {
  await api.delete(`/comments/${id}/`);
}

export async function supportComment(id: number): Promise<{ soap_count: number }> {
  const { data } = await api.post<{ soap_count: number }>(`/comments/${id}/support/`);
  return data;
}

export interface CreateBubblepopInput {
  image: File;
  durationHours: number;
  description?: string;
}

export async function createBubblepop(input: CreateBubblepopInput): Promise<Bubblepop> {
  const form = new FormData();
  form.append("image", input.image);
  form.append("duration_hours", String(input.durationHours));
  if (input.description) form.append("description", input.description);
  const { data } = await api.post<Bubblepop>("/bubblepops/", form);
  return data;
}

export async function deleteBubblepop(id: number): Promise<void> {
  await api.delete(`/bubblepops/${id}/`);
}
