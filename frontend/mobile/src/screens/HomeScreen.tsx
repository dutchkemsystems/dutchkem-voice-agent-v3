import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { InterviewTrigger } from '../components/InterviewTrigger';
import { StatusIndicator } from '../components/StatusIndicator';
import { BackgroundMonitor } from '../services/backgroundMonitor';

export default function HomeScreen({ navigation }: { navigation: any }) {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [triggerActive, setTriggerActive] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalSessions: 0,
    audioLevel: 0,
    facesDetected: 0,
  });

  const monitor = new BackgroundMonitor();

  useEffect(() => {
    return () => {
      monitor.stop();
    };
  }, []);

  const toggleMonitoring = async () => {
    if (isMonitoring) {
      await monitor.stop();
      setIsMonitoring(false);
    } else {
      try {
        await monitor.start();
        setIsMonitoring(true);
      } catch (error) {
        console.error('Failed to start monitoring:', error);
      }
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Text style={styles.greeting}>Dutchkem Voice Agent</Text>
        <Text style={styles.subtitle}>Interview Detection System</Text>

        <StatusIndicator
          audioActive={isMonitoring}
          videoActive={false}
          batteryLevel={85}
        />

        <InterviewTrigger
          isActive={triggerActive}
          confidence={confidence}
          onPress={() => navigation.navigate('Interview')}
        />

        <View style={styles.statsContainer}>
          <Text style={styles.statsTitle}>Session Statistics</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.totalSessions}</Text>
              <Text style={styles.statLabel}>Sessions</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.audioLevel}</Text>
              <Text style={styles.statLabel}>Audio Level</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.facesDetected}</Text>
              <Text style={styles.statLabel}>Faces</Text>
            </View>
          </View>
        </View>

        <View style={styles.quickActions}>
          <Text style={styles.statsTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            <View
              style={styles.actionCard}
              onTouchEnd={() => navigation.navigate('VoiceSetup')}
            >
              <Text style={styles.actionIcon}>🎤</Text>
              <Text style={styles.actionLabel}>Voice Clone</Text>
            </View>
            <View
              style={styles.actionCard}
              onTouchEnd={() => navigation.navigate('FaceRegistration')}
            >
              <Text style={styles.actionIcon}>📷</Text>
              <Text style={styles.actionLabel}>Face Setup</Text>
            </View>
            <View
              style={styles.actionCard}
              onTouchEnd={() => navigation.navigate('Profile')}
            >
              <Text style={styles.actionIcon}>👤</Text>
              <Text style={styles.actionLabel}>Profile</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  scrollContent: {
    paddingTop: 60,
    paddingBottom: 30,
  },
  greeting: {
    color: '#ffffff',
    fontSize: 28,
    fontWeight: '800',
    paddingHorizontal: 16,
  },
  subtitle: {
    color: '#a0a0b0',
    fontSize: 16,
    paddingHorizontal: 16,
    marginBottom: 20,
  },
  statsContainer: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  statsTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    color: '#4CAF50',
    fontSize: 24,
    fontWeight: '800',
  },
  statLabel: {
    color: '#a0a0b0',
    fontSize: 12,
    marginTop: 4,
  },
  quickActions: {
    marginHorizontal: 16,
    marginTop: 8,
  },
  actionsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    width: '30%',
  },
  actionIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  actionLabel: {
    color: '#a0a0b0',
    fontSize: 12,
    fontWeight: '600',
  },
});
