const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ponytail: cookie helpers — middleware reads `token` cookie, localStorage is for api.ts auth header.
// Set both so middleware and fetch auth stay in sync.
export function setAuthCookie(token: string) {
  document.cookie = `token=${token}; path=/; SameSite=Lax`;
}

export function clearAuthCookie() {
  document.cookie = "token=; path=/; max-age=0";
}

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

  if (response.status === 401 || response.status === 403) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("currentMode");
      clearAuthCookie();
      window.location.href = "/login";
    }
    throw new Error("Session expired. Please log in again.");
  }

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
  refresh_token: string;
}

export interface VoiceProfile {
  profile_id: string;
  user_id: string;
  name: string;
  reference_audio_path: string;
  embedding?: number[];
  created_at: string;
}

export interface InterviewSession {
  id: string;
  status: string;
  started_at?: string;
  ended_at?: string;
}

export interface ModeInfo {
  mode_id: string;
  display_name: string;
  description: string;
  icon: string;
  agent_classes: string[];
  default_agent: string;
  required_context: string[];
  ui_components: string[];
  default_view: string;
}

export interface DashboardStats {
  voice_profiles: number;
  face_registrations: number;
  interviews_completed: number;
  deepfake_detections: number;
}

export interface DeepfakeDetectionResult {
  is_deepfake: boolean;
  confidence: number;
  details: Record<string, unknown>;
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
    refresh: (refreshToken: string) =>
      request<{ access_token: string }>(`${API_BASE}/auth/refresh`, {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      }),
  },
  voice: {
    clone: (audioFile: File, userId?: string, name?: string) => {
      const formData = new FormData();
      formData.append("audio", audioFile);
      if (userId) formData.append("user_id", userId);
      if (name) formData.append("name", name);
      return request<{ profile_id: string }>(`${API_BASE}/voice/clone`, {
        method: "POST",
        body: formData,
      });
    },
    synthesize: (text: string, profileId: string, exaggeration?: number) =>
      request<{ audio_base64: string }>(`${API_BASE}/voice/synthesize`, {
        method: "POST",
        body: JSON.stringify({ text, profile_id: profileId, exaggeration: exaggeration ?? 0.5 }),
      }),
    profiles: (userId?: string) => {
      const params = userId ? `?user_id=${userId}` : "";
      return request<{ profiles: VoiceProfile[] }>(`${API_BASE}/voice/profiles${params}`);
    },
    tts: (text: string, voice?: string) =>
      request<{ audio_base64: string; duration_ms: number }>(`${API_BASE}/voice/tts`, {
        method: "POST",
        body: JSON.stringify({ text, voice: voice ?? "default" }),
      }),
  },
  proctoring: {
    registerFace: (profile: { user_id: string; photo_path: string }) =>
      request<{ user_id: string; message: string; embedding_stored: boolean }>(
        `${API_BASE}/proctoring/register-face`,
        { method: "POST", body: JSON.stringify(profile) }
      ),
    verify: (userId: string) =>
      request<{ verified: boolean; confidence: number }>(`${API_BASE}/proctoring/verify`, {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
      }),
    liveness: (userId: string) =>
      request<{ is_live: boolean; confidence: number; blink_detected: boolean; head_movement: boolean }>(
        `${API_BASE}/proctoring/liveness`,
        { method: "POST", body: JSON.stringify({ user_id: userId }) }
      ),
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
  modes: {
    list: () =>
      request<{ modes: ModeInfo[]; count: number }>(`${API_BASE}/api/modes/`),
    get: (modeId: string) =>
      request<ModeInfo>(`${API_BASE}/api/modes/${modeId}`),
    switch: (modeId: string, context?: Record<string, unknown>) =>
      request<{ success: boolean; mode: ModeInfo; message: string }>(
        `${API_BASE}/api/modes/switch`,
        {
          method: "POST",
          body: JSON.stringify({ mode_id: modeId, context }),
        }
      ),
  },
  deepfake: {
    detectVoice: (audioFile: File) => {
      const formData = new FormData();
      formData.append("audio", audioFile);
      return request<DeepfakeDetectionResult>(`${API_BASE}/deepfake/detect/voice`, {
        method: "POST",
        body: formData,
      });
    },
    detectVideo: (videoFile: File) => {
      const formData = new FormData();
      formData.append("video", videoFile);
      return request<DeepfakeDetectionResult>(`${API_BASE}/deepfake/detect/video`, {
        method: "POST",
        body: formData,
      });
    },
    detectCombined: (audioFile: File, videoFile: File) => {
      const formData = new FormData();
      formData.append("audio", audioFile);
      formData.append("video", videoFile);
      return request<DeepfakeDetectionResult>(`${API_BASE}/deepfake/detect/combined`, {
        method: "POST",
        body: formData,
      });
    },
  },
  analytics: {
    dashboard: () => request<DashboardStats>(`${API_BASE}/analytics/dashboard`),
    skillGaps: (scores: { category: string; overall: number }[]) =>
      request<{ category: string; current_score: number; target_score: number; gap: number; recommendations: string[] }[]>(
        `${API_BASE}/analytics/skill-gaps`,
        { method: "POST", body: JSON.stringify({ scores }) }
      ),
    performance: (sessionScores: { category: string; overall: number }[][]) =>
      request<{ total_sessions: number; average_score: number; improvement_rate: number; strongest_category: string; weakest_category: string }>(
        `${API_BASE}/analytics/performance`,
        { method: "POST", body: JSON.stringify({ session_scores: sessionScores }) }
      ),
  },
  scoring: {
    score: (data: { question: string; answer: string; category?: string }) =>
      request<{ confidence: number; clarity: number; relevance: number; response_time: number; overall: number; category: string }>(
        `${API_BASE}/scoring/score`,
        { method: "POST", body: JSON.stringify(data) }
      ),
    sessionSummary: () =>
      request<{ total_scored: number; average_confidence: number; average_clarity: number; average_relevance: number }>(
        `${API_BASE}/scoring/session/summary`
      ),
  },
  orchestrator: {
    generate: (data: { question: string; question_type?: string; candidate_profile?: Record<string, unknown> }) =>
      request<{ answer: string }>(`${API_BASE}/orchestrator/generate`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
  health: {
    check: () =>
      request<{ status: string; version: string; services: Record<string, string> }>(`${API_BASE}/health`),
  },
};
