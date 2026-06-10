"""
VANTAGE — Event Clustering Service
Uses sentence-transformers embeddings + cosine similarity to group
articles about the same real-world event across different publishers.
"""
from typing import Optional

import numpy as np
import structlog
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment]
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import Article, Event

log = structlog.get_logger()

# Load model once at import time
_model: Optional[object] = None
_fallback_notice_logged = False


def get_embedding_model() -> Optional[object]:
    global _model
    if _model is None:
        if SentenceTransformer is None:
            return None
        log.info("loading_embedding_model", model=settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _fallback_embedding(text: str, dims: int = 64) -> list[float]:
    """Deterministic lightweight embedding used when ML extras are unavailable."""
    vec = np.zeros(dims, dtype=np.float32)
    payload = text.lower().encode("utf-8", errors="ignore")
    for i, b in enumerate(payload):
        vec[(b + i) % dims] += float((b % 29) + 1)
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def embed_text(text: str) -> list[float]:
    """Embed a single text string into a vector."""
    model = get_embedding_model()
    if model is None:
        global _fallback_notice_logged
        if not _fallback_notice_logged:
            log.warning("embedding_model_missing_using_fallback")
            _fallback_notice_logged = True
        return _fallback_embedding(text)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    if not vec_a or not vec_b:
        return 0.0
    if len(vec_a) != len(vec_b):
        n = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:n]
        vec_b = vec_b[:n]
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


async def embed_article(article_id: str, db: AsyncSession) -> list[float] | None:
    """Compute and store embedding for an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        return None

    text = f"{article.title}. {article.content[:500]}"
    embedding = embed_text(text)
    article.embedding = embedding
    await db.flush()
    return embedding


async def cluster_article(article_id: str, db: AsyncSession) -> str | None:
    """
    Find or create an Event cluster for an article.
    Returns the event_id assigned.
    """
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article or not article.embedding:
        return None

    article_vec = article.embedding

    # Get recent unclustered + clustered articles (last 7 days) for comparison
    # We look at existing event centroids first for efficiency
    events_result = await db.execute(
        select(Event).where(Event.centroid_embedding.isnot(None))
    )
    events = events_result.scalars().all()

    best_event = None
    best_similarity = 0.0

    for event in events:
        if not event.centroid_embedding:
            continue
        sim = compute_similarity(article_vec, event.centroid_embedding)
        if sim > best_similarity:
            best_similarity = sim
            best_event = event

    if best_event and best_similarity >= settings.similarity_threshold:
        # Assign to existing event
        article.event_id = best_event.id
        article.is_clustered = True

        # Update centroid (running average)
        current_count = best_event.article_count
        current_centroid = np.array(best_event.centroid_embedding)
        new_centroid = (current_centroid * current_count + np.array(article_vec)) / (current_count + 1)
        best_event.centroid_embedding = new_centroid.tolist()
        best_event.article_count += 1

        log.info(
            "article_clustered_existing_event",
            article_id=article_id,
            event_id=str(best_event.id),
            similarity=round(best_similarity, 3),
        )
        await db.flush()
        return str(best_event.id)
    else:
        # Create new event
        # Use LLM output summary if available, else fall back to title
        event_title = article.title
        event_summary = None
        if article.llm_output:
            event_summary = article.llm_output.event_summary
            if article.llm_output.event_summary:
                event_title = article.llm_output.event_summary[:200]

        new_event = Event(
            title=event_title,
            summary=event_summary,
            centroid_embedding=article_vec,
            article_count=1,
        )
        db.add(new_event)
        await db.flush()

        article.event_id = new_event.id
        article.is_clustered = True
        await db.flush()

        log.info("new_event_created", event_id=str(new_event.id), title=event_title[:60])
        return str(new_event.id)


async def update_event_bias_divergence(event_id: str, db: AsyncSession) -> float:
    """
    Calculate bias divergence across sources covering the same event.
    High divergence = sources disagree on framing.
    """
    result = await db.execute(
        select(Article).where(Article.event_id == event_id, Article.bias_score.isnot(None))
    )
    articles = result.scalars().all()

    if len(articles) < 2:
        return 0.0

    scores = [a.bias_score for a in articles]
    divergence = float(np.std(scores))  # std deviation as divergence proxy

    await db.execute(
        update(Event)
        .where(Event.id == event_id)
        .values(bias_divergence_score=divergence)
    )
    return divergence


async def process_new_article(article_id: str, db: AsyncSession) -> dict:
    """Full pipeline: embed → cluster → return result."""
    embedding = await embed_article(article_id, db)
    if not embedding:
        return {"success": False, "reason": "embedding_failed"}

    event_id = await cluster_article(article_id, db)
    if event_id:
        await update_event_bias_divergence(event_id, db)

    return {
        "success": True,
        "article_id": article_id,
        "event_id": event_id,
        "embedded": True,
    }
