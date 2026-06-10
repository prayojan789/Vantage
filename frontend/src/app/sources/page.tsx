"use client";
import { useState } from "react";
import useSWR from "swr";
import { motion } from "framer-motion";
import { Newspaper, ExternalLink, TrendingUp, FileText } from "lucide-react";
import { BiasTrendChart } from "@/components/charts/BiasCharts";
import { fetcher } from "@/lib/api";
import type { MediaSource, MediaBiasTrend } from "@/types";
import { getBiasLabel } from "@/lib/utils";

const SOURCE_COLORS: Record<string, string> = {
  "kathmandu-post": "#00D4FF",
  "republica": "#F5C542",
  "online-khabar": "#A78BFA",
};

function SourceDetailCard({ source }: { source: MediaSource }) {
  const color = SOURCE_COLORS[source.slug] || "#8B949E";
  const { data: trend } = useSWR<MediaBiasTrend>(
    `/sources/${source.slug}/bias-trend?days=30`,
    fetcher
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 space-y-4"
    >
      {/* Source header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-display font-700"
            style={{ background: `${color}18`, color, border: `1px solid ${color}30` }}
          >
            {source.name.charAt(0)}
          </div>
          <div>
            <h3 className="text-sm font-display font-600 text-base-100">{source.name}</h3>
            <a
              href={source.base_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-base-500 hover:text-cyan-400 flex items-center gap-1 transition-colors"
            >
              {source.base_url.replace("https://", "")}
              <ExternalLink size={9} />
            </a>
          </div>
        </div>

        <div className="text-right">
          <div
            className="text-lg font-display font-700 font-mono"
            style={{
              color:
                source.avg_bias_score < 0.35
                  ? "#34D399"
                  : source.avg_bias_score < 0.65
                  ? "#F5C542"
                  : "#FF6B6B",
            }}
          >
            {Math.round(source.avg_bias_score * 100)}%
          </div>
          <div className="text-[10px] text-base-500 mt-0.5">
            {getBiasLabel(source.avg_bias_score)}
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-base-800/60 rounded-lg p-3 border border-base-700">
          <div className="flex items-center gap-1.5 mb-1">
            <FileText size={11} className="text-base-500" />
            <span className="text-[10px] uppercase tracking-wider text-base-500">Articles</span>
          </div>
          <span className="text-base-100 font-mono font-medium text-sm">
            {source.total_articles.toLocaleString()}
          </span>
        </div>
        <div className="bg-base-800/60 rounded-lg p-3 border border-base-700">
          <div className="flex items-center gap-1.5 mb-1">
            <TrendingUp size={11} className="text-base-500" />
            <span className="text-[10px] uppercase tracking-wider text-base-500">30d Trend</span>
          </div>
          <span className="text-base-100 font-mono font-medium text-sm">
            {trend?.trend?.length ?? 0} data pts
          </span>
        </div>
      </div>

      {/* Bias bar */}
      <div>
        <div className="flex justify-between mb-1.5">
          <span className="text-[10px] text-base-600 uppercase tracking-wider">Bias Level</span>
          <span className="text-[10px] font-mono" style={{ color }}>
            {Math.round(source.avg_bias_score * 100)}%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-base-700">
          <div
            className="h-1.5 rounded-full transition-all duration-700"
            style={{
              width: `${Math.round(source.avg_bias_score * 100)}%`,
              background: `linear-gradient(90deg, ${color}, ${color}99)`,
            }}
          />
        </div>
      </div>

      {/* Trend chart */}
      {trend?.trend && trend.trend.length > 0 ? (
        <div>
          <p className="text-[10px] uppercase tracking-wider text-base-600 mb-2">
            30-Day Bias Trend
          </p>
          <BiasTrendChart data={trend.trend} sourceSlug={source.slug} />
        </div>
      ) : (
        <div className="skeleton h-32 rounded-lg" />
      )}
    </motion.div>
  );
}

export default function SourcesPage() {
  const { data: sources, isLoading } = useSWR<MediaSource[]>("/sources", fetcher);

  return (
    <div className="min-h-screen bg-base-900">
      <div className="fixed inset-0 bg-glow-gold pointer-events-none opacity-50" />

      <div className="relative">
        {/* Header */}
        <div className="px-8 py-6 border-b border-base-800 bg-base-950/50 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-2 mb-1">
            <Newspaper size={16} className="text-base-400" />
            <span className="text-[11px] uppercase tracking-wider text-base-500">
              Publishers
            </span>
          </div>
          <h1 className="text-xl font-display font-600 text-base-100">Media Sources</h1>
        </div>

        <div className="px-8 py-6">
          {/* Explanation banner */}
          <div className="glass-card p-4 mb-6 border-cyan-400/15 flex items-start gap-3">
            <div className="w-1 h-full min-h-8 rounded-full bg-cyan-400/50 flex-shrink-0" />
            <p className="text-sm text-base-400 leading-relaxed">
              Each media house is scored by our LLM pipeline across all their articles.
              Bias scores reflect entity-level framing patterns —{" "}
              <span className="text-emerald-400">green (neutral)</span> to{" "}
              <span className="text-crimson-400">red (heavily biased)</span>.
              Scores are updated continuously as new articles are scraped and analyzed.
            </p>
          </div>

          {isLoading && (
            <div className="grid grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="glass-card p-6 space-y-4">
                  <div className="skeleton h-10 w-full rounded-lg" />
                  <div className="skeleton h-4 w-3/4 rounded" />
                  <div className="skeleton h-32 rounded-lg" />
                </div>
              ))}
            </div>
          )}

          {sources && (
            <div className="grid grid-cols-3 gap-6">
              {sources.map((source) => (
                <SourceDetailCard key={source.id} source={source} />
              ))}
            </div>
          )}

          {sources?.length === 0 && (
            <div className="glass-card p-12 text-center">
              <Newspaper size={32} className="text-base-600 mx-auto mb-3" />
              <p className="text-base-400 text-sm">
                No sources configured yet. Run the database seed script to add media sources.
              </p>
              <code className="text-[11px] text-cyan-400 mt-2 block font-mono">
                python scripts/seed_db.py
              </code>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
