"use client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell, Legend
} from "recharts";
import type { BiasDistributionBucket, EntityOverview } from "@/types";

const SOURCE_COLORS: Record<string, string> = {
  "kathmandu-post": "#00D4FF",
  "republica": "#F5C542",
  "online-khabar": "#A78BFA",
};

const COMMON_AXIS = {
  tick: { fill: "#6E7681", fontSize: 11 },
  axisLine: { stroke: "#30363D" },
  tickLine: false,
};

const TOOLTIP_STYLE = {
  contentStyle: {
    background: "#161B22",
    border: "1px solid #30363D",
    borderRadius: "8px",
    fontSize: "12px",
    color: "#C9D1D9",
  },
  cursor: { fill: "rgba(255,255,255,0.03)" },
};

// ── Bias over time for a single source ───────────────────
export function BiasTrendChart({ data, sourceSlug }: { data: any[]; sourceSlug: string }) {
  const color = SOURCE_COLORS[sourceSlug] || "#8B949E";
  return (
    <ResponsiveContainer width="100%" height={160}>
      <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id={`gradient-${sourceSlug}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.2} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1C2128" />
        <XAxis dataKey="date" {...COMMON_AXIS} />
        <YAxis domain={[0, 1]} {...COMMON_AXIS} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Area
          type="monotone"
          dataKey="bias_score"
          stroke={color}
          strokeWidth={2}
          fill={`url(#gradient-${sourceSlug})`}
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// ── Bias distribution histogram ───────────────────────────
export function BiasDistributionChart({ data }: { data: BiasDistributionBucket[] }) {
  const colors = ["#34D399", "#86EFAC", "#F5C542", "#FF6B6B", "#DC2626"];
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1C2128" />
        <XAxis dataKey="range" {...COMMON_AXIS} />
        <YAxis {...COMMON_AXIS} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={entry.range} fill={colors[index]} fillOpacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Entity sentiment bar chart ────────────────────────────
export function EntitySentimentChart({ data }: { data: EntityOverview[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 20, bottom: 0, left: 80 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#1C2128" horizontal={false} />
        <XAxis type="number" domain={[-1, 1]} {...COMMON_AXIS} />
        <YAxis type="category" dataKey="name" {...COMMON_AXIS} width={80} />
        <Tooltip {...TOOLTIP_STYLE} formatter={(v: number) => [v.toFixed(2), "Sentiment"]} />
        <Bar dataKey="avg_sentiment" radius={[0, 4, 4, 0]}>
          {data.map((entry) => (
            <Cell
              key={entry.name}
              fill={entry.avg_sentiment > 0.2 ? "#34D399" : entry.avg_sentiment < -0.2 ? "#FF6B6B" : "#6E7681"}
              fillOpacity={0.85}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Multi-source bias comparison ──────────────────────────
export function MultiSourceBiasChart({ datasets }: { datasets: { sourceSlug: string; sourceName: string; data: any[] }[] }) {
  // Merge all data by date
  const allDates = [...new Set(datasets.flatMap((d) => d.data.map((p) => p.date)))].sort();
  const merged = allDates.map((date) => {
    const point: Record<string, any> = { date };
    datasets.forEach(({ sourceSlug, data }) => {
      const found = data.find((p) => p.date === date);
      point[sourceSlug] = found?.bias_score ?? null;
    });
    return point;
  });

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={merged} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
        <defs>
          {datasets.map(({ sourceSlug }) => {
            const color = SOURCE_COLORS[sourceSlug] || "#8B949E";
            return (
              <linearGradient key={sourceSlug} id={`mg-${sourceSlug}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.15} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            );
          })}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1C2128" />
        <XAxis dataKey="date" {...COMMON_AXIS} />
        <YAxis domain={[0, 1]} {...COMMON_AXIS} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Legend wrapperStyle={{ fontSize: "11px", color: "#8B949E" }} />
        {datasets.map(({ sourceSlug, sourceName }) => {
          const color = SOURCE_COLORS[sourceSlug] || "#8B949E";
          return (
            <Area
              key={sourceSlug}
              type="monotone"
              dataKey={sourceSlug}
              name={sourceName}
              stroke={color}
              strokeWidth={2}
              fill={`url(#mg-${sourceSlug})`}
              connectNulls
              dot={false}
            />
          );
        })}
      </AreaChart>
    </ResponsiveContainer>
  );
}
