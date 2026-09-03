import { ApiClient } from '../../src/services/apiClient';

const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

describe('ApiClient', () => {
  const baseUrl = 'http://localhost:8000';
  const client = new ApiClient(baseUrl);

  describe('constructor', () => {
    it('stores base URL', () => {
      expect(client['baseUrl']).toBe(baseUrl);
    });

    it('defaults to localhost:8000', () => {
      const defaultClient = new ApiClient();
      expect(defaultClient['baseUrl']).toBe('http://localhost:8000');
    });
  });

  describe('setToken', () => {
    it('stores auth token', () => {
      client.setToken('my-token');
      expect(client['token']).toBe('my-token');
    });
  });

  describe('get', () => {
    it('makes GET request with correct URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      await client.get('/health');
      expect(mockFetch).toHaveBeenCalledWith(
        `${baseUrl}/health`,
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('includes Authorization header when token is set', async () => {
      client.setToken('test-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await client.get('/auth/me');
      expect(mockFetch).toHaveBeenCalledWith(
        `${baseUrl}/auth/me`,
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('throws on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(client.get('/auth/me')).rejects.toThrow('Unauthorized');
    });
  });

  describe('post', () => {
    it('makes POST request with JSON body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'abc' }),
      });

      const body = { email: 'test@test.com', password: 'pass1234' };
      await client.post('/auth/login', body);

      expect(mockFetch).toHaveBeenCalledWith(
        `${baseUrl}/auth/login`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(body),
        })
      );
    });

    it('returns parsed JSON response', async () => {
      const responseData = { access_token: 'token123' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => responseData,
      });

      const result = await client.post('/auth/login', {});
      expect(result).toEqual(responseData);
    });

    it('throws error with detail on failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'User already exists' }),
      });

      await expect(
        client.post('/auth/register', { email: 'a@b.com' })
      ).rejects.toThrow('User already exists');
    });
  });

  describe('uploadFile', () => {
    it('makes POST request with FormData', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ profile_id: '123' }),
      });

      const formData = new FormData();
      formData.append('audio', 'test');
      formData.append('user_id', 'u1');

      await client.uploadFile('/voice/clone', formData);

      expect(mockFetch).toHaveBeenCalledWith(
        `${baseUrl}/voice/clone`,
        expect.objectContaining({
          method: 'POST',
          body: formData,
        })
      );
    });

    it('includes auth token for file uploads', async () => {
      client.setToken('upload-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ profile_id: '456' }),
      });

      const formData = new FormData();
      await client.uploadFile('/voice/clone', formData);

      expect(mockFetch).toHaveBeenCalledWith(
        `${baseUrl}/voice/clone`,
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer upload-token',
          }),
        })
      );
    });
  });
});
