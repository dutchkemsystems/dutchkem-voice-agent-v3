"use client";

import React from "react";

interface AnimatedBackgroundProps {
  children: React.ReactNode;
}

export function AnimatedBackground({ children }: AnimatedBackgroundProps) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B6B]/10 via-[#FF8E53]/10 to-[#81ECEC]/10 animate-gradient-slow" />

      {/* Floating Particles */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="floating-particle particle-1" />
        <div className="floating-particle particle-2" />
        <div className="floating-particle particle-3" />
        <div className="floating-particle particle-4" />
        <div className="floating-particle particle-5" />
      </div>

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
