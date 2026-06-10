"""
VANTAGE — API Routes
All REST endpoints: articles, events, analytics, playground, LLM control.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import Article, Event, Entity, ArticleEntity, MediaSource, LLMOutput
from app.schemas.schemas import (
    ArticleOut, ArticleWithAnalysis, EventOut, EventArticleSummary,
    MediaSourceOut, PlaygroundRequest, PlaygroundResponse,
    LLMAnalysisResult, LLMProviderStatus, SetLLMProviderRequest,
    DashboardStats, MediaBiasTrend, EntitySentimentTrend,
    BiasTimeSeriesPoint, EntitySentiment,
)
from app.services.llm.analyzer import analyze_article
from app.services.llm.provider import llm_router
from app.services.clustering.clusterer import process_new_article

router = APIRouter()


# ─────────────────────────────────────────────────────────
#  DASHBOARD STATS
# ─────────────────────────────────────────────────────────
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_articles = await db.scalar(select(func.count(Article.id)))
    total_events = await db.scalar(select(func.count(Event.id)))
    total_entities = await db.scalar(select(func.count(Entity.id)))
    avg_bias = await db.scalar(
        select(func.avg(Article.bias_score)).where(Article.bias_score.isnot(None))
    )

    # Most biased source
    biased_source_result = await db.execute(
        select(MediaSource.name)
        .order_by(desc(MediaSource.avg_bias_score))
        .limit(1)
    )
    most_biased = biased_source_result.scalar_one_or_none()

    # Most covered entity
    entity_result = await db.execute(
        select(Entity.name, func.count(ArticleEntity.id).label("mention_count"))
        .join(ArticleEntity)
        .group_by(Entity.id, Entity.name)
        .order_by(desc("mention_count"))
        .limit(1)
    )
    row = entity_result.first()
    most_covered = row[0] if row else None

    return DashboardStats(
        total_articles=total_articles or 0,
        total_events=total_events or 0,
        total_entities=total_entities or 0,
        avg_bias_score=round(float(avg_bias or 0.0), 3),
        most_biased_source=most_biased,
        most_covered_entity=most_covered,
    )


# ─────────────────────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────────────────────
@router.get("/events", response_model=list[EventOut])
async def list_events(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.articles).selectinload(Article.source),
            selectinload(Event.articles).selectinload(Article.entities).selectinload(ArticleEntity.entity),
            selectinload(Event.articles).selectinload(Article.llm_output),
        )
        .order_by(desc(Event.first_seen_at))
        .offset(skip)
        .limit(limit)
    )
    events = result.scalars().all()

    output = []
    for event in events:
        articles_out = []
        for article in event.articles:
            entities = [
                EntitySentiment(
                    name=ae.entity.name,
                    type=ae.entity.entity_type or "PERSON",
                    sentiment=ae.sentiment or "neutral",
                    sentiment_score=ae.sentiment_score or 0.0,
                    framing=ae.framing or "neutral",
                    context_snippet=ae.context_snippet or "",
                )
                for ae in article.entities if ae.entity
            ]
            articles_out.append(EventArticleSummary(
                id=str(article.id),
                title=article.title,
                url=article.url,
                source_name=article.source.name,
                source_slug=article.source.slug,
                bias_score=article.bias_score,
                published_at=article.published_at,
                framing_analysis=article.llm_output.framing_analysis if article.llm_output else None,
                entity_sentiments=entities,
            ))

        output.append(EventOut(
            id=str(event.id),
            title=event.title,
            summary=event.summary,
            first_seen_at=event.first_seen_at,
            article_count=event.article_count,
            bias_divergence_score=event.bias_divergence_score or 0.0,
            articles=articles_out,
        ))
    return output


@router.get("/events/{event_id}", response_model=EventOut)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.articles).selectinload(Article.source),
            selectinload(Event.articles).selectinload(Article.entities).selectinload(ArticleEntity.entity),
            selectinload(Event.articles).selectinload(Article.llm_output),
        )
        .where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    articles_out = []
    for article in event.articles:
        entities = [
            EntitySentiment(
                name=ae.entity.name,
                type=ae.entity.entity_type or "PERSON",
                sentiment=ae.sentiment or "neutral",
                sentiment_score=ae.sentiment_score or 0.0,
                framing=ae.framing or "neutral",
                context_snippet=ae.context_snippet or "",
            )
            for ae in article.entities if ae.entity
        ]
        articles_out.append(EventArticleSummary(
            id=str(article.id),
            title=article.title,
            url=article.url,
            source_name=article.source.name,
            source_slug=article.source.slug,
            bias_score=article.bias_score,
            published_at=article.published_at,
            framing_analysis=article.llm_output.framing_analysis if article.llm_output else None,
            entity_sentiments=entities,
        ))

    return EventOut(
        id=str(event.id),
        title=event.title,
        summary=event.summary,
        first_seen_at=event.first_seen_at,
        article_count=event.article_count,
        bias_divergence_score=event.bias_divergence_score or 0.0,
        articles=articles_out,
    )


# ─────────────────────────────────────────────────────────
#  ARTICLES
# ─────────────────────────────────────────────────────────
@router.get("/articles", response_model=list[ArticleOut])
async def list_articles(
    source_slug: str | None = None,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    q = select(Article).options(selectinload(Article.source)).order_by(desc(Article.scraped_at))
    if source_slug:
        q = q.join(MediaSource).where(MediaSource.slug == source_slug)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/articles/{article_id}", response_model=ArticleWithAnalysis)
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.source),
            selectinload(Article.llm_output),
            selectinload(Article.entities).selectinload(ArticleEntity.entity),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    llm_analysis = None
    if article.llm_output:
        llm_analysis = LLMAnalysisResult(**article.llm_output.raw_output)

    entities = [
        EntitySentiment(
            name=ae.entity.name,
            type=ae.entity.entity_type or "PERSON",
            sentiment=ae.sentiment or "neutral",
            sentiment_score=ae.sentiment_score or 0.0,
            framing=ae.framing or "neutral",
            context_snippet=ae.context_snippet or "",
        )
        for ae in article.entities if ae.entity
    ]

    return ArticleWithAnalysis(
        id=str(article.id),
        url=article.url,
        title=article.title,
        content=article.content,
        author=article.author,
        published_at=article.published_at,
        bias_score=article.bias_score,
        source=article.source,
        is_analyzed=article.is_analyzed,
        llm_analysis=llm_analysis,
        entities=entities,
    )


@router.post("/articles/{article_id}/analyze")
async def trigger_analysis(
    article_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger LLM analysis + clustering for an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    analysis = await analyze_article(article_id, db)
    if analysis:
        await process_new_article(article_id, db)

    return {"success": True, "article_id": article_id, "analyzed": analysis is not None}


# ─────────────────────────────────────────────────────────
#  MEDIA SOURCES
# ─────────────────────────────────────────────────────────
@router.get("/sources", response_model=list[MediaSourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaSource).where(MediaSource.is_active == True))
    return result.scalars().all()


@router.get("/sources/{slug}/bias-trend", response_model=MediaBiasTrend)
async def get_source_bias_trend(slug: str, days: int = 30, db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta
    from sqlalchemy import cast, Date
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(MediaSource).where(MediaSource.slug == slug)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    trend_result = await db.execute(
        select(
            cast(Article.published_at, Date).label("date"),
            func.avg(Article.bias_score).label("avg_bias"),
            func.count(Article.id).label("count"),
        )
        .where(
            Article.source_id == source.id,
            Article.published_at >= cutoff,
            Article.bias_score.isnot(None),
        )
        .group_by("date")
        .order_by("date")
    )

    trend = [
        BiasTimeSeriesPoint(
            date=str(row.date),
            bias_score=round(float(row.avg_bias), 3),
            article_count=row.count,
        )
        for row in trend_result
    ]

    return MediaBiasTrend(source_name=source.name, source_slug=slug, trend=trend)


# ─────────────────────────────────────────────────────────
#  ANALYTICS — Entity Sentiment
# ─────────────────────────────────────────────────────────
@router.get("/analytics/entities", response_model=list[dict])
async def get_entity_sentiment_overview(
    limit: int = 15,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Entity.name,
            Entity.entity_type,
            func.avg(ArticleEntity.sentiment_score).label("avg_sentiment"),
            func.count(ArticleEntity.id).label("mention_count"),
        )
        .join(ArticleEntity)
        .group_by(Entity.id, Entity.name, Entity.entity_type)
        .order_by(desc("mention_count"))
        .limit(limit)
    )
    return [
        {
            "name": row.name,
            "type": row.entity_type,
            "avg_sentiment": round(float(row.avg_sentiment or 0), 3),
            "mention_count": row.mention_count,
        }
        for row in result
    ]


@router.get("/analytics/bias-distribution")
async def get_bias_distribution(db: AsyncSession = Depends(get_db)):
    """Histogram buckets for bias score distribution."""
    result = await db.execute(
        select(Article.bias_score).where(Article.bias_score.isnot(None))
    )
    scores = [row[0] for row in result]

    buckets = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
    for s in scores:
        if s < 0.2:
            buckets["0.0-0.2"] += 1
        elif s < 0.4:
            buckets["0.2-0.4"] += 1
        elif s < 0.6:
            buckets["0.4-0.6"] += 1
        elif s < 0.8:
            buckets["0.6-0.8"] += 1
        else:
            buckets["0.8-1.0"] += 1

    return [{"range": k, "count": v} for k, v in buckets.items()]


# ─────────────────────────────────────────────────────────
#  PLAYGROUND
# ─────────────────────────────────────────────────────────
@router.post("/playground/analyze", response_model=PlaygroundResponse)
async def playground_analyze(request: PlaygroundRequest):
    """
    Live analysis endpoint — paste any text, get LLM analysis instantly.
    No DB writes, pure LLM reasoning.
    """
    status = await llm_router.get_status()

    if request.provider:
        if request.provider == "openai" and not status["openai_configured"]:
            raise HTTPException(status_code=400, detail="OpenAI is not configured. Set OPENAI_API_KEY in .env or switch to Ollama.")
        if request.provider == "ollama" and not status["ollama_available"]:
            raise HTTPException(status_code=400, detail="Ollama is not available. Start Ollama locally or switch to OpenAI.")

    chosen_provider = request.provider or llm_router.get_active_provider_name()
    if request.provider is None:
        if chosen_provider == "openai" and not status["openai_configured"] and status["ollama_available"]:
            chosen_provider = "ollama"
        elif chosen_provider == "ollama" and not status["ollama_available"] and status["openai_configured"]:
            chosen_provider = "openai"

    if chosen_provider == "openai" and not status["openai_configured"]:
        raise HTTPException(status_code=503, detail="No usable LLM provider: OpenAI is not configured and Ollama fallback is unavailable.")
    if chosen_provider == "ollama" and not status["ollama_available"]:
        raise HTTPException(status_code=503, detail="No usable LLM provider: Ollama is unavailable and OpenAI fallback is not configured.")

    original = llm_router.get_active_provider_name()
    if chosen_provider != original:
        llm_router.set_provider(chosen_provider)
    try:
        analysis = await llm_router.analyze_article(request.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM analysis failed via {chosen_provider}: {str(e)}")
    finally:
        if chosen_provider != original:
            llm_router.set_provider(original)

    return PlaygroundResponse(analysis=analysis)


# ─────────────────────────────────────────────────────────
#  LLM PROVIDER CONTROL
# ─────────────────────────────────────────────────────────
@router.get("/llm/status", response_model=LLMProviderStatus)
async def get_llm_status():
    status = await llm_router.get_status()
    return LLMProviderStatus(**status)


@router.post("/llm/provider")
async def set_llm_provider(request: SetLLMProviderRequest):
    """Hot-switch LLM provider without restarting the server."""
    try:
        llm_router.set_provider(request.provider)
        return {"success": True, "provider": request.provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
