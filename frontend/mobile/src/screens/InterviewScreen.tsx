import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { StatusIndicator } from '../components/StatusIndicator';
import { BackgroundMonitor } from '../services/backgroundMonitor';
import { NotificationService } from '../services/notificationService';

export default function InterviewScreen() {
  const [isActive, setIsActive] = useState(false);
  const [duration, setDuration] = useState(0);
  const [events, setEvents] = useState<string[]>([]);

  const monitor = new BackgroundMonitor();
  const notifications = new NotificationService();

  useEffect(() => {
    notifications.initialize();
    return () => {
      monitor.stop();
    };
  }, []);

  const toggleInterview = async () => {
    if (isActive) {
      await monitor.stop();
      setIsActive(false);
      addEvent('Interview session ended');
    } else {
      try {
        await monitor.start();
        setIsActive(true);
        setDuration(0);
        addEvent('Interview session started');
        await notifications.sendInterviewTrigger(1.0, 'manual');
      } catch (error) {
        addEvent('Failed to start monitoring');
      }
    }
  };

  const addEvent = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setEvents((prev) => [`[${timestamp}] ${message}`, ...prev]);
  };

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isActive]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Interview Session</Text>

      <StatusIndicator
        audioActive={isActive}
        videoActive={false}
        batteryLevel={80}
      />

      <View style={styles.timerCard}>
        <Text style={styles.timer}>{formatDuration(duration)}</Text>
        <Text style={styles.timerLabel}>
          {isActive ? 'In Progress' : 'Ready'}
        </Text>
      </View>

      <TouchableOpacity
        style={[styles.mainButton, isActive && styles.mainButtonActive]}
        onPress={toggleInterview}
      >
        <Text style={styles.mainButtonText}>
          {isActive ? 'End Interview' : 'Start Interview'}
        </Text>
      </TouchableOpacity>

      <View style={styles.eventLog}>
        <Text style={styles.eventLogTitle}>Event Log</Text>
        <ScrollView style={styles.eventList}>
          {events.length === 0 ? (
            <Text style={styles.noEvents}>No events yet</Text>
          ) : (
            events.map((event, index) => (
              <Text key={index} style={styles.eventItem}>
                {event}
              </Text>
            ))
          )}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
    paddingTop: 60,
    paddingHorizontal: 16,
  },
  title: {
    color: '#ffffff',
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 16,
  },
  timerCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginVertical: 16,
  },
  timer: {
    color: '#4CAF50',
    fontSize: 48,
    fontWeight: '900',
    fontVariant: ['tabular-nums'],
  },
  timerLabel: {
    color: '#a0a0b0',
    fontSize: 16,
    marginTop: 8,
  },
  mainButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
  },
  mainButtonActive: {
    backgroundColor: '#f44336',
  },
  mainButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  eventLog: {
    flex: 1,
    marginTop: 16,
  },
  eventLogTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 8,
  },
  eventList: {
    flex: 1,
  },
  noEvents: {
    color: '#555',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 20,
  },
  eventItem: {
    color: '#a0a0b0',
    fontSize: 13,
    paddingVertical: 4,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
});
