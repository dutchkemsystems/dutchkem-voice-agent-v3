"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { GradientHeader } from "@/components/ColourfulComponents/GradientHeader";
import { Mic, Camera } from "lucide-react";

export default function ProfilePage() {
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [voiceStatus, setVoiceStatus] = useState("");
  const [faceStatus, setFaceStatus] = useState("");
  const [loading, setLoading] = useState<"voice" | "face" | null>(null);
  const voiceInputRef = useRef<HTMLInputElement>(null);
  const faceInputRef = useRef<HTMLInputElement>(null);

  async function handleVoiceClone() {
    if (!voiceFile) return;
    setLoading("voice");
    setVoiceStatus("");
    try {
      await api.voice.clone(voiceFile);
      setVoiceStatus("Voice profile created successfully!");
      setVoiceFile(null);
      if (voiceInputRef.current) voiceInputRef.current.value = "";
    } catch (err) {
      setVoiceStatus(err instanceof Error ? err.message : "Voice clone failed");
    } finally {
      setLoading(null);
    }
  }

  async function handleFaceRegister() {
    if (!faceFile) return;
    setLoading("face");
    setFaceStatus("");
    try {
      await api.proctoring.registerFace(faceFile);
      setFaceStatus("Face registered successfully!");
      setFaceFile(null);
      if (faceInputRef.current) faceInputRef.current.value = "";
    } catch (err) {
      setFaceStatus(err instanceof Error ? err.message : "Face registration failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="space-y-6">
      <GradientHeader title="Profile" subtitle="Manage your voice clone and face registration." />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-[#FF6B6B]">
              <Mic className="h-5 w-5" /> Voice Clone
            </CardTitle>
            <CardDescription>
              Upload a short audio sample (5-30 seconds) to create a voice profile.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="voice-audio">Audio File</Label>
              <Input
                ref={voiceInputRef}
                id="voice-audio"
                type="file"
                accept="audio/*"
                onChange={(e) => setVoiceFile(e.target.files?.[0] || null)}
              />
              <p className="text-xs text-[#6c757d]">
                Supported: WAV, MP3, FLAC. Best results with clean speech.
              </p>
            </div>
            {voiceStatus && (
              <Alert variant={voiceStatus.includes("success") ? "default" : "destructive"}>
                <AlertDescription>{voiceStatus}</AlertDescription>
              </Alert>
            )}
            <Button variant="sunset" onClick={handleVoiceClone} disabled={!voiceFile || loading === "voice"} className="w-full">
              {loading === "voice" ? "Creating Profile..." : "Create Voice Profile"}
            </Button>
          </CardContent>
        </Card>

        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-[#81ECEC]">
              <Camera className="h-5 w-5" /> Face Registration
            </CardTitle>
            <CardDescription>
              Upload a clear photo of your face for identity verification.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="face-image">Photo</Label>
              <Input
                ref={faceInputRef}
                id="face-image"
                type="file"
                accept="image/*"
                onChange={(e) => setFaceFile(e.target.files?.[0] || null)}
              />
              <p className="text-xs text-[#6c757d]">
                Supported: JPG, PNG. Face should be clearly visible and front-facing.
              </p>
            </div>
            {faceStatus && (
              <Alert variant={faceStatus.includes("success") ? "default" : "destructive"}>
                <AlertDescription>{faceStatus}</AlertDescription>
              </Alert>
            )}
            <Button variant="ocean" onClick={handleFaceRegister} disabled={!faceFile || loading === "face"} className="w-full">
              {loading === "face" ? "Registering..." : "Register Face"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
