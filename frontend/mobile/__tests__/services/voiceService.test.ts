jest.mock('../../src/services/apiClient', () => {
  return {
    ApiClient: jest.fn().mockImplementation(() => ({
      post: jest.fn().mockResolvedValue({ profile_id: 'vp1' }),
      get: jest.fn().mockResolvedValue({ profiles: [] }),
      uploadFile: jest.fn().mockResolvedValue({ profile_id: 'vp1' }),
    })),
  };
});

import { VoiceService } from '../../src/services/voiceService';

beforeEach(() => {
  jest.clearAllMocks();
});

describe('VoiceService', () => {
  describe('cloneVoice', () => {
    it('uploads audio file with user_id to /voice/clone', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockUploadFile = jest.fn().mockResolvedValue({ profile_id: 'vp1' });
      ApiClient.mockImplementation(() => ({
        post: jest.fn(),
        get: jest.fn(),
        uploadFile: mockUploadFile,
      }));

      const service = new VoiceService('http://localhost:8000');
      const validBase64 = Buffer.from('fake-audio-data').toString('base64');
      const result = await service.cloneVoice('u1', validBase64, 'My Voice');

      expect(result.profile_id).toBe('vp1');
      expect(mockUploadFile).toHaveBeenCalled();
    });

    it('handles Blob audio data', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockUploadFile = jest.fn().mockResolvedValue({ profile_id: 'vp1' });
      ApiClient.mockImplementation(() => ({
        post: jest.fn(),
        get: jest.fn(),
        uploadFile: mockUploadFile,
      }));

      const service = new VoiceService('http://localhost:8000');
      const blob = new Blob(['audio'], { type: 'audio/wav' });
      const result = await service.cloneVoice('u1', blob, 'Test');

      expect(result.profile_id).toBe('vp1');
      expect(mockUploadFile).toHaveBeenCalled();
    });
  });

  describe('synthesize', () => {
    it('sends text and profile_id to /voice/synthesize', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockPost = jest.fn().mockResolvedValue({ audio_base64: 'base64data', duration_ms: 5000 });
      ApiClient.mockImplementation(() => ({
        post: mockPost,
        get: jest.fn(),
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      const result = await service.synthesize('Hello world', 'profile1');

      expect(mockPost).toHaveBeenCalledWith('/voice/synthesize', {
        text: 'Hello world',
        profile_id: 'profile1',
        exaggeration: 0.5,
      });
      expect(result.audio_base64).toBe('base64data');
      expect(result.duration_ms).toBe(5000);
    });

    it('accepts custom exaggeration', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockPost = jest.fn().mockResolvedValue({ audio_base64: 'x', duration_ms: 0 });
      ApiClient.mockImplementation(() => ({
        post: mockPost,
        get: jest.fn(),
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      await service.synthesize('Hi', 'p1', 0.8);

      expect(mockPost).toHaveBeenCalledWith(
        '/voice/synthesize',
        expect.objectContaining({ exaggeration: 0.8 })
      );
    });
  });

  describe('listProfiles', () => {
    it('fetches profiles from /voice/profiles', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockGet = jest.fn().mockResolvedValue({
        profiles: [
          { profile_id: 'p1', user_id: 'u1', name: 'Voice 1' },
          { profile_id: 'p2', user_id: 'u1', name: 'Voice 2' },
        ],
      });
      ApiClient.mockImplementation(() => ({
        post: jest.fn(),
        get: mockGet,
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      const result = await service.listProfiles('u1');

      expect(mockGet).toHaveBeenCalledWith('/voice/profiles?user_id=u1');
      expect(result.profiles).toHaveLength(2);
    });

    it('fetches all profiles when no user_id given', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockGet = jest.fn().mockResolvedValue({ profiles: [] });
      ApiClient.mockImplementation(() => ({
        post: jest.fn(),
        get: mockGet,
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      await service.listProfiles();

      expect(mockGet).toHaveBeenCalledWith('/voice/profiles');
    });
  });

  describe('textToSpeech', () => {
    it('sends text and voice to /voice/tts', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockPost = jest.fn().mockResolvedValue({ audio_base64: 'tts-data', duration_ms: 3000 });
      ApiClient.mockImplementation(() => ({
        post: mockPost,
        get: jest.fn(),
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      const result = await service.textToSpeech('Hello', 'nigerian');

      expect(mockPost).toHaveBeenCalledWith('/voice/tts', {
        text: 'Hello',
        voice: 'nigerian',
      });
      expect(result.audio_base64).toBe('tts-data');
    });

    it('defaults voice to af_heart', async () => {
      const { ApiClient } = require('../../src/services/apiClient');
      const mockPost = jest.fn().mockResolvedValue({ audio_base64: '', duration_ms: 0 });
      ApiClient.mockImplementation(() => ({
        post: mockPost,
        get: jest.fn(),
        uploadFile: jest.fn(),
      }));

      const service = new VoiceService('http://localhost:8000');
      await service.textToSpeech('Test');

      expect(mockPost).toHaveBeenCalledWith('/voice/tts', {
        text: 'Test',
        voice: 'af_heart',
      });
    });
  });
});
