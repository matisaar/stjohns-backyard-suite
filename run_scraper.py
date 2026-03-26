#!/usr/bin/env python3
"""Main entry point — run Kent.ca building materials scraper.

Usage:
    python run_scraper.py --all                    # Scrape all categories
    python run_scraper.py --category plywood       # Single category
    python run_scraper.py --clear --all            # Clear DB then scrape
    python run_scraper.py --list-categories        # Show available categories
"""
import argparse
import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    parser = argparse.ArgumentParser(description="Kent.ca Building Materials Scraper")
    parser.add_argument("--all", action="store_true", help="Scrape all categories")
    parser.add_argument("--category", type=str, help="Scrape a specific category")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages per category")
    parser.add_argument("--clear", action="store_true", help="Clear database before scraping")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    args = parser.parse_args()

    # Import spider to access its CATEGORIES
    from scrapers.spiders.kent_spider import KentSpider

    if args.list_categories:
        print("Available categories:")
        for cat in KentSpider.CATEGORIES:
            print(f"  - {cat}")
        return

    if args.clear:
        db_path = os.path.join("data", "building_materials.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Cleared {db_path}")

    if not args.all and not args.category:
        parser.print_help()
        sys.exit(1)

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    kwargs = {"max_pages": args.max_pages}
    if args.category:
        kwargs["category"] = args.category

    process.crawl(KentSpider, **kwargs)
    process.start()


if __name__ == "__main__":
    main()
