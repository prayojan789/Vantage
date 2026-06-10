"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Layers, Newspaper, BarChart3,
  FlaskConical, Settings, Activity, Eye
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard", label: "Event Clusters", icon: Layers },
  { href: "/sources", label: "Media Sources", icon: Newspaper },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/playground", label: "AI Playground", icon: FlaskConical },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 z-40 flex flex-col"
      style={{
        background: "rgba(8, 11, 15, 0.95)",
        borderRight: "1px solid #1C2128",
        backdropFilter: "blur(20px)",
      }}>

      {/* Logo */}
      <div className="px-5 py-6 border-b border-base-800">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #00D4FF20, #F5C54220)", border: "1px solid #00D4FF30" }}>
              <Eye size={16} className="text-cyan-400" />
            </div>
            {/* Live indicator */}
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />
          </div>
          <div>
            <h1 className="font-display font-700 text-base-100 tracking-tight text-[15px]">
              VANTAGE
            </h1>
            <p className="text-[10px] text-base-400 uppercase tracking-widest mt-0.5">
              Nepal Media Intel
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        <p className="text-[10px] uppercase tracking-widest text-base-500 px-3 mb-3">
          Platform
        </p>
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                active
                  ? "bg-cyan-400/10 text-cyan-400 border border-cyan-400/20"
                  : "text-base-400 hover:text-base-200 hover:bg-base-800"
              )}
            >
              <Icon size={16} strokeWidth={active ? 2 : 1.5} />
              {label}
              {active && (
                <span className="ml-auto w-1 h-4 rounded-full bg-cyan-400/60" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* LLM Status indicator */}
      <div className="px-4 py-4 border-t border-base-800">
        <div className="glass-card p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-1.5">
            <Activity size={12} className="text-emerald-400" />
            <span className="text-[11px] text-base-400 uppercase tracking-wider">LLM Engine</span>
          </div>
          <LLMStatusBadge />
        </div>
      </div>
    </aside>
  );
}

function LLMStatusBadge() {
  // Simple inline status — real status fetched in settings
  return (
    <div className="flex items-center gap-2">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
      <span className="text-[12px] text-base-300 font-mono">Active</span>
    </div>
  );
}
