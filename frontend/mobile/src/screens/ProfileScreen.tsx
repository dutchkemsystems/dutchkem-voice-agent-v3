import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { AuthService } from '../services/authService';
import { VoiceService } from '../services/voiceService';
import type { User, VoiceProfile } from '../types';

export default function ProfileScreen({ navigation }: { navigation: any }) {
  const [user, setUser] = useState<User | null>(null);
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);

  const authService = new AuthService();
  const voiceService = new VoiceService();

  useEffect(() => {
    loadProfile();
    loadProfiles();
  }, []);

  const loadProfile = async () => {
    try {
      const profile = await authService.getProfile();
      setUser(profile);
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const loadProfiles = async () => {
    try {
      const result = await voiceService.listProfiles();
      setProfiles(result.profiles);
    } catch (error) {
      console.error('Failed to load profiles:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Profile</Text>

      {user && (
        <View style={styles.userCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {user.username.charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={styles.username}>{user.username}</Text>
          <Text style={styles.email}>{user.email}</Text>
          <Text style={styles.memberSince}>
            Member since {new Date(user.created_at).toLocaleDateString()}
          </Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Setup</Text>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('VoiceSetup')}
        >
          <Text style={styles.menuIcon}>🎤</Text>
          <View style={styles.menuContent}>
            <Text style={styles.menuLabel}>Voice Clone Setup</Text>
            <Text style={styles.menuDescription}>
              {profiles.length > 0
                ? `${profiles.length} voice profile(s) configured`
                : 'No voice profiles yet'}
            </Text>
          </View>
          <Text style={styles.menuArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('FaceRegistration')}
        >
          <Text style={styles.menuIcon}>📷</Text>
          <View style={styles.menuContent}>
            <Text style={styles.menuLabel}>Face Registration</Text>
            <Text style={styles.menuDescription}>
              Register your face for liveness detection
            </Text>
          </View>
          <Text style={styles.menuArrow}>›</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Voice Profiles</Text>
        {profiles.length === 0 ? (
          <Text style={styles.emptyText}>No voice profiles yet. Create one above.</Text>
        ) : (
          profiles.map((profile) => (
            <View key={profile.profile_id} style={styles.profileItem}>
              <Text style={styles.profileName}>{profile.name || 'Unnamed'}</Text>
              <Text style={styles.profileDate}>
                Created {new Date(profile.created_at).toLocaleDateString()}
              </Text>
            </View>
          ))
        )}
      </View>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={() => {
          Alert.alert('Logout', 'Are you sure?', [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Logout', onPress: () => navigation.replace('Login') },
          ]);
        }}
      >
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>
    </ScrollView>
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
    marginBottom: 20,
  },
  userCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
  },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatarText: {
    color: '#ffffff',
    fontSize: 32,
    fontWeight: '800',
  },
  username: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '700',
  },
  email: {
    color: '#a0a0b0',
    fontSize: 14,
    marginTop: 4,
  },
  memberSince: {
    color: '#555',
    fontSize: 12,
    marginTop: 8,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 8,
  },
  menuItem: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  menuIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  menuContent: {
    flex: 1,
  },
  menuLabel: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  menuDescription: {
    color: '#a0a0b0',
    fontSize: 13,
    marginTop: 2,
  },
  menuArrow: {
    color: '#555',
    fontSize: 24,
  },
  profileItem: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  profileName: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  profileDate: {
    color: '#a0a0b0',
    fontSize: 12,
    marginTop: 2,
  },
  emptyText: {
    color: '#555',
    fontSize: 14,
    textAlign: 'center',
    padding: 20,
  },
  logoutButton: {
    backgroundColor: '#2a2a4e',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 30,
  },
  logoutText: {
    color: '#f44336',
    fontSize: 16,
    fontWeight: '600',
  },
});
