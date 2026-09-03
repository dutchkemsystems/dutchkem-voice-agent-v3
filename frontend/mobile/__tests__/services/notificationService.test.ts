jest.mock('expo-notifications', () => ({
  requestPermissionsAsync: jest.fn().mockResolvedValue({ status: 'granted' }),
  scheduleNotificationAsync: jest.fn().mockResolvedValue('notif-id'),
  setNotificationHandler: jest.fn(),
  addNotificationReceivedListener: jest.fn(),
  addNotificationResponseReceivedListener: jest.fn(),
}));

beforeEach(() => {
  jest.clearAllMocks();
});

import { NotificationService } from '../../src/services/notificationService';

describe('NotificationService', () => {
  describe('requestPermissions', () => {
    it('requests notification permissions', async () => {
      const service = new NotificationService();
      const granted = await service.requestPermissions();

      const Notifications = require('expo-notifications');
      expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
      expect(granted).toBe(true);
    });

    it('returns false when denied', async () => {
      const Notifications = require('expo-notifications');
      Notifications.requestPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });
      const service = new NotificationService();
      const granted = await service.requestPermissions();

      expect(granted).toBe(false);
    });
  });

  describe('initialize', () => {
    it('sets up notification handler', () => {
      const service = new NotificationService();
      service.initialize();

      const Notifications = require('expo-notifications');
      expect(Notifications.setNotificationHandler).toHaveBeenCalledWith({
        handleNotification: expect.any(Function),
      });
    });

    it('registers received listener', () => {
      const service = new NotificationService();
      service.initialize();

      const Notifications = require('expo-notifications');
      expect(Notifications.addNotificationReceivedListener).toHaveBeenCalled();
    });

    it('registers response listener', () => {
      const service = new NotificationService();
      service.initialize();

      const Notifications = require('expo-notifications');
      expect(Notifications.addNotificationResponseReceivedListener).toHaveBeenCalled();
    });
  });

  describe('sendInterviewTrigger', () => {
    it('sends interview trigger notification', async () => {
      const service = new NotificationService();

      await service.sendInterviewTrigger(0.95, 'voice_match');

      const Notifications = require('expo-notifications');
      expect(Notifications.scheduleNotificationAsync).toHaveBeenCalledWith({
        content: {
          title: 'Interview Detected',
          body: expect.stringContaining('Interview trigger detected'),
          data: expect.objectContaining({
            type: 'interview_trigger',
            confidence: 0.95,
          }),
        },
        trigger: null,
      });
    });
  });

  describe('sendBackgroundAlert', () => {
    it('sends background monitoring alert', async () => {
      const service = new NotificationService();

      await service.sendBackgroundAlert('Audio monitoring active');

      const Notifications = require('expo-notifications');
      expect(Notifications.scheduleNotificationAsync).toHaveBeenCalledWith({
        content: {
          title: 'Background Monitoring',
          body: 'Audio monitoring active',
          data: expect.objectContaining({ type: 'background_alert' }),
        },
        trigger: null,
      });
    });
  });

  describe('onNotificationReceived', () => {
    it('registers callback for notification events', () => {
      const service = new NotificationService();
      const callback = jest.fn();
      service.onNotificationReceived(callback);

      expect(service['receivedCallback']).toBe(callback);
    });
  });
});
