"use client";
import { motion } from "framer-motion";
import { FileText, Layers, Users, TrendingUp } from "lucide-react";
import type { DashboardStats } from "@/types";
import { getBiasLabel } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  accent?: string;
  delay?: number;
}

function StatCard({ label, value, sub, icon, accent = "#00D4FF", delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="glass-card p-5 relative overflow-hidden"
    >
      {/* Subtle glow */}
      <div
        className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10 blur-2xl"
        style={{ background: accent, transform: "translate(30%, -30%)" }}
      />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-wider text-base-500 mb-2">{label}</p>
          <p className="text-2xl font-display font-600 text-base-100">{value}</p>
          {sub && <p className="text-xs text-base-400 mt-1">{sub}</p>}
        </div>
        <div
          className="p-2 rounded-lg"
          style={{ background: `${accent}15`, color: accent }}
        >
          {icon}
        </div>
      </div>
    </motion.div>
  );
}

export function DashboardStatsRow({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        label="Total Articles"
        value={stats.total_articles.toLocaleString()}
        sub="across all sources"
        icon={<FileText size={18} />}
        accent="#00D4FF"
        delay={0}
      />
      <StatCard
        label="Event Clusters"
        value={stats.total_events.toLocaleString()}
        sub="unique stories tracked"
        icon={<Layers size={18} />}
        accent="#A78BFA"
        delay={0.05}
      />
      <StatCard
        label="Political Entities"
        value={stats.total_entities.toLocaleString()}
        sub="people, parties, orgs"
        icon={<Users size={18} />}
        accent="#F5C542"
        delay={0.1}
      />
      <StatCard
        label="Avg Bias Score"
        value={`${Math.round(stats.avg_bias_score * 100)}%`}
        sub={getBiasLabel(stats.avg_bias_score)}
        icon={<TrendingUp size={18} />}
        accent={stats.avg_bias_score > 0.5 ? "#FF6B6B" : "#34D399"}
        delay={0.15}
      />
    </div>
  );
}
