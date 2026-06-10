"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Cloud, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import type { LLMProviderStatus } from "@/types";

export function LLMProviderToggle() {
  const [status, setStatus] = useState<LLMProviderStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  async function loadStatus() {
    try {
      const data = await api.getLLMStatus();
      setStatus(data as LLMProviderStatus);
    } catch {
      // silent
    }
  }

  async function switchProvider(provider: "openai" | "ollama") {
    if (!status || status.current_provider === provider) return;
    setLoading(true);
    try {
      await api.setLLMProvider(provider);
      await loadStatus();
      toast.success(`Switched to ${provider === "openai" ? "OpenAI GPT" : "Ollama (local)"}`);
    } catch {
      toast.error("Failed to switch provider");
    } finally {
      setLoading(false);
    }
  }

  if (!status) return null;

  return (
    <div className="glass-card p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[11px] uppercase tracking-wider text-base-400">
          LLM Engine
        </span>
        {loading && <Loader2 size={12} className="text-cyan-400 animate-spin" />}
      </div>

      <div className="grid grid-cols-2 gap-2">
        {/* OpenAI */}
        <button
          onClick={() => switchProvider("openai")}
          disabled={loading}
          className={cn(
            "flex flex-col items-center gap-2 p-3 rounded-lg border transition-all text-xs",
            status.current_provider === "openai"
              ? "bg-cyan-400/10 border-cyan-400/30 text-cyan-400"
              : "bg-base-800 border-base-600 text-base-400 hover:border-base-500"
          )}
        >
          <Cloud size={16} />
          <span className="font-medium">OpenAI</span>
          <span className={cn(
            "flex items-center gap-1 text-[10px]",
            status.openai_configured ? "text-emerald-400" : "text-crimson-400"
          )}>
            {status.openai_configured
              ? <><CheckCircle size={9} /> Ready</>
              : <><XCircle size={9} /> No key</>
            }
          </span>
        </button>

        {/* Ollama */}
        <button
          onClick={() => switchProvider("ollama")}
          disabled={loading}
          className={cn(
            "flex flex-col items-center gap-2 p-3 rounded-lg border transition-all text-xs",
            status.current_provider === "ollama"
              ? "bg-gold-400/10 border-gold-400/30 text-gold-400"
              : "bg-base-800 border-base-600 text-base-400 hover:border-base-500"
          )}
        >
          <Cpu size={16} />
          <span className="font-medium">Ollama</span>
          <span className={cn(
            "flex items-center gap-1 text-[10px]",
            status.ollama_available ? "text-emerald-400" : "text-crimson-400"
          )}>
            {status.ollama_available
              ? <><CheckCircle size={9} /> Local</>
              : <><XCircle size={9} /> Offline</>
            }
          </span>
        </button>
      </div>

      <div className="text-[11px] text-base-500 font-mono text-center">
        Active: {status.current_model}
      </div>
    </div>
  );
}
