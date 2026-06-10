"""
VANTAGE — Celery Background Tasks
Scheduled jobs: scrape → embed → analyze → cluster → update stats.
Run worker:  celery -A app.tasks.celery_app worker --loglevel=info
Run beat:    celery -A app.tasks.celery_app beat --loglevel=info
"""
import asyncio
from celery import Celery
from celery.schedules import crontab
import structlog

from app.core.config import settings

log = structlog.get_logger()

# ── App setup ────────────────────────────────────────────
celery_app = Celery(
    "vantage",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kathmandu",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# ── Periodic schedule ─────────────────────────────────────
celery_app.conf.beat_schedule = {
    # Analyze unprocessed articles every 5 minutes
    "analyze-unprocessed-articles": {
        "task": "app.tasks.analyze_pending_articles",
        "schedule": 300,  # every 5 minutes
    },
    # Cluster unembedded articles every 10 minutes
    "cluster-new-articles": {
        "task": "app.tasks.cluster_pending_articles",
        "schedule": 600,
    },
    # Refresh media source aggregate stats every hour
    "refresh-source-stats": {
        "task": "app.tasks.refresh_source_stats",
        "schedule": 3600,
    },
}


def run_async(coro):
    """Helper: run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Tasks ─────────────────────────────────────────────────

@celery_app.task(name="app.tasks.analyze_pending_articles", bind=True, max_retries=2)
def analyze_pending_articles(self):
    """
    Pick up all unanalyzed articles and run LLM analysis on them.
    Runs every 5 minutes via beat scheduler.
    """
    async def _run():
        from app.db.database import AsyncSessionLocal
        from app.services.llm.analyzer import bulk_analyze_unprocessed

        async with AsyncSessionLocal() as db:
            count = await bulk_analyze_unprocessed(db, limit=10)
            await db.commit()
            log.info("analyze_task_complete", articles_processed=count)
            return count

    try:
        return run_async(_run())
    except Exception as exc:
        log.error("analyze_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.tasks.cluster_pending_articles", bind=True, max_retries=2)
def cluster_pending_articles(self):
    """
    Embed and cluster articles that haven't been grouped into events yet.
    Runs every 10 minutes.
    """
    async def _run():
        from sqlalchemy import select
        from app.db.database import AsyncSessionLocal
        from app.models.models import Article
        from app.services.clustering.clusterer import process_new_article

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Article)
                .where(Article.is_clustered == False, Article.is_analyzed == True)
                .limit(20)
            )
            articles = result.scalars().all()
            count = 0
            for article in articles:
                await process_new_article(str(article.id), db)
                count += 1
            await db.commit()
            log.info("cluster_task_complete", articles_clustered=count)
            return count

    try:
        return run_async(_run())
    except Exception as exc:
        log.error("cluster_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=90)


@celery_app.task(name="app.tasks.refresh_source_stats")
def refresh_source_stats():
    """
    Recompute avg_bias_score and total_articles for each media source.
    Runs every hour.
    """
    async def _run():
        from sqlalchemy import select, func, update
        from app.db.database import AsyncSessionLocal
        from app.models.models import MediaSource, Article

        async with AsyncSessionLocal() as db:
            sources_result = await db.execute(select(MediaSource))
            sources = sources_result.scalars().all()

            for source in sources:
                avg_result = await db.execute(
                    select(func.avg(Article.bias_score), func.count(Article.id))
                    .where(
                        Article.source_id == source.id,
                        Article.bias_score.isnot(None),
                    )
                )
                row = avg_result.first()
                avg_bias = float(row[0] or 0.0)
                total = row[1] or 0

                await db.execute(
                    update(MediaSource)
                    .where(MediaSource.id == source.id)
                    .values(avg_bias_score=round(avg_bias, 4), total_articles=total)
                )

            await db.commit()
            log.info("source_stats_refreshed", source_count=len(sources))

    run_async(_run())


@celery_app.task(name="app.tasks.analyze_single_article")
def analyze_single_article(article_id: str):
    """Triggered immediately after scraping a new article."""
    async def _run():
        from app.db.database import AsyncSessionLocal
        from app.services.llm.analyzer import analyze_article
        from app.services.clustering.clusterer import process_new_article

        async with AsyncSessionLocal() as db:
            result = await analyze_article(article_id, db)
            if result:
                await process_new_article(article_id, db)
            await db.commit()
            return result is not None

    return run_async(_run())
