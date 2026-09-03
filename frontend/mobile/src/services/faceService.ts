import { ApiClient } from './apiClient';
import type { FaceVerifyResult, LivenessResult } from '../types';

interface RegisterFaceResponse {
  user_id: string;
  message: string;
  embedding_stored: boolean;
}

export class FaceService {
  private api: ApiClient;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.api = new ApiClient(baseUrl);
  }

  async registerFace(
    userId: string,
    photoPath: string
  ): Promise<RegisterFaceResponse> {
    return this.api.post<RegisterFaceResponse>('/proctoring/register-face', {
      user_id: userId,
      photo_path: photoPath,
    });
  }

  async verifyFace(
    userId: string,
    imageData: string
  ): Promise<FaceVerifyResult> {
    return this.api.post<FaceVerifyResult>('/proctoring/verify', {
      user_id: userId,
      image_data: imageData,
    });
  }

  async checkLiveness(
    userId: string,
    imageData: string
  ): Promise<LivenessResult> {
    return this.api.post<LivenessResult>('/proctoring/liveness', {
      user_id: userId,
      image_data: imageData,
    });
  }
}
