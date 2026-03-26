"""Pipelines: clean, dedup, store in SQLite, export CSV.
Adapted from calgary-grocery-scraper pipelines.py.
"""
import csv
import os
import re
import sqlite3
from datetime import datetime, timezone


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "building_materials.db")
CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class CleaningPipeline:
    """Normalize prices and text fields."""

    def process_item(self, item, spider):
        # Clean price
        raw = item.get("price", "")
        if isinstance(raw, str):
            raw = re.sub(r"[^\d.]", "", raw)
            item["price"] = float(raw) if raw else 0.0
        elif raw is None:
            item["price"] = 0.0

        # Clean name
        if item.get("name"):
            item["name"] = " ".join(item["name"].split())

        # Ensure scraped_date
        if not item.get("scraped_date"):
            item["scraped_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Default store
        if not item.get("store"):
            item["store"] = "Kent Building Supplies"

        return item


class DedupPipeline:
    """Drop duplicate items by SKU within a single crawl."""

    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        sku = item.get("sku", "")
        if sku and sku in self.seen:
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate SKU: {sku}")
        self.seen.add(sku)
        return item


class SQLitePipeline:
    """Store items in SQLite database."""

    def open_spider(self, spider):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                sku TEXT,
                price REAL,
                unit TEXT,
                category TEXT,
                subcategory TEXT,
                brand TEXT,
                url TEXT,
                in_stock INTEGER,
                store TEXT,
                scraped_date TEXT,
                image_url TEXT,
                rating REAL,
                review_count INTEGER,
                UNIQUE(sku, scraped_date)
            )
        """)
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO materials
                (name, sku, price, unit, category, subcategory, brand, url,
                 in_stock, store, scraped_date, image_url, rating, review_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("name"), item.get("sku"), item.get("price"),
                item.get("unit"), item.get("category"), item.get("subcategory"),
                item.get("brand"), item.get("url"), int(item.get("in_stock", True)),
                item.get("store"), item.get("scraped_date"), item.get("image_url"),
                item.get("rating"), item.get("review_count"),
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"SQLite error: {e}")
        return item


class CSVPipeline:
    """Export items to per-category CSV files."""

    def open_spider(self, spider):
        os.makedirs(CSV_DIR, exist_ok=True)
        self.files = {}
        self.writers = {}

    def close_spider(self, spider):
        for f in self.files.values():
            f.close()

    def process_item(self, item, spider):
        cat = item.get("category", "misc")
        if cat not in self.files:
            path = os.path.join(CSV_DIR, f"{cat}_products.csv")
            f = open(path, "w", newline="", encoding="utf-8")
            writer = csv.DictWriter(f, fieldnames=[
                "name", "sku", "price", "unit", "category", "subcategory",
                "brand", "url", "in_stock", "store", "scraped_date",
            ])
            writer.writeheader()
            self.files[cat] = f
            self.writers[cat] = writer

        self.writers[cat].writerow({
            k: item.get(k, "") for k in [
                "name", "sku", "price", "unit", "category", "subcategory",
                "brand", "url", "in_stock", "store", "scraped_date",
            ]
        })
        return item
