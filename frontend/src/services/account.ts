import type { User } from "@/types";
import { api, setAccessToken } from "./api";

export interface UpdateProfileInput {
  name: string;
  description: string;
  birthDate: string;
  photo?: File | null;
  removePhoto?: boolean;
}

export async function updateProfile(input: UpdateProfileInput): Promise<User> {
  const form = new FormData();
  form.append("name", input.name);
  form.append("description", input.description);
  if (input.birthDate) form.append("birth_date", input.birthDate);
  if (input.photo) form.append("profile_photo", input.photo);
  else if (input.removePhoto) form.append("remove_profile_photo", "true");
  const { data } = await api.patch<User>("/users/me/", form);
  return data;
}

/** The server ends every other session and answers with a fresh access token for this one. */
export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  const { data } = await api.post<{ access: string }>("/users/me/password/", {
    current_password: currentPassword,
    new_password: newPassword,
  });
  setAccessToken(data.access);
}

export async function changeEmail(password: string, newEmail: string): Promise<User> {
  const { data } = await api.post<User>("/users/me/email/", { password, new_email: newEmail });
  return data;
}

export async function deleteAccount(password: string): Promise<void> {
  await api.delete("/users/me/", { data: { password } });
  setAccessToken(null);
}
