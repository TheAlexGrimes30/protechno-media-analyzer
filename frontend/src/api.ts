/** База API: пустая строка = относительные пути (прокси Vite → backend). Или VITE_API_BASE_URL=http://127.0.0.1:8000 */
export const JWT_KEY = "protechno_jwt";
export const getStoredToken = (): string => localStorage.getItem(JWT_KEY) ?? "";
export function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";
  if (!path.startsWith("/")) return `${base}/${path}`;
  return base ? `${base}${path}` : path;
}

function authHeaders(token: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson<T>(path: string, init: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(apiUrl(path), init);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Нет соединения с backend. Проверьте, что фронт запущен через Vite, а backend доступен по proxy /api");
    }
    throw error;
  }

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(detail || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export type LlmGenerateResponse = {
  text: string;
  model: string;
  shots_used: number;
};

export async function llmGenerate(query: string): Promise<LlmGenerateResponse> {
  return fetchJson<LlmGenerateResponse>("/api/llm/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
}

export type VkPosterResponse = {
  post_id: number;
  url: string;
};

/** Публикация на стену VK (токен и группа настраиваются на бэкенде). */
export async function vkPoster(token: string, payload: {
  message: string;
  attachments?: string | null;
  from_group?: boolean;
}): Promise<VkPosterResponse> {
  return fetchJson<VkPosterResponse>("/api/vk/poster", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify({
      message: payload.message,
      attachments: payload.attachments ?? null,
      from_group: payload.from_group ?? true,
    }),
  });
}

export async function vkDeletePost(token: string, post_id: number): Promise<{ success: boolean }> {
  return fetchJson<{ success: boolean }>("/api/vk/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify({ post_id }),
  });
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export type AuthResponse = { access_token: string; token_type: string; email: string; name: string };
export type MeResponse = { id: string; email: string; name: string; role: string };

export async function apiGetMe(token: string): Promise<MeResponse> {
  return fetchJson<MeResponse>("/api/auth/me", {
    headers: { ...authHeaders(token) },
  });
}

export async function authRegister(email: string, name: string, password: string): Promise<AuthResponse> {
  return fetchJson<AuthResponse>("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, name, password }),
  });
}

export async function authLogin(email: string, password: string): Promise<AuthResponse> {
  return fetchJson<AuthResponse>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

// ─── Posts (Content Events) ───────────────────────────────────────────────────

export type ApiPost = {
  id: string;
  title: string;
  text_draft: string | null;
  text_generated: string | null;
  tone: string;
  vk_post_id: string | null;
  vk_wall_url: string | null;
  status: string;
  created_at: string;
};

export async function apiGetPosts(token: string): Promise<ApiPost[]> {
  return fetchJson<ApiPost[]>("/api/posts/", {
    headers: { ...authHeaders(token) },
  });
}

export async function apiCreatePost(token: string, data: {
  title: string; text_draft: string; text_generated: string; tone: string; vk_post_id?: string | null;
}): Promise<ApiPost> {
  return fetchJson<ApiPost>("/api/posts/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });
}

export async function apiUpdatePostVk(token: string, postId: string, vkPostId: string | null): Promise<ApiPost> {
  return fetchJson<ApiPost>(`/api/posts/${postId}/vk`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify({ vk_post_id: vkPostId }),
  });
}

export async function apiDeletePost(token: string, postId: string): Promise<void> {
  await fetchJson<unknown>(`/api/posts/${postId}`, {
    method: "DELETE",
    headers: { ...authHeaders(token) },
  });
}

// ─── Calendar Events ──────────────────────────────────────────────────────────

export type ApiCalendarEvent = {
  id: string;
  title: string;
  date: string;
  start_time: string;
  end_time: string;
  description: string;
  status: string;
  platforms: string[];
};

export async function apiGetCalendarEvents(token: string): Promise<ApiCalendarEvent[]> {
  return fetchJson<ApiCalendarEvent[]>("/api/calendar/", {
    headers: { ...authHeaders(token) },
  });
}

export async function apiCreateCalendarEvent(token: string, data: {
  title: string; date: string; description: string;
  start_time: string; end_time: string; status: string; platforms: string[];
}): Promise<ApiCalendarEvent> {
  return fetchJson<ApiCalendarEvent>("/api/calendar/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });
}

export async function apiUpdateCalendarEvent(token: string, eventId: string, data: {
  title: string; date: string; description: string;
  start_time: string; end_time: string; status: string; platforms: string[];
}): Promise<ApiCalendarEvent> {
  return fetchJson<ApiCalendarEvent>(`/api/calendar/${eventId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });
}

export async function apiDeleteCalendarEvent(token: string, eventId: string): Promise<void> {
  await fetchJson<unknown>(`/api/calendar/${eventId}`, {
    method: "DELETE",
    headers: { ...authHeaders(token) },
  });
}

/** Загружает фото в VK и возвращает строку вложения (photo{owner}_{id}). */
export async function vkUploadPhoto(token: string, file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  let res: Response;
  try {
    res = await fetch(apiUrl("/api/vk/upload-photo"), { method: "POST", body: form, headers: { ...authHeaders(token) } });
  } catch (error) {
    throw new Error("Нет соединения с backend при загрузке фото");
  }
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(detail || `HTTP ${res.status}`);
  }
  const data = (await res.json()) as { attachment: string };
  return data.attachment;
}
