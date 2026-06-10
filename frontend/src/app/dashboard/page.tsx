"use client";
import { useState } from "react";
import useSWR from "swr";
import { motion } from "framer-motion";
import { Layers, RefreshCw, Filter } from "lucide-react";
import { EventCard } from "@/components/analysis/EventCard";
import { AIInsightPanel } from "@/components/analysis/AIInsightPanel";
import { DashboardStatsRow } from "@/components/analysis/DashboardStats";
import { LLMProviderToggle } from "@/components/ui/LLMProviderToggle";
import { fetcher } from "@/lib/api";
import type { NewsEvent, DashboardStats } from "@/types";

export default function DashboardPage() {
  const [selectedEvent, setSelectedEvent] = useState<NewsEvent | null>(null);
  const { data: events, isLoading: eventsLoading, mutate } = useSWR<NewsEvent[]>("/events?limit=30", fetcher);
  const { data: stats } = useSWR<DashboardStats>("/dashboard/stats", fetcher);

  const selectedArticle = selectedEvent?.articles[0];
  const selectedAnalysis = selectedArticle?.entity_sentiments.length
    ? {
        entities: selectedArticle.entity_sentiments,
        bias_score: selectedArticle.bias_score ?? 0,
        framing_analysis: selectedArticle.framing_analysis ?? "",
        bias_reasoning: "",
        event_summary: selectedEvent?.summary ?? "",
        overall_sentiment: "neutral" as const,
        provider: "openai" as const,
        model_name: "gpt-4o-mini",
        latency_ms: 0,
      }
    : null;

  return (
    <div className="min-h-screen bg-base-900">
      {/* Background grid */}
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-40 pointer-events-none" />

      <div className="relative">
        {/* Page Header */}
        <div className="px-8 py-6 border-b border-base-800 bg-base-950/50 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Layers size={16} className="text-cyan-400" />
                <span className="text-[11px] uppercase tracking-wider text-base-500">
                  Event Intelligence
                </span>
              </div>
              <h1 className="text-xl font-display font-600 text-base-100">
                Event Clusters
              </h1>
            </div>
            <button
              onClick={() => mutate()}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm text-base-400 hover:text-base-200 bg-base-800 hover:bg-base-700 border border-base-600 transition-all"
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>
        </div>

        <div className="px-8 py-6 space-y-6">
          {/* Stats */}
          {stats && <DashboardStatsRow stats={stats} />}

          <div className="grid grid-cols-12 gap-6">
            {/* Event List */}
            <div className="col-span-7 space-y-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-base-500 uppercase tracking-wider">
                  {events?.length ?? 0} events tracked
                </span>
              </div>

              {eventsLoading && (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="glass-card p-5">
                      <div className="skeleton h-4 w-3/4 mb-3" />
                      <div className="skeleton h-3 w-full mb-2" />
                      <div className="skeleton h-3 w-1/2" />
                    </div>
                  ))}
                </div>
              )}

              {events?.map((event, i) => (
                <EventCard
                  key={event.id}
                  event={event}
                  index={i}
                  onClick={() => setSelectedEvent(event)}
                />
              ))}
            </div>

            {/* Right Panel */}
            <div className="col-span-5 space-y-4">
              {/* LLM Toggle */}
              <LLMProviderToggle />

              {/* AI Insight Panel */}
              {selectedEvent && selectedAnalysis ? (
                <motion.div
                  key={selectedEvent.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="mb-3">
                    <p className="text-[11px] text-base-500 uppercase tracking-wider mb-1">
                      Analyzing
                    </p>
                    <p className="text-sm font-medium text-base-200 line-clamp-2">
                      {selectedEvent.title}
                    </p>
                  </div>
                  <AIInsightPanel analysis={selectedAnalysis} />
                </motion.div>
              ) : (
                <div className="glass-card p-6 text-center">
                  <div className="w-10 h-10 rounded-full bg-base-800 flex items-center justify-center mx-auto mb-3">
                    <Layers size={18} className="text-base-500" />
                  </div>
                  <p className="text-sm text-base-400">
                    Select an event cluster to view AI analysis
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
