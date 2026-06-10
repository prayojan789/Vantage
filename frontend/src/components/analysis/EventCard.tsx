"use client";
import { motion } from "framer-motion";
import { ExternalLink, GitBranch, AlertTriangle } from "lucide-react";
import { BiasScoreBar } from "@/components/ui/BiasScoreBar";
import { EntityPill } from "@/components/ui/EntityPill";
import { cn, timeAgo, truncate } from "@/lib/utils";
import type { NewsEvent } from "@/types";

interface EventCardProps {
  event: NewsEvent;
  onClick?: () => void;
  index?: number;
}

const SOURCE_COLORS: Record<string, string> = {
  "kathmandu-post": "#00D4FF",
  "republica": "#F5C542",
  "online-khabar": "#A78BFA",
};

export function EventCard({ event, onClick, index = 0 }: EventCardProps) {
  const allEntities = event.articles
    .flatMap((a) => a.entity_sentiments)
    .filter((e, i, arr) => arr.findIndex((x) => x.name === e.name) === i)
    .slice(0, 5);

  const divergenceHigh = event.bias_divergence_score > 0.3;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      onClick={onClick}
      className="glass-card p-5 cursor-pointer hover:border-base-500 transition-all duration-200 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-sm font-display font-medium text-base-100 leading-snug group-hover:text-cyan-400 transition-colors line-clamp-2">
          {event.title}
        </h3>
        {divergenceHigh && (
          <span className="flex-shrink-0 flex items-center gap-1 text-[10px] text-gold-400 bg-gold-400/10 border border-gold-400/20 rounded-full px-2 py-0.5">
            <AlertTriangle size={9} />
            Divergent
          </span>
        )}
      </div>

      {/* Summary */}
      {event.summary && (
        <p className="text-xs text-base-400 leading-relaxed mb-3 line-clamp-2">
          {truncate(event.summary, 140)}
        </p>
      )}

      {/* Entities */}
      {allEntities.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {allEntities.map((entity) => (
            <EntityPill key={entity.name} entity={entity} />
          ))}
        </div>
      )}

      {/* Sources comparison */}
      <div className="space-y-1.5 mb-3">
        {event.articles.map((article) => {
          const color = SOURCE_COLORS[article.source_slug] || "#8B949E";
          const score = article.bias_score ?? 0;
          return (
            <div key={article.id} className="flex items-center gap-2">
              <span
                className="text-[10px] font-medium w-28 flex-shrink-0 truncate"
                style={{ color }}
              >
                {article.source_name}
              </span>
              <div className="flex-1 h-1 rounded-full bg-base-700">
                <div
                  className="h-1 rounded-full transition-all duration-700"
                  style={{
                    width: `${Math.round(score * 100)}%`,
                    background: score < 0.35 ? "#34D399" : score < 0.65 ? "#F5C542" : "#FF6B6B",
                  }}
                />
              </div>
              <span className="text-[10px] font-mono text-base-400 w-8 text-right">
                {Math.round(score * 100)}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-base-700">
        <div className="flex items-center gap-3 text-[11px] text-base-500">
          <span className="flex items-center gap-1">
            <GitBranch size={10} />
            {event.article_count} {event.article_count === 1 ? "source" : "sources"}
          </span>
          <span>{timeAgo(event.first_seen_at)}</span>
        </div>
        <span className="text-[10px] text-base-500 group-hover:text-cyan-400 flex items-center gap-1 transition-colors">
          View analysis <ExternalLink size={9} />
        </span>
      </div>
    </motion.div>
  );
}
