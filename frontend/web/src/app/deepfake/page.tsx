"use client";

import { useState, useRef } from "react";
import { api, DeepfakeDetectionResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { GradientHeader } from "@/components/ColourfulComponents/GradientHeader";
import { Shield, Upload, CheckCircle, XCircle } from "lucide-react";

export default function DeepfakePage() {
  const [result, setResult] = useState<DeepfakeDetectionResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"voice" | "video">("voice");
  const audioInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const detectVoice = async () => {
    const file = audioInputRef.current?.files?.[0];
    if (!file) return;
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const res = await api.deepfake.detectVoice(file);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  const detectVideo = async () => {
    const file = videoInputRef.current?.files?.[0];
    if (!file) return;
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const res = await api.deepfake.detectVideo(file);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <GradientHeader
        title="Deepfake Detection"
        subtitle="Analyze audio and video files for deepfake artifacts."
      />

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="text-gradient-sunset">Detection Mode</CardTitle>
            <CardDescription>Choose the type of media to analyze</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "voice" ? "sunset" : "outline"}
                onClick={() => setActiveTab("voice")}
                className="gap-2"
              >
                Voice Analysis
              </Button>
              <Button
                variant={activeTab === "video" ? "sunset" : "outline"}
                onClick={() => setActiveTab("video")}
                className="gap-2"
              >
                Video Analysis
              </Button>
            </div>

            {activeTab === "voice" && (
              <div className="space-y-3">
                <input
                  ref={audioInputRef}
                  type="file"
                  accept="audio/*"
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => audioInputRef.current?.click()}
                  className="w-full gap-2"
                >
                  <Upload className="h-4 w-4" />
                  Select Audio File
                </Button>
                <Button
                  variant="sunset"
                  onClick={detectVoice}
                  disabled={loading || !audioInputRef.current?.files?.[0]}
                  className="w-full gap-2"
                >
                  <Shield className="h-4 w-4" />
                  {loading ? "Analyzing..." : "Analyze Voice"}
                </Button>
              </div>
            )}

            {activeTab === "video" && (
              <div className="space-y-3">
                <input
                  ref={videoInputRef}
                  type="file"
                  accept="video/*"
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => videoInputRef.current?.click()}
                  className="w-full gap-2"
                >
                  <Upload className="h-4 w-4" />
                  Select Video File
                </Button>
                <Button
                  variant="sunset"
                  onClick={detectVideo}
                  disabled={loading || !videoInputRef.current?.files?.[0]}
                  className="w-full gap-2"
                >
                  <Shield className="h-4 w-4" />
                  {loading ? "Analyzing..." : "Analyze Video"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card variant="glass">
          <CardHeader>
            <CardTitle className="text-gradient-sunset">Results</CardTitle>
            <CardDescription>Detection analysis output</CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {result.is_deepfake ? (
                    <XCircle className="h-8 w-8 text-[#dc3545]" />
                  ) : (
                    <CheckCircle className="h-8 w-8 text-[#55EFC4]" />
                  )}
                  <div>
                    <div className="text-lg font-bold">
                      {result.is_deepfake ? "Deepfake Detected" : "Authentic Content"}
                    </div>
                    <div className="text-sm text-[#6c757d]">
                      Confidence: {(result.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <Badge variant={result.is_deepfake ? "destructive" : "tropical"}>
                  {result.is_deepfake ? "HIGH RISK" : "LOW RISK"}
                </Badge>

                {Object.keys(result.details).length > 0 && (
                  <div className="rounded-xl border border-[#FF6B6B]/20 bg-[#FF6B6B]/5 p-4">
                    <h3 className="mb-2 text-sm font-medium text-[#1A1A2E]">Technical Details</h3>
                    <pre className="text-xs text-[#6c757d] overflow-auto max-h-48">
                      {JSON.stringify(result.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-[#6c757d]">
                <Shield className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Upload a file and run detection to see results.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
