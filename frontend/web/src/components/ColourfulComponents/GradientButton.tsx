"use client";

import React from "react";

interface GradientButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "primary" | "secondary" | "success" | "warning" | "danger";
  size?: "sm" | "md" | "lg";
  className?: string;
  disabled?: boolean;
}

const gradients = {
  primary: "from-[#FF6B6B] to-[#FF8E53]",
  secondary: "from-[#FECA57] to-[#55EFC4]",
  success: "from-[#55EFC4] to-[#81ECEC]",
  warning: "from-[#FF8E53] to-[#FECA57]",
  danger: "from-[#FF6B6B] to-[#FF8E53]",
};

const sizes = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-5 py-2.5 text-base",
  lg: "px-6 py-3 text-lg",
};

export function GradientButton({
  children,
  onClick,
  type = "primary",
  size = "md",
  className = "",
  disabled = false,
}: GradientButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        bg-gradient-to-r ${gradients[type]} ${sizes[size]}
        text-white font-semibold rounded-xl
        shadow-lg hover:shadow-xl transform hover:scale-105
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
        ${className}
      `}
    >
      {children}
    </button>
  );
}
