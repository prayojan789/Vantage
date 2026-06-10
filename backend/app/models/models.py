"""
VANTAGE — Database Models
Complete schema: articles, events, entities, sentiment, sources, llm_outputs.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────
#  MediaSource — e.g. "Kathmandu Post", "Republica"
# ─────────────────────────────────────────────────────────
class MediaSource(Base):
    __tablename__ = "media_sources"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False, unique=True)
    slug = Column(String(80), nullable=False, unique=True)
    base_url = Column(String(255), nullable=False)
    rss_feed_url = Column(String(255))
    logo_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Aggregated stats (refreshed by background job)
    avg_bias_score = Column(Float, default=0.0)
    total_articles = Column(Integer, default=0)

    articles = relationship("Article", back_populates="source")

    def __repr__(self):
        return f"<MediaSource {self.name}>"


# ─────────────────────────────────────────────────────────
#  Event — A real-world news event (cluster of articles)
# ─────────────────────────────────────────────────────────
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    article_count = Column(Integer, default=0)

    # Embedding centroid stored as JSON array
    centroid_embedding = Column(JSON)

    # Bias divergence across sources (0 = all agree, 1 = wildly different)
    bias_divergence_score = Column(Float, default=0.0)

    articles = relationship("Article", back_populates="event")

    def __repr__(self):
        return f"<Event {self.title[:50]}>"


# ─────────────────────────────────────────────────────────
#  Article — Individual news article
# ─────────────────────────────────────────────────────────
class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("url", name="uq_article_url"),
        Index("ix_article_published_at", "published_at"),
        Index("ix_article_source_id", "source_id"),
        Index("ix_article_event_id", "event_id"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    url = Column(String(1000), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(200))
    published_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK
    source_id = Column(UUID(as_uuid=False), ForeignKey("media_sources.id"), nullable=False)
    event_id = Column(UUID(as_uuid=False), ForeignKey("events.id"), nullable=True)

    # Embedding (stored as JSON for portability)
    embedding = Column(JSON)

    # Processing state
    is_analyzed = Column(Boolean, default=False)
    is_clustered = Column(Boolean, default=False)

    # Overall bias score (0=neutral, 1=heavily biased)
    bias_score = Column(Float)

    source = relationship("MediaSource", back_populates="articles")
    event = relationship("Event", back_populates="articles")
    entities = relationship("ArticleEntity", back_populates="article", cascade="all, delete-orphan")
    llm_output = relationship("LLMOutput", back_populates="article", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article {self.title[:50]}>"


# ─────────────────────────────────────────────────────────
#  Entity — A political actor extracted from an article
# ─────────────────────────────────────────────────────────
class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(200), nullable=False, unique=True)
    entity_type = Column(String(50))  # PERSON | ORG | PARTY | LOCATION
    aliases = Column(JSON, default=list)  # ["KP Oli", "K.P. Sharma Oli"]
    is_political = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    article_mentions = relationship("ArticleEntity", back_populates="entity")

    def __repr__(self):
        return f"<Entity {self.name} ({self.entity_type})>"


# ─────────────────────────────────────────────────────────
#  ArticleEntity — Junction: article ↔ entity + sentiment
# ─────────────────────────────────────────────────────────
class ArticleEntity(Base):
    __tablename__ = "article_entities"
    __table_args__ = (
        UniqueConstraint("article_id", "entity_id", name="uq_article_entity"),
        Index("ix_article_entity_entity_id", "entity_id"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    article_id = Column(UUID(as_uuid=False), ForeignKey("articles.id"), nullable=False)
    entity_id = Column(UUID(as_uuid=False), ForeignKey("entities.id"), nullable=False)

    # Aspect-Based Sentiment
    sentiment = Column(String(20))         # positive | negative | neutral
    sentiment_score = Column(Float)        # -1.0 to 1.0
    framing = Column(String(50))           # critical | supportive | neutral | mixed

    # Context snippet from the article mentioning this entity
    context_snippet = Column(Text)

    article = relationship("Article", back_populates="entities")
    entity = relationship("Entity", back_populates="article_mentions")


# ─────────────────────────────────────────────────────────
#  LLMOutput — Raw structured JSON from LLM analysis
# ─────────────────────────────────────────────────────────
class LLMOutput(Base):
    __tablename__ = "llm_outputs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    article_id = Column(UUID(as_uuid=False), ForeignKey("articles.id"), nullable=False, unique=True)

    # Which LLM produced this
    provider = Column(String(30))   # openai | ollama
    model_name = Column(String(80))

    # The full structured JSON returned by LLM
    raw_output = Column(JSON, nullable=False)

    # Parsed fields for quick access
    framing_analysis = Column(Text)
    event_summary = Column(Text)
    bias_reasoning = Column(Text)

    tokens_used = Column(Integer)
    latency_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="llm_output")
