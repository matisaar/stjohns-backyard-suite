"""Anti-detection middleware — UA rotation, realistic headers.
Adapted from calgary-grocery-scraper middlewares/anti_detection.py.
"""
import random


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

ACCEPT_LANGUAGES = [
    "en-CA,en;q=0.9",
    "en-CA,en-US;q=0.9,en;q=0.8",
    "en-CA,fr-CA;q=0.9,en;q=0.8",
    "en,en-CA;q=0.9",
]


class AntiDetectionMiddleware:
    """Rotate UA and set realistic headers for Kent.ca."""

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENTS)
        request.headers["User-Agent"] = ua
        request.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        request.headers["Accept-Language"] = random.choice(ACCEPT_LANGUAGES)
        request.headers["Accept-Encoding"] = "gzip, deflate, br"
        request.headers["Referer"] = "https://www.kent.ca/en/"
        request.headers["Sec-Fetch-Dest"] = "document"
        request.headers["Sec-Fetch-Mode"] = "navigate"
        request.headers["Sec-Fetch-Site"] = "same-origin"
        request.headers["DNT"] = "1"
        return None
