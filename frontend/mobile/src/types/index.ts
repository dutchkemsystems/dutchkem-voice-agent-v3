export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  voice_profile_id?: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface VoiceProfile {
  profile_id: string;
  user_id: string;
  name: string;
  reference_audio_path: string;
  created_at: string;
}

export interface FaceVerifyResult {
  verified: boolean;
  confidence: number;
}

export interface LivenessResult {
  is_live: boolean;
  confidence: number;
  blink_detected: boolean;
  head_movement: boolean;
}

export interface InterviewTrigger {
  detected: boolean;
  confidence: number;
  timestamp: number;
}

export interface MonitorStatus {
  audioActive: boolean;
  videoActive: boolean;
  batteryLevel: number;
}
