"use client";

import { useState, useRef, useCallback } from "react";
import { api, InterviewSession } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { GradientHeader } from "@/components/ColourfulComponents/GradientHeader";
import { Mic, MicOff, Play, Square } from "lucide-react";
import { INTERVIEW_AGENTS } from "./agents";
import { AgentCard } from "./AgentCard";

export default function InterviewPage() {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const isActive = session?.status === "active";

  const startSession = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const result = await api.interview.start();
      setSession(result);
      setTranscript([]);

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      mediaRecorder.start();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setLoading(false);
    }
  }, []);

  const stopSession = useCallback(async () => {
    if (!session) return;
    setError("");
    setLoading(true);

    try {
      if (mediaRecorderRef.current?.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }

      const result = await api.interview.stop(session.id);
      setSession(result);
      setTranscript((prev) => [...prev, "[Interview ended]"]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to stop interview");
    } finally {
      setLoading(false);
    }
  }, [session]);

  return (
    <div className="space-y-6">
      <GradientHeader title="Interview Session" subtitle="Start and manage your AI interview session." />

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card variant="glass" className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-gradient-sunset">Session Control</CardTitle>
              {session && (
                <Badge variant={isActive ? "sunset" : "secondary"}>
                  {session.status}
                </Badge>
              )}
            </div>
            <CardDescription>
              {isActive
                ? "Interview is in progress. Microphone is active."
                : "Start a new interview session to begin."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              {!isActive ? (
                <Button variant="sunset" onClick={startSession} disabled={loading} size="lg" className="gap-2">
                  <Play className="h-5 w-5" />
                  {loading ? "Starting..." : "Start Interview"}
                </Button>
              ) : (
                <Button onClick={stopSession} disabled={loading} variant="destructive" size="lg" className="gap-2">
                  <Square className="h-5 w-5" />
                  {loading ? "Stopping..." : "Stop Interview"}
                </Button>
              )}
            </div>

            {isActive && (
              <div className="flex items-center gap-2 text-sm text-[#FF6B6B]">
                <Mic className="h-4 w-4 animate-pulse" />
                Recording in progress...
              </div>
            )}

            <div className="rounded-xl border border-[#FF6B6B]/20 bg-[#FF6B6B]/5 p-4">
              <h3 className="mb-2 text-sm font-medium text-[#1A1A2E]">Transcript</h3>
              <div className="max-h-64 space-y-2 overflow-y-auto text-sm">
                {transcript.length === 0 ? (
                  <p className="text-[#6c757d]">
                    {isActive ? "Listening..." : "No transcript yet. Start an interview to begin."}
                  </p>
                ) : (
                  transcript.map((line, i) => (
                    <p key={i} className="text-[#1A1A2E]">
                      {line}
                    </p>
                  ))
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="glass">
          <CardHeader>
            <CardTitle className="text-gradient-sunset">Session Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {session ? (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-[#6c757d]">Session ID</span>
                  <span className="font-mono text-xs">{session.id.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[#6c757d]">Status</span>
                  <Badge variant={isActive ? "sunset" : "secondary"}>
                    {session.status}
                  </Badge>
                </div>
                {session.started_at && (
                  <div className="flex justify-between text-sm">
                    <span className="text-[#6c757d]">Started</span>
                    <span>{new Date(session.started_at).toLocaleTimeString()}</span>
                  </div>
                )}
                {session.ended_at && (
                  <div className="flex justify-between text-sm">
                    <span className="text-[#6c757d]">Ended</span>
                    <span>{new Date(session.ended_at).toLocaleTimeString()}</span>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-[#6c757d]">No active session</p>
            )}

            <div className="border-t border-[#FF6B6B]/10 pt-3">
              <h4 className="mb-2 text-sm font-medium text-[#1A1A2E]">Capabilities</h4>
              <ul className="space-y-1 text-sm text-[#6c757d]">
                <li>• Voice transcription (STT)</li>
                <li>• AI-generated responses (LLM)</li>
                <li>• Deepfake detection</li>
                <li>• Face verification</li>
                <li>• Background monitoring</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Available Agents */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-[#1A1A2E]">Available Interview Agents</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {INTERVIEW_AGENTS.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              isActive={isActive && session?.status === "active"}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
