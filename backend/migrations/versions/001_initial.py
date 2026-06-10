"""Initial schema — all VANTAGE tables

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # media_sources
    op.create_table(
        "media_sources",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("base_url", sa.String(255), nullable=False),
        sa.Column("rss_feed_url", sa.String(255)),
        sa.Column("logo_url", sa.String(255)),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("avg_bias_score", sa.Float(), default=0.0),
        sa.Column("total_articles", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # events
    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("article_count", sa.Integer(), default=0),
        sa.Column("centroid_embedding", sa.JSON()),
        sa.Column("bias_divergence_score", sa.Float(), default=0.0),
    )

    # articles
    op.create_table(
        "articles",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author", sa.String(200)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("source_id", UUID(as_uuid=False), sa.ForeignKey("media_sources.id"), nullable=False),
        sa.Column("event_id", UUID(as_uuid=False), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("embedding", sa.JSON()),
        sa.Column("is_analyzed", sa.Boolean(), default=False),
        sa.Column("is_clustered", sa.Boolean(), default=False),
        sa.Column("bias_score", sa.Float()),
        sa.UniqueConstraint("url", name="uq_article_url"),
    )
    op.create_index("ix_article_published_at", "articles", ["published_at"])
    op.create_index("ix_article_source_id", "articles", ["source_id"])
    op.create_index("ix_article_event_id", "articles", ["event_id"])

    # entities
    op.create_table(
        "entities",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("aliases", sa.JSON(), default=list),
        sa.Column("is_political", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # article_entities
    op.create_table(
        "article_entities",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("article_id", UUID(as_uuid=False), sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=False), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("sentiment_score", sa.Float()),
        sa.Column("framing", sa.String(50)),
        sa.Column("context_snippet", sa.Text()),
        sa.UniqueConstraint("article_id", "entity_id", name="uq_article_entity"),
    )
    op.create_index("ix_article_entity_entity_id", "article_entities", ["entity_id"])

    # llm_outputs
    op.create_table(
        "llm_outputs",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("article_id", UUID(as_uuid=False), sa.ForeignKey("articles.id"), nullable=False, unique=True),
        sa.Column("provider", sa.String(30)),
        sa.Column("model_name", sa.String(80)),
        sa.Column("raw_output", sa.JSON(), nullable=False),
        sa.Column("framing_analysis", sa.Text()),
        sa.Column("event_summary", sa.Text()),
        sa.Column("bias_reasoning", sa.Text()),
        sa.Column("tokens_used", sa.Integer()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("llm_outputs")
    op.drop_table("article_entities")
    op.drop_table("entities")
    op.drop_table("articles")
    op.drop_table("events")
    op.drop_table("media_sources")
