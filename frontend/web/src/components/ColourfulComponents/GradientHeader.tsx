import React from "react";

interface GradientHeaderProps {
  title: string;
  subtitle?: string;
}

export function GradientHeader({ title, subtitle }: GradientHeaderProps) {
  return (
    <div className="py-6">
      <h1 className="text-4xl font-bold text-gradient-sunset">{title}</h1>
      {subtitle && (
        <p className="mt-2 text-lg text-[#6c757d]">{subtitle}</p>
      )}
    </div>
  );
}
