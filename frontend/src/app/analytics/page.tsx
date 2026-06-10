"use client";
import { useState } from "react";
import useSWR from "swr";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Users, Activity } from "lucide-react";
import {
  BiasDistributionChart,
  EntitySentimentChart,
  MultiSourceBiasChart,
} from "@/components/charts/BiasCharts";
import { fetcher, api } from "@/lib/api";
import type {
  BiasDistributionBucket,
  EntityOverview,
  MediaSource,
  MediaBiasTrend,
} from "@/types";

function SectionHeader({ icon, title, sub }: { icon: React.ReactNode; title: string; sub?: string }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <div className="p-2 rounded-lg bg-base-800 border border-base-700">{icon}</div>
      <div>
        <h2 className="text-sm font-display font-600 text-base-100">{title}</h2>
        {sub && <p className="text-xs text-base-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);

  const { data: distribution } = useSWR<BiasDistributionBucket[]>(
    "/analytics/bias-distribution",
    fetcher
  );
  const { data: entities } = useSWR<EntityOverview[]>(
    "/analytics/entities?limit=15",
    fetcher
  );
  const { data: sources } = useSWR<MediaSource[]>("/sources", fetcher);

  // Fetch bias trends for all sources
  const { data: kpTrend } = useSWR<MediaBiasTrend>(
    `/sources/kathmandu-post/bias-trend?days=${days}`,
    fetcher
  );
  const { data: repTrend } = useSWR<MediaBiasTrend>(
    `/sources/republica/bias-trend?days=${days}`,
    fetcher
  );
  const { data: okTrend } = useSWR<MediaBiasTrend>(
    `/sources/online-khabar/bias-trend?days=${days}`,
    fetcher
  );

  const multiSourceDatasets = [
    kpTrend && { sourceSlug: "kathmandu-post", sourceName: "Kathmandu Post", data: kpTrend.trend },
    repTrend && { sourceSlug: "republica", sourceName: "Republica", data: repTrend.trend },
    okTrend && { sourceSlug: "online-khabar", sourceName: "OnlineKhabar", data: okTrend.trend },
  ].filter(Boolean) as any[];

  return (
    <div className="min-h-screen bg-base-900">
      <div className="fixed inset-0 bg-glow-gold pointer-events-none" />

      <div className="relative">
        {/* Header */}
        <div className="px-8 py-6 border-b border-base-800 bg-base-950/50 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <BarChart3 size={16} className="text-gold-400" />
                <span className="text-[11px] uppercase tracking-wider text-base-500">
                  Intelligence
                </span>
              </div>
              <h1 className="text-xl font-display font-600 text-base-100">Analytics</h1>
            </div>

            {/* Day range toggle */}
            <div className="flex rounded-lg overflow-hidden border border-base-600">
              {[7, 14, 30].map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`px-4 py-2 text-xs transition-all ${
                    days === d
                      ? "bg-base-700 text-base-100"
                      : "text-base-500 hover:text-base-300"
                  } ${d !== 7 ? "border-l border-base-600" : ""}`}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="px-8 py-6 space-y-8">
          {/* Row 1: Bias Distribution + Source comparison */}
          <div className="grid grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-5"
            >
              <SectionHeader
                icon={<Activity size={15} className="text-gold-400" />}
                title="Bias Score Distribution"
                sub="How articles are distributed across the bias spectrum"
              />
              {distribution ? (
                <BiasDistributionChart data={distribution} />
              ) : (
                <div className="skeleton h-40 rounded-lg" />
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="glass-card p-5"
            >
              <SectionHeader
                icon={<TrendingUp size={15} className="text-cyan-400" />}
                title="Media House Bias Trends"
                sub={`Bias score over the last ${days} days`}
              />
              {multiSourceDatasets.length > 0 ? (
                <MultiSourceBiasChart datasets={multiSourceDatasets} />
              ) : (
                <div className="skeleton h-40 rounded-lg" />
              )}
            </motion.div>
          </div>

          {/* Row 2: Entity sentiment */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-5"
          >
            <SectionHeader
              icon={<Users size={15} className="text-purple-400" />}
              title="Political Entity Sentiment"
              sub="Average sentiment score per entity across all analyzed articles"
            />
            {entities ? (
              <EntitySentimentChart data={entities} />
            ) : (
              <div className="skeleton h-56 rounded-lg" />
            )}
            <p className="text-[11px] text-base-600 mt-3 text-center">
              Scores range from −1.0 (very negative coverage) to +1.0 (very positive). Derived from LLM aspect-based sentiment analysis.
            </p>
          </motion.div>

          {/* Row 3: Source cards */}
          {sources && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <SectionHeader
                icon={<BarChart3 size={15} className="text-emerald-400" />}
                title="Media House Report Cards"
                sub="Aggregated bias metrics per publication"
              />
              <div className="grid grid-cols-3 gap-4">
                {sources.map((source, i) => (
                  <SourceReportCard key={source.id} source={source} index={i} />
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

function SourceReportCard({ source, index }: { source: MediaSource; index: number }) {
  const SOURCE_COLORS: Record<string, string> = {
    "kathmandu-post": "#00D4FF",
    "republica": "#F5C542",
    "online-khabar": "#A78BFA",
  };
  const color = SOURCE_COLORS[source.slug] || "#8B949E";
  const biasLabel =
    source.avg_bias_score < 0.35
      ? "Mostly Neutral"
      : source.avg_bias_score < 0.65
      ? "Moderate Bias"
      : "High Bias";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.05 }}
      className="glass-card p-5 relative overflow-hidden"
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-0.5 rounded-r"
        style={{ background: color }}
      />
      <div className="pl-3">
        <h3 className="text-sm font-display font-600 text-base-100 mb-1">
          {source.name}
        </h3>
        <p className="text-[11px] text-base-500 mb-3">{source.total_articles} articles analyzed</p>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[11px] text-base-500">Avg Bias</span>
            <span
              className="text-[11px] font-mono font-medium"
              style={{
                color:
                  source.avg_bias_score < 0.35
                    ? "#34D399"
                    : source.avg_bias_score < 0.65
                    ? "#F5C542"
                    : "#FF6B6B",
              }}
            >
              {Math.round(source.avg_bias_score * 100)}% · {biasLabel}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-base-700">
            <div
              className="h-1.5 rounded-full transition-all duration-700"
              style={{
                width: `${Math.round(source.avg_bias_score * 100)}%`,
                background:
                  source.avg_bias_score < 0.35
                    ? "linear-gradient(90deg,#34D399,#10B981)"
                    : source.avg_bias_score < 0.65
                    ? "linear-gradient(90deg,#F5C542,#E6A817)"
                    : "linear-gradient(90deg,#FF6B6B,#DC2626)",
              }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
