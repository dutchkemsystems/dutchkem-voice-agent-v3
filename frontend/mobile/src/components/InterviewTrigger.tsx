import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';

interface InterviewTriggerProps {
  isActive: boolean;
  confidence: number;
  onPress: () => void;
}

export function InterviewTrigger({
  isActive,
  confidence,
  onPress,
}: InterviewTriggerProps) {
  const confidencePercent = Math.round(confidence * 100);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View
          style={[
            styles.statusDot,
            { backgroundColor: isActive ? '#4CAF50' : '#9E9E9E' },
          ]}
        />
        <Text style={styles.title}>Interview Detected</Text>
      </View>

      <Text style={styles.confidence}>
        {isActive ? `${confidencePercent}% Confidence` : 'Not Active'}
      </Text>

      <TouchableOpacity
        style={[styles.button, isActive && styles.buttonActive]}
        onPress={onPress}
        disabled={!isActive}
        accessibilityRole="button"
      >
        <Text style={[styles.buttonText, isActive && styles.buttonTextActive]}>
          {isActive ? 'Start Interview' : 'Waiting...'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1a2e',
    borderRadius: 16,
    padding: 20,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  title: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  confidence: {
    color: '#a0a0b0',
    fontSize: 14,
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#2a2a4e',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  buttonActive: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonTextActive: {
    color: '#ffffff',
  },
});
