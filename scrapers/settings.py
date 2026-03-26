"""Scrapy settings for Kent Building Supplies scraper.
Adapted from matisaar/calgary-grocery-scraper architecture.
"""

BOT_NAME = "stjohns_bom_scraper"

SPIDER_MODULES = ["scrapers.spiders"]
NEWSPIDER_MODULE = "scrapers.spiders"

# Crawl responsibly
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

# Anti-detection
DOWNLOADER_MIDDLEWARES = {
    "scrapers.middlewares.anti_detection.AntiDetectionMiddleware": 543,
    "scrapers.middlewares.smart_retry.SmartRetryMiddleware": 550,
}

ITEM_PIPELINES = {
    "scrapers.pipelines.CleaningPipeline": 100,
    "scrapers.pipelines.DedupPipeline": 200,
    "scrapers.pipelines.SQLitePipeline": 300,
    "scrapers.pipelines.CSVPipeline": 400,
}

# Output
FEEDS = {}
LOG_LEVEL = "INFO"

# Retry
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Request fingerprinting (Scrapy 2.7+)
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
