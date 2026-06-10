// VANTAGE — Utility Functions
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Returns color class based on bias score 0–1 */
export function getBiasColor(score: number): string {
  if (score < 0.35) return "text-emerald-400";
  if (score < 0.65) return "text-gold-400";
  return "text-crimson-400";
}

export function getBiasBadgeClass(score: number): string {
  if (score < 0.35) return "bias-badge-low";
  if (score < 0.65) return "bias-badge-mid";
  return "bias-badge-high";
}

export function getBiasLabel(score: number): string {
  if (score < 0.25) return "Neutral";
  if (score < 0.45) return "Slight Bias";
  if (score < 0.65) return "Moderate Bias";
  if (score < 0.80) return "High Bias";
  return "Heavily Biased";
}

export function getSentimentColor(sentiment: string): string {
  switch (sentiment) {
    case "positive": return "text-emerald-400";
    case "negative": return "text-crimson-400";
    default: return "text-base-300";
  }
}

export function getSentimentBg(score: number): string {
  if (score > 0.3) return "rgba(52, 211, 153, 0.12)";
  if (score < -0.3) return "rgba(255, 107, 107, 0.12)";
  return "rgba(139, 148, 158, 0.1)";
}

export function formatDate(dateString: string): string {
  const d = new Date(dateString);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function timeAgo(dateString: string): string {
  const d = new Date(dateString);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "…";
}
