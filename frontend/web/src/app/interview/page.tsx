"use client";

import { useState, useRef, useCallback } from "react";
import { api, InterviewSession } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";

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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Interview Session</h1>
        <p className="text-muted-foreground">Start and manage your AI interview session.</p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Session Control</CardTitle>
              {session && (
                <Badge variant={isActive ? "default" : "secondary"}>
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
                <Button onClick={startSession} disabled={loading} size="lg">
                  {loading ? "Starting..." : "Start Interview"}
                </Button>
              ) : (
                <Button onClick={stopSession} disabled={loading} variant="destructive" size="lg">
                  {loading ? "Stopping..." : "Stop Interview"}
                </Button>
              )}
            </div>

            {isActive && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
                Recording in progress...
              </div>
            )}

            <div className="rounded-lg border bg-muted/50 p-4">
              <h3 className="mb-2 text-sm font-medium">Transcript</h3>
              <div className="max-h-64 space-y-2 overflow-y-auto text-sm">
                {transcript.length === 0 ? (
                  <p className="text-muted-foreground">
                    {isActive ? "Listening..." : "No transcript yet. Start an interview to begin."}
                  </p>
                ) : (
                  transcript.map((line, i) => (
                    <p key={i} className="text-foreground">
                      {line}
                    </p>
                  ))
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Session Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {session ? (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Session ID</span>
                  <span className="font-mono text-xs">{session.id.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant={isActive ? "default" : "secondary"}>
                    {session.status}
                  </Badge>
                </div>
                {session.started_at && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Started</span>
                    <span>{new Date(session.started_at).toLocaleTimeString()}</span>
                  </div>
                )}
                {session.ended_at && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Ended</span>
                    <span>{new Date(session.ended_at).toLocaleTimeString()}</span>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No active session</p>
            )}

            <div className="border-t pt-3">
              <h4 className="mb-2 text-sm font-medium">Capabilities</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
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
    </div>
  );
}
