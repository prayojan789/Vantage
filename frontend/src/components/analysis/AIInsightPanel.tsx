"use client";
import { motion } from "framer-motion";
import { Brain, Zap, AlertCircle, ChevronRight } from "lucide-react";
import { EntityPill } from "@/components/ui/EntityPill";
import { BiasScoreBar } from "@/components/ui/BiasScoreBar";
import { getBiasLabel } from "@/lib/utils";
import type { LLMAnalysisResult } from "@/types";

interface AIInsightPanelProps {
  analysis: LLMAnalysisResult;
  articleTitle?: string;
}

export function AIInsightPanel({ analysis, articleTitle }: AIInsightPanelProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-1">
        <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-cyan-400/8 border border-cyan-400/20">
          <Brain size={13} className="text-cyan-400" />
          <span className="text-[11px] font-medium text-cyan-400 uppercase tracking-wider">
            AI Reasoning
          </span>
        </div>
        <span className="text-[10px] text-base-500 font-mono">
          via {analysis.provider}/{analysis.model_name} · {analysis.latency_ms}ms
        </span>
      </div>

      {/* Bias Score */}
      <div className="glass-card p-4">
        <BiasScoreBar score={analysis.bias_score} size="lg" />
      </div>

      {/* Framing Analysis */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-2">
          <Zap size={12} className="text-gold-400" />
          <span className="text-[11px] uppercase tracking-wider text-base-400">
            Framing Analysis
          </span>
        </div>
        <p className="text-sm text-base-300 leading-relaxed">
          {analysis.framing_analysis}
        </p>
      </div>

      {/* Bias Reasoning */}
      <div className="glass-card p-4 border-crimson-400/15">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle size={12} className="text-crimson-400" />
          <span className="text-[11px] uppercase tracking-wider text-base-400">
            Why This Is Biased
          </span>
        </div>
        <p className="text-sm text-base-300 leading-relaxed">
          {analysis.bias_reasoning}
        </p>
      </div>

      {/* Entity Sentiments */}
      {analysis.entities.length > 0 && (
        <div className="glass-card p-4">
          <p className="text-[11px] uppercase tracking-wider text-base-400 mb-3">
            Entity Sentiment
          </p>
          <div className="space-y-3">
            {analysis.entities.map((entity) => (
              <motion.div
                key={entity.name}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-3"
              >
                <EntityPill entity={entity} showScore />
                <div className="flex-1 min-w-0">
                  {entity.context_snippet && (
                    <p className="text-[11px] text-base-400 italic leading-relaxed line-clamp-2">
                      "{entity.context_snippet}"
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-0.5 rounded-full bg-base-700">
                      <div
                        className="h-0.5 rounded-full"
                        style={{
                          width: `${Math.abs(entity.sentiment_score) * 100}%`,
                          marginLeft: entity.sentiment_score < 0 ? `${100 - Math.abs(entity.sentiment_score) * 100}%` : "0",
                          background: entity.sentiment_score > 0.3 ? "#34D399" : entity.sentiment_score < -0.3 ? "#FF6B6B" : "#8B949E",
                        }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Event Summary */}
      {analysis.event_summary && (
        <div className="glass-card p-4">
          <p className="text-[11px] uppercase tracking-wider text-base-400 mb-2">
            Event Summary
          </p>
          <p className="text-sm text-base-300 leading-relaxed">
            {analysis.event_summary}
          </p>
        </div>
      )}
    </div>
  );
}
