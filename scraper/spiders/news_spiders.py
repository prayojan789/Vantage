"""
VANTAGE — Scrapy Spiders
Scrapers for major English-language Nepali news portals.
Run: scrapy crawl kathmandu_post
"""
import scrapy
from scrapy.http import Response
import feedparser
from datetime import datetime


class KathmanduPostSpider(scrapy.Spider):
    name = "kathmandu_post"
    source_slug = "kathmandu-post"
    rss_url = "https://kathmandupost.com/rss"
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "VANTAGE Research Bot/1.0 (academic research)",
    }

    def start_requests(self):
        yield scrapy.Request(self.rss_url, callback=self.parse_rss)

    def parse_rss(self, response: Response):
        feed = feedparser.parse(response.text)
        for entry in feed.entries[:self.settings.getint("MAX_ARTICLES_PER_CRAWL", 50)]:
            yield scrapy.Request(
                url=entry.link,
                callback=self.parse_article,
                meta={
                    "title": entry.get("title", ""),
                    "published": entry.get("published", ""),
                    "source_slug": self.source_slug,
                },
            )

    def parse_article(self, response: Response):
        # Extract article content
        paragraphs = response.css("article p::text, .article-body p::text").getall()
        content = " ".join(p.strip() for p in paragraphs if len(p.strip()) > 30)

        if len(content) < 100:
            return  # Skip empty/failed pages

        yield {
            "url": response.url,
            "title": response.meta.get("title") or response.css("h1::text").get("").strip(),
            "content": content,
            "author": response.css(".author-name::text, .byline::text").get("").strip(),
            "published_at": response.meta.get("published"),
            "source_slug": self.source_slug,
        }


class RepublicaSpider(scrapy.Spider):
    name = "republica"
    source_slug = "republica"
    rss_url = "https://myrepublica.nagariknetwork.com/rss"
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "VANTAGE Research Bot/1.0 (academic research)",
    }

    def start_requests(self):
        yield scrapy.Request(self.rss_url, callback=self.parse_rss)

    def parse_rss(self, response: Response):
        feed = feedparser.parse(response.text)
        for entry in feed.entries[:50]:
            yield scrapy.Request(
                url=entry.link,
                callback=self.parse_article,
                meta={"title": entry.get("title", ""), "published": entry.get("published", "")},
            )

    def parse_article(self, response: Response):
        paragraphs = response.css(".news-description p::text, .article-content p::text").getall()
        content = " ".join(p.strip() for p in paragraphs if len(p.strip()) > 30)
        if len(content) < 100:
            return
        yield {
            "url": response.url,
            "title": response.meta.get("title") or response.css("h1::text").get("").strip(),
            "content": content,
            "author": response.css(".author::text").get("").strip(),
            "published_at": response.meta.get("published"),
            "source_slug": self.source_slug,
        }


class OnlineKhabarSpider(scrapy.Spider):
    name = "online_khabar"
    source_slug = "online-khabar"
    rss_url = "https://english.onlinekhabar.com/feed"
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "VANTAGE Research Bot/1.0 (academic research)",
    }

    def start_requests(self):
        yield scrapy.Request(self.rss_url, callback=self.parse_rss)

    def parse_rss(self, response: Response):
        feed = feedparser.parse(response.text)
        for entry in feed.entries[:50]:
            yield scrapy.Request(
                url=entry.link,
                callback=self.parse_article,
                meta={"title": entry.get("title", ""), "published": entry.get("published", "")},
            )

    def parse_article(self, response: Response):
        paragraphs = response.css(".ok-news-post-content p::text, .entry-content p::text").getall()
        content = " ".join(p.strip() for p in paragraphs if len(p.strip()) > 30)
        if len(content) < 100:
            return
        yield {
            "url": response.url,
            "title": response.meta.get("title") or response.css("h1::text").get("").strip(),
            "content": content,
            "author": response.css(".author-name::text").get("").strip(),
            "published_at": response.meta.get("published"),
            "source_slug": self.source_slug,
        }
