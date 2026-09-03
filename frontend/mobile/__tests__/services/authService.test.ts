import { AuthService } from '../../src/services/authService';
import { ApiClient } from '../../src/services/apiClient';

const mockGet = jest.fn();
const mockPost = jest.fn();

jest.mock('../../src/services/apiClient', () => {
  return {
    ApiClient: jest.fn().mockImplementation(() => ({
      get: mockGet,
      post: mockPost,
      setToken: jest.fn(),
    })),
  };
});

beforeEach(() => {
  mockGet.mockReset();
  mockPost.mockReset();
});

describe('AuthService', () => {
  const service = new AuthService('http://localhost:8000');

  describe('login', () => {
    it('sends email and password to /auth/login', async () => {
      mockPost.mockResolvedValueOnce({
        access_token: 'at1',
        refresh_token: 'rt1',
      });

      const result = await service.login('user@test.com', 'password123');

      expect(mockPost).toHaveBeenCalledWith('/auth/login', {
        email: 'user@test.com',
        password: 'password123',
      });
      expect(result).toEqual({
        access_token: 'at1',
        refresh_token: 'rt1',
      });
    });

    it('returns token response', async () => {
      mockPost.mockResolvedValueOnce({
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
      });

      const result = await service.login('a@b.com', 'pass');
      expect(result.access_token).toBe('token');
      expect(result.refresh_token).toBe('refresh');
    });
  });

  describe('register', () => {
    it('sends registration data to /auth/register', async () => {
      mockPost.mockResolvedValueOnce({
        id: 'user1',
        email: 'new@test.com',
        username: 'newuser',
      });

      const result = await service.register('new@test.com', 'newuser', 'pass1234');

      expect(mockPost).toHaveBeenCalledWith('/auth/register', {
        email: 'new@test.com',
        username: 'newuser',
        password: 'pass1234',
      });
      expect(result.id).toBe('user1');
    });
  });

  describe('getProfile', () => {
    it('fetches user profile from /auth/me', async () => {
      mockGet.mockResolvedValueOnce({
        id: 'u1',
        email: 'a@b.com',
        username: 'user1',
      });

      const result = await service.getProfile();

      expect(mockGet).toHaveBeenCalledWith('/auth/me');
      expect(result.id).toBe('u1');
    });
  });

  describe('refreshToken', () => {
    it('sends refresh token to /auth/refresh', async () => {
      mockPost.mockResolvedValueOnce({
        access_token: 'new-access',
        token_type: 'bearer',
      });

      const result = await service.refreshToken('my-refresh-token');

      expect(mockPost).toHaveBeenCalledWith('/auth/refresh', {
        refresh_token: 'my-refresh-token',
      });
      expect(result.access_token).toBe('new-access');
    });
  });
});
