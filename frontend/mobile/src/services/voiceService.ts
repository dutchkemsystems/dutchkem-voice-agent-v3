import { ApiClient } from './apiClient';
import type { VoiceProfile } from '../types';

interface CloneResponse {
  profile_id: string;
}

interface SynthesizeResponse {
  audio_base64: string;
  duration_ms: number;
}

interface ListProfilesResponse {
  profiles: VoiceProfile[];
}

interface TTSResponse {
  audio_base64: string;
  duration_ms: number;
}

export class VoiceService {
  private api: ApiClient;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.api = new ApiClient(baseUrl);
  }

  async cloneVoice(
    userId: string,
    audioData: string | Blob,
    name: string = ''
  ): Promise<CloneResponse> {
    const formData = new FormData();
    if (typeof audioData === 'string') {
      const blob = new Blob(
        [Uint8Array.from(atob(audioData), (c) => c.charCodeAt(0))],
        { type: 'audio/wav' }
      );
      formData.append('audio', blob, 'recording.wav');
    } else {
      formData.append('audio', audioData, 'recording.wav');
    }
    formData.append('user_id', userId);
    formData.append('name', name);
    return this.api.uploadFile<CloneResponse>('/voice/clone', formData);
  }

  async synthesize(
    text: string,
    profileId: string,
    exaggeration: number = 0.5
  ): Promise<SynthesizeResponse> {
    return this.api.post<SynthesizeResponse>('/voice/synthesize', {
      text,
      profile_id: profileId,
      exaggeration,
    });
  }

  async listProfiles(userId?: string): Promise<ListProfilesResponse> {
    const path = userId
      ? `/voice/profiles?user_id=${encodeURIComponent(userId)}`
      : '/voice/profiles';
    return this.api.get<ListProfilesResponse>(path);
  }

  async textToSpeech(
    text: string,
    voice: string = 'af_heart'
  ): Promise<TTSResponse> {
    return this.api.post<TTSResponse>('/voice/tts', { text, voice });
  }
}
