import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { FaceService } from '../services/faceService';

export default function FaceRegistrationScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [captured, setCaptured] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [registered, setRegistered] = useState(false);
  const cameraRef = useRef<any>(null);

  const faceService = new FaceService();

  const capturePhoto = async () => {
    if (!cameraRef.current) return;

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
      });
      setCaptured(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to capture photo');
    }
  };

  const registerFace = async () => {
    setRegistering(true);
    try {
      const result = await faceService.registerFace(
        'current-user',
        '/tmp/face-photo.jpg'
      );
      setRegistered(true);
      Alert.alert('Success', result.message);
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message || 'Failed to register face');
    } finally {
      setRegistering(false);
    }
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Camera Permission Required</Text>
        <Text style={styles.subtitle}>
          We need camera access for face registration and liveness detection
        </Text>
        <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
          <Text style={styles.permissionText}>Grant Camera Access</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Face Registration</Text>
      <Text style={styles.subtitle}>
        Position your face in the frame for registration
      </Text>

      <View style={styles.cameraContainer}>
        <CameraView style={styles.camera} ref={cameraRef} facing="front">
          <View style={styles.overlay}>
            <View style={styles.faceGuide} />
          </View>
        </CameraView>
      </View>

      <View style={styles.instructions}>
        <Text style={styles.instructionText}>
          {captured
            ? 'Photo captured! Ready to register.'
            : 'Center your face and tap to capture'}
        </Text>
      </View>

      <View style={styles.actions}>
        {!captured ? (
          <TouchableOpacity style={styles.captureButton} onPress={capturePhoto}>
            <View style={styles.captureDot} />
          </TouchableOpacity>
        ) : (
          <>
            <TouchableOpacity
              style={styles.retakeButton}
              onPress={() => setCaptured(false)}
            >
              <Text style={styles.retakeText}>Retake</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.registerButton, registering && styles.registerButtonDisabled]}
              onPress={registerFace}
              disabled={registering}
            >
              {registering ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.registerText}>Register Face</Text>
              )}
            </TouchableOpacity>
          </>
        )}
      </View>

      {registered && (
        <View style={styles.successCard}>
          <Text style={styles.successTitle}>Face Registered</Text>
          <Text style={styles.successText}>
            Your face is now registered for liveness detection and interview verification.
          </Text>
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
    marginBottom: 16,
  },
  cameraContainer: {
    borderRadius: 16,
    overflow: 'hidden',
    height: 300,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceGuide: {
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  instructions: {
    alignItems: 'center',
    marginVertical: 16,
  },
  instructionText: {
    color: '#a0a0b0',
    fontSize: 14,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
  },
  captureButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 4,
    borderColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureDot: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#4CAF50',
  },
  retakeButton: {
    backgroundColor: '#2a2a4e',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
  },
  retakeText: {
    color: '#a0a0b0',
    fontSize: 16,
    fontWeight: '600',
  },
  registerButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
  },
  registerButtonDisabled: {
    opacity: 0.6,
  },
  registerText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  permissionButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  permissionText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  successCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
  },
  successTitle: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  successText: {
    color: '#a0a0b0',
    fontSize: 14,
  },
});
