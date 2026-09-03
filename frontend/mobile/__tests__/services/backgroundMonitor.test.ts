jest.mock('expo-av', () => ({
  Audio: {
    requestPermissionsAsync: jest.fn().mockResolvedValue({ status: 'granted' }),
    Recording: jest.fn().mockImplementation(() => ({
      prepareToRecordAsync: jest.fn(),
      startAsync: jest.fn(),
      stopAndUnloadAsync: jest.fn(),
      getURI: jest.fn().mockReturnValue('file:///test.wav'),
      setOnRecordingStatusUpdate: jest.fn(),
    })),
    RecordingOptionsPresets: {
      HIGH_QUALITY: {},
    },
    setAudioModeAsync: jest.fn(),
  },
}));

jest.mock('expo-camera', () => ({
  Camera: {
    requestCameraPermissionsAsync: jest.fn().mockResolvedValue({ status: 'granted', granted: true }),
  },
}));

jest.mock('../../src/services/apiClient', () => {
  return {
    ApiClient: jest.fn().mockImplementation(() => ({
      post: jest.fn().mockResolvedValue({ detected: false }),
      get: jest.fn(),
      setToken: jest.fn(),
    })),
  };
});

import { BackgroundMonitor } from '../../src/services/backgroundMonitor';

beforeEach(() => {
  jest.clearAllMocks();
});

describe('BackgroundMonitor', () => {
  describe('constructor', () => {
    it('initializes with default status', () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      expect(monitor.getStatus()).toEqual({
        audioActive: false,
        videoActive: false,
        batteryLevel: 100,
      });
    });

    it('stores API base URL', () => {
      const monitor = new BackgroundMonitor('http://custom:9000');
      expect(monitor['apiBaseUrl']).toBe('http://custom:9000');
    });
  });

  describe('requestPermissions', () => {
    it('requests audio permissions', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      const result = await monitor.requestPermissions();

      expect(result.audio).toBe(true);
    });

    it('requests camera permissions', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      const result = await monitor.requestPermissions();

      expect(result.camera).toBe(true);
    });

    it('returns false when permissions denied', async () => {
      const { Audio } = require('expo-av');
      Audio.requestPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });
      const monitor = new BackgroundMonitor('http://localhost:8000');
      const result = await monitor.requestPermissions();

      expect(result.audio).toBe(false);
    });
  });

  describe('start and stop', () => {
    it('marks audio as active on start', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      await monitor.start();

      const status = monitor.getStatus();
      expect(status.audioActive).toBe(true);
    });

    it('marks audio as inactive on stop', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      await monitor.start();
      await monitor.stop();

      const status = monitor.getStatus();
      expect(status.audioActive).toBe(false);
      expect(status.videoActive).toBe(false);
    });

    it('can be started only once', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      await monitor.start();
      await monitor.start();

      const status = monitor.getStatus();
      expect(status.audioActive).toBe(true);
    });
  });

  describe('onTriggerDetected callback', () => {
    it('accepts trigger detection callback', () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      const callback = jest.fn();
      monitor.onTriggerDetected(callback);

      expect(monitor['triggerCallback']).toBe(callback);
    });
  });

  describe('sendAudioChunk', () => {
    it('posts audio chunk to backend', async () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');

      await monitor.sendAudioChunk('base64audio');

      const { ApiClient } = require('../../src/services/apiClient');
      expect(ApiClient).toHaveBeenCalled();
    });
  });

  describe('setSamplingRate', () => {
    it('updates audio sampling interval', () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      monitor.setSamplingRate(2000);

      expect(monitor['audioSamplingMs']).toBe(2000);
    });

    it('rejects sampling rate below 500ms', () => {
      const monitor = new BackgroundMonitor('http://localhost:8000');
      monitor.setSamplingRate(100);

      expect(monitor['audioSamplingMs']).toBe(1000);
    });
  });
});
