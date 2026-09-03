import { FaceService } from '../../src/services/faceService';
import { ApiClient } from '../../src/services/apiClient';

const mockPost = jest.fn();

jest.mock('../../src/services/apiClient', () => {
  return {
    ApiClient: jest.fn().mockImplementation(() => ({
      post: mockPost,
    })),
  };
});

beforeEach(() => {
  mockPost.mockReset();
});

describe('FaceService', () => {
  const service = new FaceService('http://localhost:8000');

  describe('registerFace', () => {
    it('sends user_id and photo_path to /proctoring/register-face', async () => {
      mockPost.mockResolvedValueOnce({
        user_id: 'u1',
        message: 'Face profile registered successfully',
        embedding_stored: false,
      });

      const result = await service.registerFace('u1', '/path/to/photo.jpg');

      expect(mockPost).toHaveBeenCalledWith('/proctoring/register-face', {
        user_id: 'u1',
        photo_path: '/path/to/photo.jpg',
      });
      expect(result.message).toContain('registered');
    });
  });

  describe('verifyFace', () => {
    it('sends user_id and image_data to /proctoring/verify', async () => {
      mockPost.mockResolvedValueOnce({
        verified: true,
        confidence: 0.95,
      });

      const result = await service.verifyFace('u1', 'base64image');

      expect(mockPost).toHaveBeenCalledWith('/proctoring/verify', {
        user_id: 'u1',
        image_data: 'base64image',
      });
      expect(result.verified).toBe(true);
      expect(result.confidence).toBe(0.95);
    });
  });

  describe('checkLiveness', () => {
    it('sends user_id and image_data to /proctoring/liveness', async () => {
      mockPost.mockResolvedValueOnce({
        is_live: true,
        confidence: 0.9,
        blink_detected: true,
        head_movement: true,
      });

      const result = await service.checkLiveness('u1', 'base64frame');

      expect(mockPost).toHaveBeenCalledWith('/proctoring/liveness', {
        user_id: 'u1',
        image_data: 'base64frame',
      });
      expect(result.is_live).toBe(true);
      expect(result.blink_detected).toBe(true);
    });
  });
});
