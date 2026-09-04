"use client";

import React from "react";

interface NavItem {
  href: string;
  label: string;
}

interface ColourfulNavProps {
  items: NavItem[];
}

export function ColourfulNav({ items }: ColourfulNavProps) {
  return (
    <nav className="bg-gradient-to-r from-[#FF6B6B] via-[#FF8E53] to-[#FECA57] shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-white text-2xl font-bold">🎙️ Voice Agent</span>
          </div>
          <div className="flex items-center space-x-6">
            {items.map((item, index) => (
              <a
                key={index}
                href={item.href}
                className="text-white hover:text-white/80 font-medium transition-colors duration-200 hover:scale-105 transform"
              >
                {item.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
