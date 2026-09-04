import React from "react";

interface Stat {
  label: string;
  value: string | number;
  icon?: string;
}

interface ColourfulStatsProps {
  stats: Stat[];
}

const gradients = [
  "from-[#FF6B6B] to-[#FF8E53]",
  "from-[#FF8E53] to-[#FECA57]",
  "from-[#FECA57] to-[#55EFC4]",
  "from-[#55EFC4] to-[#81ECEC]",
  "from-[#81ECEC] to-[#FF6B6B]",
];

export function ColourfulStats({ stats }: ColourfulStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className={`
            bg-gradient-to-br ${gradients[index % gradients.length]}
            rounded-2xl p-6 text-white shadow-lg
            hover:shadow-xl transform hover:scale-105
            transition-all duration-300
          `}
        >
          {stat.icon && <div className="text-3xl mb-2">{stat.icon}</div>}
          <div className="text-3xl font-bold">{stat.value}</div>
          <div className="text-sm opacity-90 mt-1">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
