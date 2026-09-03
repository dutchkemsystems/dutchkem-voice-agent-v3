import { ApiClient } from './apiClient';
import type { User, TokenResponse } from '../types';

export class AuthService {
  private api: ApiClient;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.api = new ApiClient(baseUrl);
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    return this.api.post<TokenResponse>('/auth/login', { email, password });
  }

  async register(
    email: string,
    username: string,
    password: string
  ): Promise<User> {
    return this.api.post<User>('/auth/register', {
      email,
      username,
      password,
    });
  }

  async getProfile(): Promise<User> {
    return this.api.get<User>('/auth/me');
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    return this.api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
  }

  setToken(token: string): void {
    this.api.setToken(token);
  }
}
