"""Smart retry with exponential backoff.
Adapted from calgary-grocery-scraper middlewares/smart_retry.py.
"""
import time
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware

logger = logging.getLogger(__name__)


class SmartRetryMiddleware(RetryMiddleware):
    """Exponential backoff on retries — avoids triggering rate limits."""

    def _retry(self, request, reason, spider):
        retries = request.meta.get("retry_times", 0)
        delay = min(2 ** retries * 3, 60)  # 3s, 6s, 12s, 24s, 48s, max 60s
        logger.info(f"Retry {retries + 1} for {request.url} — waiting {delay}s")
        time.sleep(delay)
        return super()._retry(request, reason, spider)
