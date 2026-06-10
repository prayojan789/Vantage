"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import useSWR from "swr";
import {
  Eye, ArrowRight, Layers, BarChart3, FlaskConical,
  Newspaper, Zap, Brain, GitBranch, Activity
} from "lucide-react";
import { DashboardStatsRow } from "@/components/analysis/DashboardStats";
import { fetcher } from "@/lib/api";
import type { DashboardStats, NewsEvent } from "@/types";
import { timeAgo, getBiasLabel } from "@/lib/utils";

function PipelineStep({
  step, label, detail, color, delay
}: { step: string; label: string; detail: string; color: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="flex items-start gap-4"
    >
      <div
        className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-mono font-600"
        style={{ background: `${color}18`, color, border: `1px solid ${color}30` }}
      >
        {step}
      </div>
      <div>
        <p className="text-sm font-medium text-base-200">{label}</p>
        <p className="text-xs text-base-500 mt-0.5">{detail}</p>
      </div>
    </motion.div>
  );
}

export default function OverviewPage() {
  const { data: stats } = useSWR<DashboardStats>("/dashboard/stats", fetcher);
  const { data: events } = useSWR<NewsEvent[]>("/events?limit=5", fetcher);

  return (
    <div className="min-h-screen bg-base-900">
      {/* Background effects */}
      <div className="fixed inset-0 bg-glow-cyan pointer-events-none" />
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-30 pointer-events-none" />

      <div className="relative px-8 py-10 space-y-10 max-w-5xl">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-2 mb-4">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, rgba(0,212,255,0.15), rgba(245,197,66,0.1))",
                border: "1px solid rgba(0,212,255,0.25)",
              }}
            >
              <Eye size={20} className="text-cyan-400" />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-700 text-base-100 text-xl tracking-tight">
                VANTAGE
              </span>
              <span className="text-[10px] text-base-500 uppercase tracking-widest -mt-0.5">
                Nepal Media Intelligence
              </span>
            </div>
          </div>

          <h1 className="text-3xl font-display font-700 text-base-100 leading-tight mb-3">
            Understand how Nepal's media{" "}
            <span
              className="text-glow-cyan"
              style={{
                background: "linear-gradient(135deg, #00D4FF, #F5C542)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              shapes political perception
            </span>
          </h1>
          <p className="text-base text-base-400 max-w-2xl leading-relaxed">
            VANTAGE uses LLM-powered reasoning to detect entity-level bias in English-language
            Nepali news. Compare how Kathmandu Post, Republica, and OnlineKhabar frame the same
            political event — and get AI explanations for every bias score.
          </p>

          <div className="flex items-center gap-3 mt-6">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
              style={{
                background: "linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,212,255,0.05))",
                border: "1px solid rgba(0,212,255,0.3)",
                color: "#00D4FF",
              }}
            >
              Open Dashboard <ArrowRight size={14} />
            </Link>
            <Link
              href="/playground"
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium text-base-300 bg-base-800 border border-base-600 hover:border-base-500 transition-all"
            >
              <FlaskConical size={14} /> Try Playground
            </Link>
          </div>
        </motion.div>

        {/* Live stats */}
        {stats && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-[11px] uppercase tracking-wider text-base-600 mb-3 flex items-center gap-2">
              <Activity size={10} className="text-emerald-400" />
              Live Platform Stats
            </p>
            <DashboardStatsRow stats={stats} />
          </motion.div>
        )}

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h2 className="text-sm font-display font-600 text-base-200 mb-5">
            How the Pipeline Works
          </h2>
          <div className="grid grid-cols-2 gap-x-10 gap-y-5">
            <PipelineStep step="01" label="Ingestion" color="#8B949E"
              detail="Scrapy spiders crawl RSS feeds from 3 Nepali news portals every 30 minutes"
              delay={0.35}
            />
            <PipelineStep step="02" label="Embedding & Clustering" color="#A78BFA"
              detail="sentence-transformers vectorizes each article; cosine similarity groups related articles into Events"
              delay={0.4}
            />
            <PipelineStep step="03" label="LLM Analysis" color="#00D4FF"
              detail="GPT-4o or LLaMA3 extracts entities, assigns per-entity sentiment, scores bias, and explains framing"
              delay={0.45}
            />
            <PipelineStep step="04" label="Intelligence Dashboard" color="#F5C542"
              detail="Real-time dashboard surfaces bias divergence, media report cards, and AI reasoning panels"
              delay={0.5}
            />
          </div>
        </motion.div>

        {/* Recent Events */}
        {events && events.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex items-center justify-between mb-4">
              <p className="text-[11px] uppercase tracking-wider text-base-600 flex items-center gap-2">
                <Layers size={10} className="text-cyan-400" />
                Recent Event Clusters
              </p>
              <Link
                href="/dashboard"
                className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
              >
                View all <ArrowRight size={10} />
              </Link>
            </div>
            <div className="space-y-2">
              {events.map((event, i) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.04 }}
                >
                  <Link href="/dashboard">
                    <div className="glass-card px-4 py-3 flex items-center gap-4 hover:border-base-500 transition-all group">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-base-200 group-hover:text-cyan-400 truncate transition-colors">
                          {event.title}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[10px] text-base-600 flex items-center gap-1">
                            <GitBranch size={9} />
                            {event.article_count} sources
                          </span>
                          <span className="text-[10px] text-base-600">·</span>
                          <span className="text-[10px] text-base-600">
                            {timeAgo(event.first_seen_at)}
                          </span>
                        </div>
                      </div>
                      <div
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full flex-shrink-0 ${
                          event.bias_divergence_score > 0.3
                            ? "bg-gold-400/10 text-gold-400 border border-gold-400/20"
                            : "bg-base-800 text-base-500 border border-base-700"
                        }`}
                      >
                        {event.bias_divergence_score > 0.3 ? "⚡ Divergent" : "Aligned"}
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Feature cards */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-[11px] uppercase tracking-wider text-base-600 mb-4">
            Platform Capabilities
          </p>
          <div className="grid grid-cols-3 gap-4">
            {[
              {
                icon: <Layers size={16} className="text-cyan-400" />,
                title: "Event Clustering",
                desc: "Groups articles across publishers covering the same story for instant framing comparison",
                href: "/dashboard",
                color: "#00D4FF",
              },
              {
                icon: <Brain size={16} className="text-purple-400" />,
                title: "AI Bias Reasoning",
                desc: "LLM explains why bias was detected with textual evidence, not just a score",
                href: "/dashboard",
                color: "#A78BFA",
              },
              {
                icon: <FlaskConical size={16} className="text-gold-400" />,
                title: "Live Playground",
                desc: "Paste any text and get real-time entity extraction + bias analysis from the LLM",
                href: "/playground",
                color: "#F5C542",
              },
            ].map(({ icon, title, desc, href, color }) => (
              <Link key={title} href={href}>
                <div className="glass-card p-4 h-full hover:border-base-500 transition-all group cursor-pointer">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center mb-3"
                    style={{ background: `${color}15`, border: `1px solid ${color}25` }}
                  >
                    {icon}
                  </div>
                  <h3 className="text-sm font-medium text-base-200 mb-1.5 group-hover:text-base-100 transition-colors">
                    {title}
                  </h3>
                  <p className="text-xs text-base-500 leading-relaxed">{desc}</p>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
