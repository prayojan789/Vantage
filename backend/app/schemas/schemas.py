"""
VANTAGE — Pydantic Schemas
Request/response models for all API endpoints.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl


# ─────────────────────────────────────────────────────────
#  LLM Analysis — the core output schema
# ─────────────────────────────────────────────────────────
class EntitySentiment(BaseModel):
    name: str
    type: str  # PERSON | ORG | PARTY | LOCATION
    sentiment: str  # positive | negative | neutral
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    framing: str  # critical | supportive | neutral | mixed
    context_snippet: str


class LLMAnalysisResult(BaseModel):
    entities: list[EntitySentiment]
    bias_score: float = Field(ge=0.0, le=1.0)
    framing_analysis: str
    bias_reasoning: str
    event_summary: str
    overall_sentiment: str
    provider: str
    model_name: str
    latency_ms: int


# ─────────────────────────────────────────────────────────
#  Playground
# ─────────────────────────────────────────────────────────
class PlaygroundRequest(BaseModel):
    text: str = Field(min_length=50, max_length=10000)
    provider: Optional[str] = None  # override global setting


class PlaygroundResponse(BaseModel):
    analysis: LLMAnalysisResult


# ─────────────────────────────────────────────────────────
#  Media Source
# ─────────────────────────────────────────────────────────
class MediaSourceOut(BaseModel):
    id: str
    name: str
    slug: str
    base_url: str
    logo_url: Optional[str]
    avg_bias_score: float
    total_articles: int

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  Article
# ─────────────────────────────────────────────────────────
class ArticleOut(BaseModel):
    id: str
    url: str
    title: str
    content: str
    author: Optional[str]
    published_at: Optional[datetime]
    bias_score: Optional[float]
    source: MediaSourceOut
    is_analyzed: bool

    model_config = {"from_attributes": True}


class ArticleWithAnalysis(ArticleOut):
    llm_analysis: Optional[LLMAnalysisResult] = None
    entities: list[EntitySentiment] = []


# ─────────────────────────────────────────────────────────
#  Event Cluster
# ─────────────────────────────────────────────────────────
class EventArticleSummary(BaseModel):
    id: str
    title: str
    url: str
    source_name: str
    source_slug: str
    bias_score: Optional[float]
    published_at: Optional[datetime]
    framing_analysis: Optional[str]
    entity_sentiments: list[EntitySentiment] = []

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    first_seen_at: datetime
    article_count: int
    bias_divergence_score: float
    articles: list[EventArticleSummary] = []

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  Analytics
# ─────────────────────────────────────────────────────────
class BiasTimeSeriesPoint(BaseModel):
    date: str
    bias_score: float
    article_count: int


class MediaBiasTrend(BaseModel):
    source_name: str
    source_slug: str
    trend: list[BiasTimeSeriesPoint]


class EntitySentimentTrend(BaseModel):
    entity_name: str
    entity_type: str
    sources: dict[str, list[BiasTimeSeriesPoint]]


class DashboardStats(BaseModel):
    total_articles: int
    total_events: int
    total_entities: int
    avg_bias_score: float
    most_biased_source: Optional[str]
    most_covered_entity: Optional[str]


# ─────────────────────────────────────────────────────────
#  LLM Provider toggle
# ─────────────────────────────────────────────────────────
class LLMProviderStatus(BaseModel):
    current_provider: str
    available_providers: list[str]
    openai_configured: bool
    ollama_available: bool
    current_model: str


class SetLLMProviderRequest(BaseModel):
    provider: str  # "openai" | "ollama"
