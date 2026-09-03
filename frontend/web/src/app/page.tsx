import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <div className="mx-auto max-w-2xl px-4 text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            DutchKem Voice Agent
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            AI-powered voice agent with deepfake detection and interview proctoring
          </p>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/login"
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium text-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
          >
            Create Account
          </Link>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          <div className="rounded-lg border bg-card p-6 text-left">
            <div className="mb-2 text-lg font-semibold text-card-foreground">Voice Cloning</div>
            <p className="text-sm text-muted-foreground">
              Clone your voice with just a few seconds of audio using Chatterbox TTS.
            </p>
          </div>
          <div className="rounded-lg border bg-card p-6 text-left">
            <div className="mb-2 text-lg font-semibold text-card-foreground">Deepfake Detection</div>
            <p className="text-sm text-muted-foreground">
              Real-time voice and video deepfake detection with multi-method analysis.
            </p>
          </div>
          <div className="rounded-lg border bg-card p-6 text-left">
            <div className="mb-2 text-lg font-semibold text-card-foreground">Interview Proctoring</div>
            <p className="text-sm text-muted-foreground">
              Face recognition, liveness detection, and background monitoring.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
