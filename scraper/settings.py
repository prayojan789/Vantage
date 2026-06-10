# VANTAGE — Scrapy Settings
BOT_NAME = "vantage_scraper"
SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 2

ITEM_PIPELINES = {
    "scraper.pipelines.db_pipeline.DuplicateFilterPipeline": 100,
    "scraper.pipelines.db_pipeline.PostgreSQLPipeline": 200,
}

LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
