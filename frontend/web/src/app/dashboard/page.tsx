"use client";

import { useEffect, useState } from "react";
import { api, User } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface Stats {
  voiceProfiles: number;
  interviewsCompleted: number;
  deepfakeDetections: number;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [stats] = useState<Stats>({ voiceProfiles: 0, interviewsCompleted: 0, deepfakeDetections: 0 });
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await api.auth.me();
        setUser(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load user");
      }
    }
    loadUser();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back{user ? `, ${user.username}` : ""}. Here&apos;s an overview of your account.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Profiles</CardTitle>
            <span className="text-2xl">🎙️</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.voiceProfiles}</div>
            <CardDescription>Cloned voice profiles</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interviews</CardTitle>
            <span className="text-2xl">🎤</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.interviewsCompleted}</div>
            <CardDescription>Completed interview sessions</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Detections</CardTitle>
            <span className="text-2xl">🛡️</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.deepfakeDetections}</div>
            <CardDescription>Deepfake detections performed</CardDescription>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account Status</CardTitle>
          <CardDescription>Your account and service status</CardDescription>
        </CardHeader>
        <CardContent>
          {user ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Email</span>
                <span className="text-sm font-medium">{user.email}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Username</span>
                <span className="text-sm font-medium">{user.username}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <Badge variant={user.is_active ? "default" : "destructive"}>
                  {user.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Voice Profile</span>
                <Badge variant={user.voice_profile_id ? "default" : "secondary"}>
                  {user.voice_profile_id ? "Registered" : "Not Set"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Face Registration</span>
                <Badge variant={user.face_embedding ? "default" : "secondary"}>
                  {user.face_embedding ? "Registered" : "Not Set"}
                </Badge>
              </div>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">Loading account info...</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
