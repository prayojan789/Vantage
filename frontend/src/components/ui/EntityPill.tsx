"use client";
import { cn } from "@/lib/utils";
import type { EntitySentiment } from "@/types";

interface EntityPillProps {
  entity: EntitySentiment;
  showScore?: boolean;
  onClick?: () => void;
}

const FRAMING_COLORS: Record<string, string> = {
  critical: "bg-crimson-400/10 text-crimson-400 border-crimson-400/25",
  supportive: "bg-emerald-400/10 text-emerald-400 border-emerald-400/25",
  neutral: "bg-base-500/10 text-base-300 border-base-500/20",
  mixed: "bg-gold-400/10 text-gold-400 border-gold-400/25",
};

const TYPE_ICONS: Record<string, string> = {
  PERSON: "P",
  ORG: "O",
  PARTY: "★",
  LOCATION: "◎",
};

export function EntityPill({ entity, showScore = false, onClick }: EntityPillProps) {
  const colorClass = FRAMING_COLORS[entity.framing] || FRAMING_COLORS.neutral;
  const scoreDisplay = entity.sentiment_score > 0
    ? `+${entity.sentiment_score.toFixed(2)}`
    : entity.sentiment_score.toFixed(2);

  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all",
        "hover:brightness-110 cursor-pointer",
        colorClass
      )}
      title={entity.context_snippet}
    >
      <span className="opacity-60 font-mono text-[10px]">
        {TYPE_ICONS[entity.type] || "·"}
      </span>
      <span>{entity.name}</span>
      {showScore && (
        <span className="font-mono opacity-70 text-[10px]">{scoreDisplay}</span>
      )}
    </button>
  );
}
