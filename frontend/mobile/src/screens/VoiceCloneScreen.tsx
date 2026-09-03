import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Audio } from 'expo-av';
import { VoiceService } from '../services/voiceService';

export default function VoiceCloneScreen() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recorded, setRecorded] = useState(false);
  const [cloning, setCloning] = useState(false);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [recordingDuration, setRecordingDuration] = useState(0);

  const voiceService = new VoiceService();

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        Alert.alert('Permission Required', 'Microphone access is needed for voice cloning');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
      setRecorded(false);
      setRecordingDuration(0);

      const interval = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);

      rec.setOnRecordingStatusUpdate((status) => {
        if (!status.isRecording) {
          clearInterval(interval);
        }
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

      const uri = recording.getURI();
      if (uri) {
        setRecorded(true);
      }
      setRecording(null);
    } catch (error) {
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const cloneVoice = async () => {
    if (!recording) return;

    setCloning(true);
    try {
      const uri = recording.getURI();
      if (!uri) {
        Alert.alert('Error', 'No recording found');
        return;
      }

      const result = await voiceService.cloneVoice('current-user', uri, 'My Voice Clone');
      setProfileId(result.profile_id);
      Alert.alert('Success', `Voice clone created! Profile ID: ${result.profile_id}`);
    } catch (error: any) {
      Alert.alert('Clone Failed', error.message || 'Failed to clone voice');
    } finally {
      setCloning(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Voice Clone Setup</Text>
      <Text style={styles.subtitle}>
        Record 5-10 seconds of your voice to create a clone
      </Text>

      <View style={styles.recordingCard}>
        <View style={styles.waveform}>
          {Array.from({ length: 20 }).map((_, i) => (
            <View
              key={i}
              style={[
                styles.bar,
                recording && { height: Math.random() * 40 + 10 },
              ]}
            />
          ))}
        </View>

        <Text style={styles.duration}>
          {recordingDuration}s / 10s
        </Text>

        <TouchableOpacity
          style={[
            styles.recordButton,
            recording && styles.recordButtonActive,
          ]}
          onPress={recording ? stopRecording : startRecording}
        >
          <View
            style={[
              styles.recordDot,
              recording && styles.recordDotActive,
            ]}
          />
          <Text style={styles.recordText}>
            {recording ? 'Stop Recording' : 'Start Recording'}
          </Text>
        </TouchableOpacity>
      </View>

      {recorded && (
        <TouchableOpacity
          style={[styles.cloneButton, cloning && styles.cloneButtonDisabled]}
          onPress={cloneVoice}
          disabled={cloning}
        >
          {cloning ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.cloneText}>Clone My Voice</Text>
          )}
        </TouchableOpacity>
      )}

      {profileId && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Voice Clone Ready</Text>
          <Text style={styles.resultId}>Profile: {profileId}</Text>
        </View>
      )}
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
    marginBottom: 8,
  },
  subtitle: {
    color: '#a0a0b0',
    fontSize: 16,
    marginBottom: 24,
  },
  recordingCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  waveform: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 60,
    marginBottom: 16,
  },
  bar: {
    width: 4,
    height: 10,
    backgroundColor: '#4CAF50',
    borderRadius: 2,
    marginHorizontal: 2,
  },
  duration: {
    color: '#a0a0b0',
    fontSize: 14,
    marginBottom: 16,
  },
  recordButton: {
    backgroundColor: '#2a2a4e',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 32,
    flexDirection: 'row',
    alignItems: 'center',
  },
  recordButtonActive: {
    backgroundColor: '#f44336',
  },
  recordDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#f44336',
    marginRight: 8,
  },
  recordDotActive: {
    backgroundColor: '#ffffff',
  },
  recordText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  cloneButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  cloneButtonDisabled: {
    opacity: 0.6,
  },
  cloneText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  resultCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
  },
  resultTitle: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  resultId: {
    color: '#a0a0b0',
    fontSize: 14,
  },
});
