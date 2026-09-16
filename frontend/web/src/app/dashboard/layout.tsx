"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { api, ModeInfo } from "@/lib/api";
import { LayoutDashboard, User, Mic, Shield, LogOut } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/interview", label: "Interview", icon: Mic },
  { href: "/deepfake", label: "Deepfake Detection", icon: Shield },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [modes, setModes] = useState<ModeInfo[]>([]);
  const [currentMode, setCurrentMode] = useState<ModeInfo | null>(null);
  const [loadingModes, setLoadingModes] = useState(true);

  useEffect(() => {
    async function loadModes() {
      try {
        const { modes: modeList } = await api.modes.list();
        setModes(modeList);
        const savedModeId = localStorage.getItem("currentMode") || "interview";
        const active = modeList.find((m) => m.mode_id === savedModeId) || modeList[0];
        setCurrentMode(active);
      } catch {
        setCurrentMode({
          mode_id: "interview",
          display_name: "Interview",
          description: "Default interview mode",
          icon: "🎤",
          agent_classes: [],
          default_agent: "hr_agent",
          required_context: [],
          ui_components: [],
          default_view: "transcript",
        });
      } finally {
        setLoadingModes(false);
      }
    }
    loadModes();
  }, []);

  async function handleModeSwitch(modeId: string) {
    try {
      const result = await api.modes.switch(modeId);
      if (result.success) {
        setCurrentMode(result.mode);
        localStorage.setItem("currentMode", modeId);
      }
    } catch {
      const mode = modes.find((m) => m.mode_id === modeId);
      if (mode) {
        setCurrentMode(mode);
        localStorage.setItem("currentMode", modeId);
      }
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("currentMode");
    router.push("/login");
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 border-r border-[#FF6B6B]/20 bg-gradient-to-b from-white to-[#FF6B6B]/5 lg:block">
        <div className="flex h-14 items-center border-b border-[#FF6B6B]/20 px-4 bg-gradient-to-r from-[#FF6B6B] to-[#FF8E53]">
          <Link href="/dashboard" className="text-lg font-bold text-white">
            🎙️ DutchKem
          </Link>
        </div>

        {/* Mode Selector */}
        <div className="border-b border-[#FF6B6B]/10 p-4">
          <label className="text-xs font-medium text-[#6c757d] uppercase tracking-wider">
            Mode
          </label>
          {loadingModes ? (
            <div className="mt-1 h-9 animate-pulse rounded-md bg-[#FF6B6B]/10" />
          ) : (
            <select
              value={currentMode?.mode_id || "interview"}
              onChange={(e) => handleModeSwitch(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[#FF6B6B]/30 bg-white px-3 py-2 text-sm text-[#1A1A2E] focus:outline-none focus:ring-2 focus:ring-[#FF8E53] focus:border-[#FF8E53]"
            >
              {modes.map((mode) => (
                <option key={mode.mode_id} value={mode.mode_id}>
                  {mode.display_name}
                </option>
              ))}
            </select>
          )}
          {currentMode && (
            <p className="mt-1 text-xs text-[#6c757d]">{currentMode.description}</p>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                  pathname === item.href
                    ? "bg-gradient-to-r from-[#FF6B6B] to-[#FF8E53] text-white shadow-md"
                    : "text-[#1A1A2E] hover:bg-[#FF6B6B]/10"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="mt-auto border-t border-[#FF6B6B]/10 p-4">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[#6c757d] transition-all duration-200 hover:bg-[#FF6B6B]/10 hover:text-[#FF6B6B]"
          >
            <LogOut className="h-5 w-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Mobile Header */}
        <header className="flex h-14 items-center justify-between border-b border-[#FF6B6B]/20 px-4 bg-gradient-to-r from-[#FF6B6B] to-[#FF8E53] lg:hidden">
          <Link href="/dashboard" className="text-lg font-bold text-white">
            🎙️ DutchKem
          </Link>
          <div className="flex gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-md p-2 text-white transition-all duration-200",
                    pathname === item.href
                      ? "bg-white/20"
                      : "hover:bg-white/10"
                  )}
                >
                  <Icon className="h-5 w-5" />
                </Link>
              );
            })}
            <button
              onClick={handleLogout}
              className="rounded-md p-2 text-white hover:bg-white/10"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Mobile Mode Badge */}
        <div className="flex items-center gap-2 border-b border-[#FF6B6B]/10 bg-[#FF6B6B]/5 px-4 py-2 lg:hidden">
          <span className="text-xs text-[#6c757d]">Mode:</span>
          <select
            value={currentMode?.mode_id || "interview"}
            onChange={(e) => handleModeSwitch(e.target.value)}
            className="rounded-md border border-[#FF6B6B]/30 bg-white px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-[#FF8E53]"
          >
            {modes.map((mode) => (
              <option key={mode.mode_id} value={mode.mode_id}>
                {mode.display_name}
              </option>
            ))}
          </select>
        </div>

        <main className="flex-1 overflow-auto p-4 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
