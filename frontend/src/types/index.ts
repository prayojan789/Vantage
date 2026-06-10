// VANTAGE — TypeScript Types

export interface EntitySentiment {
  name: string;
  type: "PERSON" | "ORG" | "PARTY" | "LOCATION";
  sentiment: "positive" | "negative" | "neutral";
  sentiment_score: number; // -1.0 to 1.0
  framing: "critical" | "supportive" | "neutral" | "mixed";
  context_snippet: string;
}

export interface LLMAnalysisResult {
  entities: EntitySentiment[];
  bias_score: number; // 0.0 to 1.0
  framing_analysis: string;
  bias_reasoning: string;
  event_summary: string;
  overall_sentiment: string;
  provider: "openai" | "ollama";
  model_name: string;
  latency_ms: number;
}

export interface MediaSource {
  id: string;
  name: string;
  slug: string;
  base_url: string;
  logo_url?: string;
  avg_bias_score: number;
  total_articles: number;
}

export interface Article {
  id: string;
  url: string;
  title: string;
  content: string;
  author?: string;
  published_at?: string;
  bias_score?: number;
  source: MediaSource;
  is_analyzed: boolean;
  llm_analysis?: LLMAnalysisResult;
  entities?: EntitySentiment[];
}

export interface EventArticle {
  id: string;
  title: string;
  url: string;
  source_name: string;
  source_slug: string;
  bias_score?: number;
  published_at?: string;
  framing_analysis?: string;
  entity_sentiments: EntitySentiment[];
}

export interface NewsEvent {
  id: string;
  title: string;
  summary?: string;
  first_seen_at: string;
  article_count: number;
  bias_divergence_score: number;
  articles: EventArticle[];
}

export interface DashboardStats {
  total_articles: number;
  total_events: number;
  total_entities: number;
  avg_bias_score: number;
  most_biased_source?: string;
  most_covered_entity?: string;
}

export interface BiasTimeSeriesPoint {
  date: string;
  bias_score: number;
  article_count: number;
}

export interface MediaBiasTrend {
  source_name: string;
  source_slug: string;
  trend: BiasTimeSeriesPoint[];
}

export interface EntityOverview {
  name: string;
  type: string;
  avg_sentiment: number;
  mention_count: number;
}

export interface LLMProviderStatus {
  current_provider: "openai" | "ollama";
  available_providers: string[];
  openai_configured: boolean;
  ollama_available: boolean;
  current_model: string;
}

export interface BiasDistributionBucket {
  range: string;
  count: number;
}
