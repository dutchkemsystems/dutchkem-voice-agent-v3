"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { api, ModeInfo } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/profile", label: "Profile", icon: "👤" },
  { href: "/interview", label: "Interview", icon: "🎤" },
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
        // API not available, use default
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
      // Fallback to local state
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
      <aside className="hidden w-64 border-r bg-sidebar lg:block">
        <div className="flex h-14 items-center border-b px-4">
          <Link href="/dashboard" className="text-lg font-semibold text-sidebar-foreground">
            DutchKem
          </Link>
        </div>

        {/* Mode Selector */}
        <div className="border-b p-4">
          <label className="text-xs font-medium text-sidebar-foreground/70 uppercase tracking-wider">
            Mode
          </label>
          {loadingModes ? (
            <div className="mt-1 h-9 animate-pulse rounded-md bg-sidebar-accent" />
          ) : (
            <select
              value={currentMode?.mode_id || "interview"}
              onChange={(e) => handleModeSwitch(e.target.value)}
              className="mt-1 w-full rounded-md border border-sidebar-border bg-sidebar px-3 py-2 text-sm text-sidebar-foreground focus:outline-none focus:ring-2 focus:ring-sidebar-accent"
            >
              {modes.map((mode) => (
                <option key={mode.mode_id} value={mode.mode_id}>
                  {mode.icon} {mode.display_name}
                </option>
              ))}
            </select>
          )}
          {currentMode && (
            <p className="mt-1 text-xs text-sidebar-foreground/50">{currentMode.description}</p>
          )}
        </div>

        <nav className="flex flex-col gap-1 p-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                pathname === item.href
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              )}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto border-t p-4">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent/50"
          >
            <span>🚪</span>
            Sign Out
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b px-4 lg:hidden">
          <Link href="/dashboard" className="text-lg font-semibold">
            DutchKem
          </Link>
          <div className="flex gap-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {item.icon}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              🚪
            </button>
          </div>
        </header>

        {/* Mobile Mode Badge */}
        <div className="flex items-center gap-2 border-b px-4 py-2 lg:hidden">
          <span className="text-xs text-muted-foreground">Mode:</span>
          <select
            value={currentMode?.mode_id || "interview"}
            onChange={(e) => handleModeSwitch(e.target.value)}
            className="rounded-md border px-2 py-1 text-xs"
          >
            {modes.map((mode) => (
              <option key={mode.mode_id} value={mode.mode_id}>
                {mode.icon} {mode.display_name}
              </option>
            ))}
          </select>
        </div>

        <main className="flex-1 overflow-auto p-4 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
