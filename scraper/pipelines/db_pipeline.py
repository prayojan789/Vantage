"""
VANTAGE — Scrapy Pipeline
Saves scraped articles to PostgreSQL and triggers analysis.
"""
import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime

import psycopg2
from scrapy import Spider
from scrapy.exceptions import DropItem

from app.core.config import settings


class DuplicateFilterPipeline:
    """Drop articles already in the database."""
    def __init__(self):
        self.seen_urls = set()
        self.conn = None

    def open_spider(self, spider: Spider):
        self.conn = psycopg2.connect(settings.database_url_sync)
        cursor = self.conn.cursor()
        cursor.execute("SELECT url FROM articles")
        for row in cursor.fetchall():
            self.seen_urls.add(row[0])
        cursor.close()

    def close_spider(self, spider: Spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        if item["url"] in self.seen_urls:
            raise DropItem(f"Duplicate URL: {item['url']}")
        self.seen_urls.add(item["url"])
        return item


class PostgreSQLPipeline:
    """Saves article to DB and queues for LLM analysis."""
    def __init__(self):
        self.conn = None
        self.cursor = None

    def open_spider(self, spider: Spider):
        self.conn = psycopg2.connect(settings.database_url_sync)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider: Spider):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def process_item(self, item, spider):
        # Resolve source_id from slug
        self.cursor.execute(
            "SELECT id FROM media_sources WHERE slug = %s",
            (item["source_slug"],)
        )
        row = self.cursor.fetchone()
        if not row:
            raise DropItem(f"Unknown source slug: {item['source_slug']}")
        source_id = row[0]

        # Parse published_at
        published_at = None
        if item.get("published_at"):
            try:
                published_at = parsedate_to_datetime(item["published_at"])
            except Exception:
                published_at = None

        self.cursor.execute(
            """
            INSERT INTO articles (url, title, content, author, published_at, source_id, is_analyzed, is_clustered)
            VALUES (%s, %s, %s, %s, %s, %s, false, false)
            ON CONFLICT (url) DO NOTHING
            """,
            (
                item["url"],
                item["title"][:500],
                item["content"],
                item.get("author", "")[:200],
                published_at,
                source_id,
            )
        )
        self.conn.commit()
        spider.logger.info(f"Saved: {item['title'][:60]}")
        return item
