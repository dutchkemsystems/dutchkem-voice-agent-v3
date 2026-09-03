const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  detail: string;
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorData: ApiError;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: `Request failed with status ${response.status}` };
    }
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return response.json() as Promise<T>;
  }
  return response.text() as unknown as Promise<T>;
}

export interface User {
  id: string;
  email: string;
  username: string;
  voice_profile_id?: string;
  face_embedding?: boolean;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface VoiceProfile {
  id: string;
  name: string;
  created_at: string;
}

export interface InterviewSession {
  id: string;
  status: string;
  started_at?: string;
  ended_at?: string;
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<TokenResponse>(`${API_BASE}/auth/login`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    register: (data: { email: string; username: string; password: string }) =>
      request<User>(`${API_BASE}/auth/register`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    me: () => request<User>(`${API_BASE}/auth/me`),
  },
  voice: {
    clone: (audioFile: File) => {
      const formData = new FormData();
      formData.append("audio", audioFile);
      return request<VoiceProfile>(`${API_BASE}/voice/clone`, {
        method: "POST",
        body: formData,
      });
    },
    synthesize: (text: string, voiceId: string) =>
      fetch(`${API_BASE}/voice/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice_id: voiceId }),
      }).then((r) => r.blob()),
    profiles: () => request<VoiceProfile[]>(`${API_BASE}/voice/profiles`),
  },
  proctoring: {
    registerFace: (imageFile: File) => {
      const formData = new FormData();
      formData.append("image", imageFile);
      return request<{ status: string }>(`${API_BASE}/proctoring/register-face`, {
        method: "POST",
        body: formData,
      });
    },
    verify: (imageFile: File) => {
      const formData = new FormData();
      formData.append("image", imageFile);
      return request<{ verified: boolean; confidence: number }>(
        `${API_BASE}/proctoring/verify`,
        { method: "POST", body: formData }
      );
    },
  },
  interview: {
    start: () =>
      request<InterviewSession>(`${API_BASE}/interview/start`, {
        method: "POST",
      }),
    stop: (sessionId: string) =>
      request<InterviewSession>(`${API_BASE}/interview/${sessionId}/stop`, {
        method: "POST",
      }),
  },
};
