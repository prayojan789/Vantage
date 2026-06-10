"use client";
import { cn, getBiasLabel } from "@/lib/utils";

interface BiasScoreBarProps {
  score: number;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function BiasScoreBar({ score, showLabel = true, size = "md", className }: BiasScoreBarProps) {
  const pct = Math.round(score * 100);

  const barColor =
    score < 0.35
      ? "linear-gradient(90deg, #34D399, #10B981)"
      : score < 0.65
      ? "linear-gradient(90deg, #F5C542, #E6A817)"
      : "linear-gradient(90deg, #FF6B6B, #DC2626)";

  const heights = { sm: "h-1", md: "h-1.5", lg: "h-2" };
  const fontSizes = { sm: "text-[11px]", md: "text-xs", lg: "text-sm" };

  return (
    <div className={cn("w-full", className)}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1.5">
          <span className={cn("font-mono text-base-400", fontSizes[size])}>
            Bias Score
          </span>
          <span className={cn("font-mono font-medium", fontSizes[size],
            score < 0.35 ? "text-emerald-400" : score < 0.65 ? "text-gold-400" : "text-crimson-400"
          )}>
            {pct}% · {getBiasLabel(score)}
          </span>
        </div>
      )}
      <div className={cn("w-full rounded-full bg-base-700", heights[size])}>
        <div
          className={cn("rounded-full transition-all duration-700", heights[size])}
          style={{ width: `${pct}%`, background: barColor }}
        />
      </div>
    </div>
  );
}
