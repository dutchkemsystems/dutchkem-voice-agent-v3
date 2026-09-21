"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AgentInfo } from "./agents";

interface AgentCardProps {
  agent: AgentInfo;
  isActive?: boolean;
}

export function AgentCard({ agent, isActive }: AgentCardProps) {
  return (
    <Card
      variant="glass"
      className={`transition-all ${isActive ? "ring-2 ring-[#FF6B6B]" : ""}`}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{agent.icon}</span>
          <CardTitle className="text-sm">{agent.name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-xs text-[#6c757d]">{agent.description}</p>
        <div className="flex flex-wrap gap-1">
          {agent.specialties.map((s) => (
            <Badge key={s} variant="secondary" className="text-[10px]">
              {s}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
