"use client";

import React from "react";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  colour?: "sunset" | "ocean" | "tropical";
}

const borderColours = {
  sunset: "border-[#FF6B6B]/30",
  ocean: "border-[#81ECEC]/30",
  tropical: "border-[#55EFC4]/30",
};

export function GlassCard({
  children,
  className = "",
  colour = "sunset",
}: GlassCardProps) {
  return (
    <div
      className={`
        backdrop-blur-xl bg-white/80
        border ${borderColours[colour]} border-opacity-30
        rounded-2xl shadow-2xl
        hover:shadow-[#FF6B6B]/20 transition-all duration-300
        ${className}
      `}
    >
      {children}
    </div>
  );
}
