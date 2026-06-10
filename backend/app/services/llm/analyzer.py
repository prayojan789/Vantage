"""
VANTAGE — Article Analysis Service
Orchestrates LLM analysis and persists results to DB.
"""
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Article, Entity, ArticleEntity, LLMOutput
from app.schemas.schemas import LLMAnalysisResult
from app.services.llm.provider import llm_router

log = structlog.get_logger()


async def analyze_article(article_id: str, db: AsyncSession) -> LLMAnalysisResult | None:
    """
    Run LLM analysis on an article and persist all results.
    Returns the structured analysis or None on failure.
    """
    # Load article
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        log.error("article_not_found", article_id=article_id)
        return None

    # Skip if already analyzed
    if article.is_analyzed:
        log.info("article_already_analyzed", article_id=article_id)
        existing = await db.execute(
            select(LLMOutput).where(LLMOutput.article_id == article_id)
        )
        llm_out = existing.scalar_one_or_none()
        if llm_out:
            return LLMAnalysisResult(**llm_out.raw_output)
        return None

    # Run LLM
    log.info("running_llm_analysis", article_id=article_id, title=article.title[:60])
    try:
        analysis = await llm_router.analyze_article(
            f"TITLE: {article.title}\n\n{article.content}"
        )
    except Exception as e:
        log.error("llm_analysis_failed", article_id=article_id, error=str(e))
        return None

    # Persist bias score on article
    article.bias_score = analysis.bias_score
    article.is_analyzed = True

    # Persist LLM output
    llm_output = LLMOutput(
        article_id=article.id,
        provider=analysis.provider,
        model_name=analysis.model_name,
        raw_output=analysis.model_dump(),
        framing_analysis=analysis.framing_analysis,
        event_summary=analysis.event_summary,
        bias_reasoning=analysis.bias_reasoning,
        latency_ms=analysis.latency_ms,
    )
    db.add(llm_output)

    # Persist entities and sentiment
    for ent_data in analysis.entities:
        # Get or create entity
        ent_result = await db.execute(
            select(Entity).where(Entity.name == ent_data.name)
        )
        entity = ent_result.scalar_one_or_none()
        if not entity:
            entity = Entity(
                name=ent_data.name,
                entity_type=ent_data.type,
                is_political=True,
            )
            db.add(entity)
            await db.flush()

        # Create article-entity link with sentiment
        article_entity = ArticleEntity(
            article_id=article.id,
            entity_id=entity.id,
            sentiment=ent_data.sentiment,
            sentiment_score=ent_data.sentiment_score,
            framing=ent_data.framing,
            context_snippet=ent_data.context_snippet,
        )
        db.add(article_entity)

    await db.flush()
    log.info("analysis_complete", article_id=article_id, bias_score=analysis.bias_score)
    return analysis


async def bulk_analyze_unprocessed(db: AsyncSession, limit: int = 20) -> int:
    """Analyze all unprocessed articles. Called by Celery beat."""
    result = await db.execute(
        select(Article)
        .where(Article.is_analyzed == False)
        .limit(limit)
    )
    articles = result.scalars().all()
    count = 0
    for article in articles:
        result = await analyze_article(str(article.id), db)
        if result:
            count += 1
    return count
