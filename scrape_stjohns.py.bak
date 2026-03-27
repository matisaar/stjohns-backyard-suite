#!/usr/bin/env python3
"""Scrape live Kent.ca prices for every BOM item and update the database.

Reads all items from bom_data.py, extracts SKUs from URLs, scrapes current
prices from Kent.ca product pages, stores results in SQLite, and optionally
patches bom_data.py with corrected prices.

Usage:
    python scrape_stjohns.py              # scrape + report diffs
    python scrape_stjohns.py --update     # scrape + auto-patch bom_data.py
"""
import json
import os
import re
import sqlite3
import sys
import time
import urllib.request
from datetime import datetime

# ── project imports ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bom_data import ALL_DIVISIONS

# ── constants ────────────────────────────────────────────────────────────────
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "building_materials.db")
BOM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bom_data.py")
REQUEST_DELAY = 0.4          # seconds between requests — be polite
TIMEOUT = 20                 # per-request timeout
TODAY = datetime.now().strftime("%Y-%m-%d")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def extract_sku_from_url(url: str) -> str:
    """Pull the Kent.ca SKU from a product URL.

    Patterns:
      kent.ca/en/…-1016278
      kent.ca/en/…-1015669-neu
      kent.ca/en/…-1080257-pwt
    """
    if "kent.ca" not in url:
        return ""
    m = re.search(r'-(\d{6,8}(?:-[a-z]+)?)(?:\?|$)', url)
    return m.group(1) if m else ""


def scrape_price(url: str) -> float | None:
    """Fetch a Kent.ca product page and extract the price.

    Tries multiple extraction strategies in order of reliability:
      1. JSON-LD structured data (most reliable)
      2. <meta property="product:price:amount">
      3. data-price-amount attribute
      4. <span class="price">$X.XX</span>
      5. Regex pattern: "price":X.XX anywhere in page source
    """
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(f"HTTP error: {exc}") from exc

    # Strategy 1: JSON-LD
    for blob in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    ):
        try:
            data = json.loads(blob)
            offers = data.get("offers") if isinstance(data, dict) else None
            if isinstance(offers, dict) and "price" in offers:
                return float(offers["price"])
            if isinstance(offers, list):
                for o in offers:
                    if "price" in o:
                        return float(o["price"])
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # Strategy 2: Open Graph meta
    m = re.search(
        r'<meta\s+(?:property|name)="product:price:amount"\s+content="([^"]+)"', html
    )
    if m:
        return float(m.group(1))

    # Strategy 3: data-price-amount (Magento)
    m = re.search(r'data-price-amount="([^"]+)"', html)
    if m:
        return float(m.group(1))

    # Strategy 4: <span class="price">
    m = re.search(r'<span[^>]*class="price"[^>]*>\s*\$\s*([0-9,]+\.[0-9]{2})', html)
    if m:
        return float(m.group(1).replace(",", ""))

    # Strategy 5: raw JSON "price": anywhere
    m = re.search(r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]{1,2}))"?', html)
    if m:
        return float(m.group(1))

    return None


# ── database ─────────────────────────────────────────────────────────────────

def init_db():
    """Create the materials table if it doesn't exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sku         TEXT NOT NULL,
            name        TEXT NOT NULL,
            price       REAL,
            bom_price   REAL,
            url         TEXT,
            division    TEXT,
            scraped_date TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_materials_sku ON materials(sku)
    """)
    conn.commit()
    return conn


def save_result(conn, sku, name, price, bom_price, url, division):
    """Insert one scraped result."""
    conn.execute(
        "INSERT INTO materials (sku, name, price, bom_price, url, division, scraped_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (sku, name, price, bom_price, url, division, TODAY),
    )


# ── BOM auto-patcher ────────────────────────────────────────────────────────

def patch_bom_file(updates: list[tuple[str, float, float]]):
    """Replace unit_price values in bom_data.py for items whose prices changed.

    Each entry in `updates` is (item_name, old_price, new_price).
    """
    with open(BOM_FILE, "r") as f:
        src = f.read()

    patched = 0
    for name, old_price, new_price in updates:
        # Use a regex that finds this item's name nearby the unit_price
        pattern = re.compile(
            r'("name":\s*"[^"]*' + re.escape(name[:30]) + r'[^"]*"'
            r'.*?'
            r'"unit_price":\s*)' + re.escape(str(old_price)),
            re.DOTALL
        )
        new_src = pattern.sub(r'\g<1>' + str(new_price), src, count=1)
        if new_src != src:
            src = new_src
            patched += 1

    if patched > 0:
        with open(BOM_FILE, "w") as f:
            f.write(src)
        print(f"\n✅ Patched {patched} price(s) in bom_data.py")
    else:
        print("\nNo prices needed patching in bom_data.py")


# ── main ─────────────────────────────────────────────────────────────────────

def collect_kent_items():
    """Build list of all Kent.ca-linked items with extractable SKUs."""
    items = []
    seen_urls = set()
    for div in ALL_DIVISIONS:
        for item in div["items"]:
            url = item.get("url", "")
            if "kent.ca" not in url:
                continue
            # Skip search pages
            if "/search?" in url:
                continue
            # Deduplicate by URL (e.g. bathroom faucet reuses shower valve URL)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            sku = item.get("sku") or extract_sku_from_url(url)
            if not sku:
                continue
            items.append({
                "division": div["name"],
                "name": item["name"],
                "bom_price": item["unit_price"],
                "url": url,
                "sku": sku,
            })
    return items


def main():
    auto_update = "--update" in sys.argv

    items = collect_kent_items()
    print(f"Found {len(items)} Kent.ca items to scrape\n")
    print(f"{'SKU':<16} {'Item':<55} {'BOM $':>9} {'Kent $':>9} {'Diff':>8}")
    print("─" * 100)

    conn = init_db()
    results = []
    errors = []
    price_changes = []

    for i, it in enumerate(items, 1):
        sku, name, bom_price, url = it["sku"], it["name"], it["bom_price"], it["url"]
        try:
            kent_price = scrape_price(url)
            if kent_price is None:
                errors.append((sku, name, "price not found on page"))
                print(f"{sku:<16} {name[:55]:<55} ${bom_price:>8.2f}  {'NOT FOUND':>9}")
            else:
                diff = kent_price - bom_price
                flag = "" if abs(diff) < 0.01 else f"{'':>1}{'↑' if diff > 0 else '↓'}"
                print(
                    f"{sku:<16} {name[:55]:<55} ${bom_price:>8.2f} ${kent_price:>8.2f} "
                    f"{'—' if abs(diff) < 0.01 else f'{diff:+.2f}'} {flag}"
                )
                results.append((sku, name, bom_price, kent_price, diff))
                save_result(conn, sku, name, kent_price, bom_price, url, it["division"])

                if abs(diff) >= 0.01:
                    price_changes.append((name, bom_price, kent_price))

        except RuntimeError as exc:
            errors.append((sku, name, str(exc)))
            print(f"{sku:<16} {name[:55]:<55} ${bom_price:>8.2f}  {'ERROR':>9}")

        if i < len(items):
            time.sleep(REQUEST_DELAY)

    conn.commit()
    conn.close()

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "═" * 100)
    print(f"Scraped:  {len(results)}/{len(items)} prices found")
    print(f"Errors:   {len(errors)}")
    print(f"Changed:  {len(price_changes)}")

    if price_changes:
        total_delta = sum(new - old for _, old, new in price_changes)
        print(f"\nPrice differences ({'+' if total_delta >= 0 else ''}{total_delta:.2f} total delta):")
        for name, old, new in sorted(price_changes, key=lambda x: abs(x[2] - x[1]), reverse=True):
            diff = new - old
            print(f"  {name[:60]:<60} ${old:>9.2f} → ${new:>9.2f}  ({diff:+.2f})")

        if auto_update:
            patch_bom_file(price_changes)
        else:
            print("\nRun with --update to auto-patch bom_data.py")

    if errors:
        print(f"\nFailed items:")
        for sku, name, err in errors:
            print(f"  {sku}: {name[:50]} — {err}")

    print(f"\nResults saved to {DB_PATH}")


if __name__ == "__main__":
    main()
