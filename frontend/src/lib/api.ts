// VANTAGE — API Client

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `API error ${res.status}`);
  }
  return res.json();
}

// Fetcher for SWR
export const fetcher = (path: string) => apiFetch(path);

// Typed API calls
export const api = {
  getDashboardStats: () => apiFetch("/dashboard/stats"),

  getEvents: (skip = 0, limit = 20) =>
    apiFetch(`/events?skip=${skip}&limit=${limit}`),

  getEvent: (id: string) => apiFetch(`/events/${id}`),

  getArticles: (sourceSlug?: string, skip = 0, limit = 20) =>
    apiFetch(`/articles?skip=${skip}&limit=${limit}${sourceSlug ? `&source_slug=${sourceSlug}` : ""}`),

  getArticle: (id: string) => apiFetch(`/articles/${id}`),

  analyzeArticle: (id: string) =>
    apiFetch(`/articles/${id}/analyze`, { method: "POST" }),

  getSources: () => apiFetch("/sources"),

  getSourceBiasTrend: (slug: string, days = 30) =>
    apiFetch(`/sources/${slug}/bias-trend?days=${days}`),

  getEntityOverview: (limit = 15) =>
    apiFetch(`/analytics/entities?limit=${limit}`),

  getBiasDistribution: () => apiFetch("/analytics/bias-distribution"),

  playgroundAnalyze: (text: string, provider?: string) =>
    apiFetch("/playground/analyze", {
      method: "POST",
      body: JSON.stringify({ text, provider }),
    }),

  getLLMStatus: () => apiFetch("/llm/status"),

  setLLMProvider: (provider: string) =>
    apiFetch("/llm/provider", {
      method: "POST",
      body: JSON.stringify({ provider }),
    }),
};
