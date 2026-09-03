import * as Notifications from 'expo-notifications';

type NotificationCallback = (notification: Notifications.Notification) => void;

export class NotificationService {
  private receivedCallback: NotificationCallback | null = null;

  async requestPermissions(): Promise<boolean> {
    const { status } = await Notifications.requestPermissionsAsync();
    return status === 'granted';
  }

  initialize(): void {
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });

    Notifications.addNotificationReceivedListener((notification) => {
      if (this.receivedCallback) {
        this.receivedCallback(notification);
      }
    });

    Notifications.addNotificationResponseReceivedListener((response) => {
      const data = response.notification.request.content.data;
      if (data?.type === 'interview_trigger' && this.receivedCallback) {
        this.receivedCallback(response.notification);
      }
    });
  }

  async sendInterviewTrigger(
    confidence: number,
    source: string
  ): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Interview Detected',
        body: `Interview trigger detected with ${Math.round(confidence * 100)}% confidence via ${source}`,
        data: {
          type: 'interview_trigger',
          confidence,
          source,
          timestamp: Date.now(),
        },
      },
      trigger: null,
    });
  }

  async sendBackgroundAlert(message: string): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Background Monitoring',
        body: message,
        data: {
          type: 'background_alert',
          timestamp: Date.now(),
        },
      },
      trigger: null,
    });
  }

  onNotificationReceived(callback: NotificationCallback): void {
    this.receivedCallback = callback;
  }
}
