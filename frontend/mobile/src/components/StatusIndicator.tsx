import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface StatusIndicatorProps {
  audioActive: boolean;
  videoActive: boolean;
  batteryLevel: number;
}

export function StatusIndicator({
  audioActive,
  videoActive,
  batteryLevel,
}: StatusIndicatorProps) {
  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <View style={styles.indicator}>
          <View
            testID="audio-indicator"
            style={[
              styles.dot,
              { backgroundColor: audioActive ? '#4CAF50' : '#f44336' },
            ]}
          />
          <Text style={styles.label}>Audio</Text>
        </View>

        <View style={styles.indicator}>
          <View
            testID="video-indicator"
            style={[
              styles.dot,
              { backgroundColor: videoActive ? '#4CAF50' : '#f44336' },
            ]}
          />
          <Text style={styles.label}>Video</Text>
        </View>

        <View style={styles.indicator}>
          <View
            testID="battery-indicator"
            style={[
              styles.dot,
              {
                backgroundColor:
                  batteryLevel > 20 ? '#4CAF50' : '#FF9800',
              },
            ]}
          />
          <Text style={styles.label}>{batteryLevel}%</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 12,
    marginHorizontal: 16,
    marginVertical: 4,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  indicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  label: {
    color: '#a0a0b0',
    fontSize: 13,
    fontWeight: '500',
  },
});
