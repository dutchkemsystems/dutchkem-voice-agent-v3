import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-[#FF6B6B]/10 via-[#FF8E53]/10 to-[#81ECEC]/10">
      <div className="mx-auto max-w-2xl px-4 text-center">
        <div className="mb-8">
          <h1 className="text-5xl font-bold tracking-tight text-gradient-sunset sm:text-6xl">
            DutchKem Voice Agent
          </h1>
          <p className="mt-4 text-lg text-[#6c757d]">
            AI-powered voice agent with deepfake detection and interview proctoring
          </p>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/login"
            className="inline-flex h-12 items-center justify-center rounded-xl bg-gradient-to-r from-[#FF6B6B] to-[#FF8E53] px-8 text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="inline-flex h-12 items-center justify-center rounded-xl border-2 border-[#FF6B6B]/30 bg-white px-8 text-sm font-semibold text-[#1A1A2E] shadow-sm transition-all duration-300 hover:border-[#FF6B6B] hover:shadow-lg"
          >
            Create Account
          </Link>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          <div className="rounded-2xl border border-[#FF6B6B]/20 bg-white/80 backdrop-blur-sm p-6 text-left shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="mb-2 text-lg font-semibold text-[#1A1A2E]">🎙️ Voice Cloning</div>
            <p className="text-sm text-[#6c757d]">
              Clone your voice with just a few seconds of audio using Chatterbox TTS.
            </p>
          </div>
          <div className="rounded-2xl border border-[#55EFC4]/20 bg-white/80 backdrop-blur-sm p-6 text-left shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="mb-2 text-lg font-semibold text-[#1A1A2E]">🛡️ Deepfake Detection</div>
            <p className="text-sm text-[#6c757d]">
              Real-time voice and video deepfake detection with multi-method analysis.
            </p>
          </div>
          <div className="rounded-2xl border border-[#81ECEC]/20 bg-white/80 backdrop-blur-sm p-6 text-left shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="mb-2 text-lg font-semibold text-[#1A1A2E]">📋 Interview Proctoring</div>
            <p className="text-sm text-[#6c757d]">
              Face recognition, liveness detection, and background monitoring.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
