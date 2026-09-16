"use client";

import { useEffect, useState } from "react";
import { api, User, DashboardStats } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { GradientHeader } from "@/components/ColourfulComponents/GradientHeader";
import { Mic, Shield, UserCheck } from "lucide-react";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<DashboardStats>({
    voice_profiles: 0,
    face_registrations: 0,
    interviews_completed: 0,
    deepfake_detections: 0,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [userData, statsData] = await Promise.all([
          api.auth.me(),
          api.analytics.dashboard(),
        ]);
        setUser(userData);
        setStats(statsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      }
    }
    loadDashboard();
  }, []);

  return (
    <div className="space-y-6">
      <GradientHeader
        title="Dashboard"
        subtitle={`Welcome back${user ? `, ${user.username}` : ""}. Here's an overview of your account.`}
      />

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="border-[#FF6B6B]/20 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Profiles</CardTitle>
            <Mic className="h-6 w-6 text-[#FF6B6B]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#FF6B6B]">{stats.voice_profiles}</div>
            <CardDescription>Cloned voice profiles</CardDescription>
          </CardContent>
        </Card>

        <Card className="border-[#FF8E53]/20 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Face Registrations</CardTitle>
            <UserCheck className="h-6 w-6 text-[#FF8E53]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#FF8E53]">{stats.face_registrations}</div>
            <CardDescription>Registered face profiles</CardDescription>
          </CardContent>
        </Card>

        <Card className="border-[#55EFC4]/20 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interviews</CardTitle>
            <Shield className="h-6 w-6 text-[#55EFC4]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#55EFC4]">{stats.interviews_completed}</div>
            <CardDescription>Completed interview sessions</CardDescription>
          </CardContent>
        </Card>
      </div>

      <Card variant="glass">
        <CardHeader>
          <CardTitle className="text-gradient-sunset">Account Status</CardTitle>
          <CardDescription>Your account and service status</CardDescription>
        </CardHeader>
        <CardContent>
          {user ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#6c757d]">Email</span>
                <span className="text-sm font-medium">{user.email}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#6c757d]">Username</span>
                <span className="text-sm font-medium">{user.username}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#6c757d]">Status</span>
                <Badge variant={user.is_active ? "sunset" : "destructive"}>
                  {user.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#6c757d]">Voice Profile</span>
                <Badge variant={user.voice_profile_id ? "ocean" : "secondary"}>
                  {user.voice_profile_id ? "Registered" : "Not Set"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#6c757d]">Face Registration</span>
                <Badge variant={user.face_embedding ? "tropical" : "secondary"}>
                  {user.face_embedding ? "Registered" : "Not Set"}
                </Badge>
              </div>
            </div>
          ) : (
            <div className="text-sm text-[#6c757d]">Loading account info...</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
