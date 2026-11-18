import type { Letter, Paginated } from "@/types";
import { api } from "./api";

export async function listInbox(page = 1) {
  const { data } = await api.get<Paginated<Letter>>("/letters/inbox/", { params: { page } });
  return data;
}

export async function listSent(page = 1) {
  const { data } = await api.get<Paginated<Letter>>("/letters/sent/", { params: { page } });
  return data;
}

/** Opening a letter as its recipient marks it as read on the server. */
export async function openLetter(id: number): Promise<Letter> {
  const { data } = await api.get<Letter>(`/letters/${id}/`);
  return data;
}

export interface SendLetterInput {
  recipientUsername: string;
  text: string;
  replyToId?: number | null;
  image?: File | null;
}

export async function sendLetter(input: SendLetterInput): Promise<Letter> {
  const form = new FormData();
  form.append("recipient_username", input.recipientUsername);
  form.append("text", input.text);
  if (input.replyToId) form.append("reply_to_id", String(input.replyToId));
  if (input.image) form.append("image", input.image);
  const { data } = await api.post<Letter>("/letters/", form);
  return data;
}
