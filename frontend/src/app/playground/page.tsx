"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FlaskConical, Play, Loader2, Cpu, Cloud, Trash2 } from "lucide-react";
import { AIInsightPanel } from "@/components/analysis/AIInsightPanel";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import type { LLMAnalysisResult } from "@/types";

const SAMPLE_TEXT = `Prime Minister KP Sharma Oli on Wednesday criticized the Rastriya Swatantra Party leadership for what he called "irresponsible opposition" to the government's new infrastructure development bill. Speaking at a party function in Kathmandu, Oli accused RSP chairman Rabi Lamichhane of playing politics with issues of national importance. Meanwhile, opposition leader Sher Bahadur Deuba called for a parliamentary committee to review the bill before it is passed, saying the government was rushing legislation without proper deliberation. The Maoist Centre, which supports the current coalition government, declined to comment.`;

export default function PlaygroundPage() {
  const [text, setText] = useState(SAMPLE_TEXT);
  const [provider, setProvider] = useState<"openai" | "ollama" | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LLMAnalysisResult | null>(null);
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  async function runAnalysis() {
    if (text.trim().length < 50) {
      toast.error("Please enter at least 50 characters");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await api.playgroundAnalyze(text, provider) as any;
      setResult(res.analysis);
      toast.success("Analysis complete");
    } catch (e: any) {
      toast.error(e.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-base-900">
      <div className="fixed inset-0 bg-glow-cyan pointer-events-none" />

      <div className="relative">
        {/* Header */}
        <div className="px-8 py-6 border-b border-base-800 bg-base-950/50 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-2">
            <FlaskConical size={16} className="text-gold-400" />
            <span className="text-[11px] uppercase tracking-wider text-base-500">
              Live Analysis
            </span>
          </div>
          <h1 className="text-xl font-display font-600 text-base-100 mt-1">
            AI Playground
          </h1>
        </div>

        <div className="px-8 py-6">
          <div className="grid grid-cols-12 gap-6">
            {/* Input Panel */}
            <div className="col-span-7 space-y-4">
              <div className="glass-card p-1 rounded-xl overflow-hidden">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste any Nepali political news article here…"
                  className="w-full h-72 bg-transparent text-sm text-base-200 placeholder:text-base-600 p-4 resize-none focus:outline-none leading-relaxed font-body"
                />
                <div className="flex items-center justify-between px-4 pb-3 border-t border-base-800">
                  <span className="text-[11px] text-base-500 font-mono">
                    {wordCount} words · {text.length} characters
                  </span>
                  <button
                    onClick={() => { setText(""); setResult(null); }}
                    className="text-base-600 hover:text-base-400 transition-colors"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>

              {/* Provider + Run */}
              <div className="flex items-center gap-3">
                {/* Provider toggle */}
                <div className="flex rounded-lg overflow-hidden border border-base-600 flex-shrink-0">
                  <button
                    onClick={() => setProvider(undefined)}
                    className={`px-3 py-2 text-xs flex items-center gap-1.5 transition-all ${
                      provider === undefined
                        ? "bg-base-700 text-base-200"
                        : "text-base-500 hover:text-base-300"
                    }`}
                  >
                    Auto
                  </button>
                  <button
                    onClick={() => setProvider("openai")}
                    className={`px-3 py-2 text-xs flex items-center gap-1.5 border-l border-base-600 transition-all ${
                      provider === "openai"
                        ? "bg-cyan-400/15 text-cyan-400"
                        : "text-base-500 hover:text-base-300"
                    }`}
                  >
                    <Cloud size={11} /> OpenAI
                  </button>
                  <button
                    onClick={() => setProvider("ollama")}
                    className={`px-3 py-2 text-xs flex items-center gap-1.5 border-l border-base-600 transition-all ${
                      provider === "ollama"
                        ? "bg-gold-400/15 text-gold-400"
                        : "text-base-500 hover:text-base-300"
                    }`}
                  >
                    <Cpu size={11} /> Ollama
                  </button>
                </div>

                <button
                  onClick={runAnalysis}
                  disabled={loading || text.trim().length < 50}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: loading ? "rgba(0,212,255,0.08)" : "linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,212,255,0.05))",
                    border: "1px solid rgba(0,212,255,0.25)",
                    color: "#00D4FF",
                  }}
                >
                  {loading ? (
                    <><Loader2 size={15} className="animate-spin" /> Analyzing…</>
                  ) : (
                    <><Play size={15} /> Run Analysis</>
                  )}
                </button>
              </div>

              {/* Sample text helper */}
              {!result && !loading && (
                <p className="text-[11px] text-base-600 text-center">
                  Using sample text above — replace with any English-language Nepali political news
                </p>
              )}
            </div>

            {/* Result Panel */}
            <div className="col-span-5">
              <AnimatePresence mode="wait">
                {loading && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="glass-card p-8 text-center space-y-4"
                  >
                    <div className="relative mx-auto w-16 h-16">
                      <div className="absolute inset-0 rounded-full border-2 border-cyan-400/20 animate-ping" />
                      <div className="absolute inset-2 rounded-full border-2 border-cyan-400/40 animate-spin"
                        style={{ animationDuration: "2s" }} />
                      <div className="absolute inset-4 rounded-full bg-cyan-400/10 flex items-center justify-center">
                        <FlaskConical size={12} className="text-cyan-400" />
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-base-200">LLM reasoning…</p>
                      <p className="text-xs text-base-500 mt-1">Extracting entities & detecting bias</p>
                    </div>
                  </motion.div>
                )}

                {result && !loading && (
                  <motion.div
                    key="result"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                  >
                    <AIInsightPanel analysis={result} />
                  </motion.div>
                )}

                {!result && !loading && (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="glass-card p-8 text-center"
                  >
                    <div className="w-12 h-12 rounded-full bg-base-800 flex items-center justify-center mx-auto mb-4">
                      <FlaskConical size={20} className="text-base-500" />
                    </div>
                    <p className="text-sm text-base-400 mb-1">
                      Paste a news article and click Run Analysis
                    </p>
                    <p className="text-xs text-base-600">
                      Works with any English political news from Nepal
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
