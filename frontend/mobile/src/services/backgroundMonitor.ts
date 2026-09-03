import { Audio } from 'expo-av';
import { Camera } from 'expo-camera';
import { ApiClient } from './apiClient';
import type { MonitorStatus } from '../types';

type TriggerCallback = (confidence: number, source: string) => void;

export class BackgroundMonitor {
  private apiBaseUrl: string;
  private api: ApiClient;
  private isRunning = false;
  private audioRecording: Audio.Recording | null = null;
  private triggerCallback: TriggerCallback | null = null;
  private audioSamplingMs = 1000;
  private audioInterval: ReturnType<typeof setInterval> | null = null;
  private status: MonitorStatus = {
    audioActive: false,
    videoActive: false,
    batteryLevel: 100,
  };

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.apiBaseUrl = baseUrl;
    this.api = new ApiClient(baseUrl);
  }

  getStatus(): MonitorStatus {
    return { ...this.status };
  }

  async requestPermissions(): Promise<{ audio: boolean; camera: boolean }> {
    const audioPerm = await Audio.requestPermissionsAsync();
    const cameraPerm = await Camera.requestCameraPermissionsAsync();

    return {
      audio: audioPerm.status === 'granted',
      camera: cameraPerm.granted,
    };
  }

  async start(): Promise<void> {
    if (this.isRunning) return;

    const permissions = await this.requestPermissions();
    if (!permissions.audio) {
      throw new Error('Audio permission is required for background monitoring');
    }

    this.isRunning = true;

    try {
      await this.startAudioMonitoring();
    } catch {
      this.status.audioActive = false;
    }
  }

  private async startAudioMonitoring(): Promise<void> {
    const recording = new Audio.Recording();
    await recording.prepareToRecordAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY
    );
    await recording.startAsync();
    this.audioRecording = recording;
    this.status.audioActive = true;

    this.audioInterval = setInterval(() => {
      this.processAudioChunk();
    }, this.audioSamplingMs);
  }

  private async processAudioChunk(): Promise<void> {
    if (!this.isRunning || !this.audioRecording) return;

    try {
      const uri = this.audioRecording.getURI();
      if (uri) {
        await this.api.post('/background/audio/chunk', {
          audio_data: uri,
          timestamp: Date.now(),
        });
      }
    } catch {
      // Chunk processing failure should not stop monitoring
    }
  }

  async sendAudioChunk(audioBase64: string): Promise<void> {
    await this.api.post('/background/audio/chunk', {
      audio_data: audioBase64,
      timestamp: Date.now(),
    });
  }

  async stop(): Promise<void> {
    this.isRunning = false;
    this.status.audioActive = false;
    this.status.videoActive = false;

    if (this.audioInterval) {
      clearInterval(this.audioInterval);
      this.audioInterval = null;
    }

    if (this.audioRecording) {
      try {
        await this.audioRecording.stopAndUnloadAsync();
      } catch {
        // Ignore errors during stop
      }
      this.audioRecording = null;
    }
  }

  onTriggerDetected(callback: TriggerCallback): void {
    this.triggerCallback = callback;
  }

  setSamplingRate(ms: number): void {
    if (ms < 500) return;
    this.audioSamplingMs = ms;

    if (this.audioInterval) {
      clearInterval(this.audioInterval);
      this.audioInterval = setInterval(() => {
        this.processAudioChunk();
      }, this.audioSamplingMs);
    }
  }
}
