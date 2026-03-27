#!/usr/bin/env python3
"""Scrape live Kent.ca prices for every BOM item.

Completely rewritten scraper with robust price extraction:
  - Targets the canonical price for the exact SKU in the URL
  - Multiple extraction strategies with SKU-awareness
  - Handles colour variants, pack sizes, sale prices
  - Stores results in SQLite and can auto-patch bom_data.py
  - Rate-limited, polite, with retry logic

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
REQUEST_DELAY = 0.5          # seconds between requests — be polite
RETRY_DELAY = 2.0            # seconds before retry on failure
MAX_RETRIES = 2              # retry count per item
TIMEOUT = 15                 # per-request timeout
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
      kent.ca/en/…-1016278         → 1016278
      kent.ca/en/…-1015669-neu     → 1015669-neu
      kent.ca/en/…-1080257-pwt     → 1080257-pwt
      kent.ca/en/…-1010785-hsl     → 1010785-hsl
    """
    if "kent.ca" not in url:
        return ""
    m = re.search(r'-(\d{6,8}(?:-[a-z]+)?)(?:\?|$)', url)
    return m.group(1) if m else ""


def fetch_page(url: str) -> str:
    """Fetch a URL with retry logic. Returns HTML string."""
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=TIMEOUT)
            return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_err = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"HTTP error after {MAX_RETRIES + 1} attempts: {last_err}")


def scrape_price(url: str) -> float | None:
    """Fetch a Kent.ca product page and extract the price.

    Uses a ranked strategy list — returns the first successful extraction.
    Each strategy is designed to find the MAIN product price, not related
    products, accessories, or different variants.

    Strategy order: prefer LIVE rendered prices (Magento JSON, data-price-amount)
    over potentially-stale SEO metadata (JSON-LD, Open Graph).
    """
    html = fetch_page(url)
    sku = extract_sku_from_url(url)
    sku_base = sku.split("-")[0] if sku else ""

    # ─── Strategy 1: Magento JSON "finalPrice" (live rendered price) ─────
    # Kent's Magento stores embed the ACTUAL displayed price in JSON config
    # blocks. This is the most accurate source — it's what the customer sees.
    for pat in [
        r'"finalPrice"\s*:\s*\{\s*"amount"\s*:\s*([0-9]+(?:\.[0-9]{1,2})?)',
        r'"regular_price"\s*:\s*\{\s*"amount"\s*:\s*([0-9]+(?:\.[0-9]{1,2})?)',
        r'"basePrice"\s*:\s*\{\s*"amount"\s*:\s*([0-9]+(?:\.[0-9]{1,2})?)',
    ]:
        m = re.search(pat, html)
        if m:
            try:
                p = float(m.group(1))
                if p > 0:
                    return p
            except ValueError:
                pass

    # ─── Strategy 2: First data-price-amount on page ─────────────────────
    # Magento renders the visible price with this attribute.
    m = re.search(r'data-price-amount="([^"]+)"', html)
    if m:
        try:
            p = float(m.group(1))
            if p > 0:
                return p
        except ValueError:
            pass

    # ─── Strategy 3: SKU-specific data-price-amount ──────────────────────
    # If there's a SKU match nearby, that's the canonical price for this variant.
    if sku_base:
        sku_region = re.search(
            rf'{re.escape(sku_base)}.*?data-price-amount="([^"]+)"',
            html[:50000], re.DOTALL | re.IGNORECASE
        )
        if sku_region:
            try:
                p = float(sku_region.group(1))
                if p > 0:
                    return p
            except ValueError:
                pass

    # ─── Strategy 4: Open Graph / meta tags ──────────────────────────────
    for tag_re in [
        r'<meta\s+property="product:price:amount"\s+content="([^"]+)"',
        r'<meta\s+content="([^"]+)"\s+property="product:price:amount"',
        r'<meta\s+property="og:price:amount"\s+content="([^"]+)"',
    ]:
        m = re.search(tag_re, html, re.IGNORECASE)
        if m:
            try:
                p = float(m.group(1))
                if p > 0:
                    return p
            except ValueError:
                pass

    # ─── Strategy 5: Visible price span ──────────────────────────────────
    # Kent renders <span class="price">$XX.XX</span>
    m = re.search(r'<span[^>]*class="[^"]*price[^"]*"[^>]*>\s*\$\s*([0-9,]+\.[0-9]{2})', html)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass

    # ─── Strategy 6: JSON-LD structured data (can be stale/cached!) ──────
    # Kent.ca embeds Product schema for SEO but this data can lag behind
    # the actual live price. Use only as a last resort.
    for blob in re.findall(
        r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL
    ):
        try:
            data = json.loads(blob)
            items_to_check = [data] if isinstance(data, dict) else (data if isinstance(data, list) else [])
            for item in items_to_check:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") not in ("Product", "product"):
                    continue
                offers = item.get("offers")
                if isinstance(offers, dict) and "price" in offers:
                    p = float(offers["price"])
                    if p > 0:
                        return p
                if isinstance(offers, list):
                    for o in offers:
                        if isinstance(o, dict) and "price" in o:
                            p = float(o["price"])
                            if p > 0:
                                return p
                if "price" in item:
                    p = float(item["price"])
                    if p > 0:
                        return p
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    return None


# ── database ─────────────────────────────────────────────────────────────────

def init_db():
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_materials_sku ON materials(sku)")
    conn.commit()
    return conn


def save_result(conn, sku, name, price, bom_price, url, division):
    conn.execute(
        "INSERT INTO materials (sku, name, price, bom_price, url, division, scraped_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (sku, name, price, bom_price, url, division, TODAY),
    )


# ── BOM patching ─────────────────────────────────────────────────────────────

def format_price(p: float) -> str:
    """Format a price to 2 decimal places, matching bom_data.py conventions."""
    if p == int(p):
        return f"{p:.2f}"
    return f"{p:.2f}"


def patch_bom_file(updates: list[tuple[str, float, float]]):
    """Replace unit_price values in bom_data.py.

    Each entry: (item_name_substring, old_price, new_price).
    Uses robust regex that handles escaped quotes and Unicode in names.
    """
    with open(BOM_FILE, "r") as f:
        src = f.read()

    patched = 0
    for name, old_price, new_price in updates:
        old_str = format_price(old_price)
        new_str = format_price(new_price)
        # Match: "name": "...name_fragment..." followed by "unit_price": old_price
        # Use a safe substring (first 25 chars, no special chars)
        safe_name = re.escape(name[:25])
        pattern = re.compile(
            r'("name":\s*"(?:[^"\\]|\\.)*' + safe_name + r'(?:[^"\\]|\\.)*"'
            r'.*?'
            r'"unit_price":\s*)' + re.escape(old_str),
            re.DOTALL
        )
        new_src = pattern.sub(r'\g<1>' + new_str, src, count=1)
        if new_src != src:
            src = new_src
            patched += 1

    if patched:
        with open(BOM_FILE, "w") as f:
            f.write(src)
        print(f"\n  Patched {patched} price(s) in bom_data.py")
    else:
        print("\n  No prices needed patching in bom_data.py")


# ── item collection ──────────────────────────────────────────────────────────

# Items where BOM uses LOT/allowance pricing (aggregated cost for multiple
# small parts). The scraped per-unit price is meaningless for these.
LOT_ITEMS = {
    "Simpson Strong-Tie",
    "Construction Screws",
    "Siding Accessories",  # starter strip, J-channel
    "Vinyl Siding Starter",  # alt name for same LOT item
    "Caulking & Sealants",
    "Drywall Tape, Corner",
    "PEX Fittings",
    "ABS/PVC Drain",
    "Electrical Boxes",
    "HRV Ducting",
    "Thin-Set Mortar",
    "Laminate Countertop",  # Kent shows $0 (discontinued); keep BOM estimate
}

# Items where BOM unit doesn't match Kent's selling unit
UNIT_MISMATCH = {
    "Gravel Base",       # BOM: cu yd, Kent: per bag
    "Concrete",          # BOM: cu m, Kent: per bag
    "Wire Mesh",         # BOM: sqft, Kent: per sheet
    "Drain Tile",        # BOM: LF, Kent: per pipe
    "Ceramic Wall Tile", # BOM: sqft, Kent: per box
}


def is_lot_item(name: str) -> bool:
    return any(kw.lower() in name.lower() for kw in LOT_ITEMS)

def is_unit_mismatch(name: str) -> bool:
    return any(kw.lower() in name.lower() for kw in UNIT_MISMATCH)


def collect_kent_items():
    """Build list of all Kent.ca-linked items suitable for price comparison."""
    items = []
    seen_urls = set()
    for div in ALL_DIVISIONS:
        for item in div["items"]:
            url = item.get("url", "")
            if "kent.ca" not in url:
                continue
            if "/search?" in url:
                continue
            # Skip qty=0 items (disabled in BOM)
            if item.get("qty", 0) <= 0:
                continue
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
                "qty": item.get("qty", 1),
                "unit": item.get("unit", ""),
                "is_lot": is_lot_item(item["name"]),
                "is_mismatch": is_unit_mismatch(item["name"]),
            })
    return items


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    auto_update = "--update" in sys.argv

    items = collect_kent_items()
    print(f"Found {len(items)} Kent.ca items to scrape\n")
    print(f"{'SKU':<16} {'Item':<50} {'BOM $':>9} {'Kent $':>9} {'Diff':>8}  Notes")
    print("=" * 110)

    conn = init_db()
    # Clear today's results for clean re-scrape
    conn.execute("DELETE FROM materials WHERE scraped_date = ?", (TODAY,))
    conn.commit()

    results = []
    errors = []
    price_updates = []     # genuine per-unit price corrections
    lot_diffs = []         # LOT items with price info (not updated)
    mismatch_diffs = []    # unit mismatch items (not updated)

    for i, it in enumerate(items, 1):
        sku = it["sku"]
        name = it["name"]
        bom_price = it["bom_price"]
        url = it["url"]

        try:
            kent_price = scrape_price(url)

            if kent_price is None:
                errors.append((sku, name, "price not found"))
                print(f"{sku:<16} {name[:50]:<50} ${bom_price:>8.2f}  {'NOTFOUND':>9}")
            else:
                diff = kent_price - bom_price
                flag = ""
                note = ""

                if it["is_lot"]:
                    note = "LOT (skip)"
                    flag = "~"
                    lot_diffs.append((name, bom_price, kent_price))
                elif it["is_mismatch"]:
                    note = "unit mismatch (skip)"
                    flag = "~"
                    mismatch_diffs.append((name, bom_price, kent_price))
                elif abs(diff) >= 0.01:
                    flag = "!" if abs(diff) > bom_price * 0.1 else "*"
                    price_updates.append((name, bom_price, kent_price))

                diff_str = "—" if abs(diff) < 0.01 else f"{diff:+.2f}"
                print(
                    f"{sku:<16} {name[:50]:<50} ${bom_price:>8.2f} ${kent_price:>8.2f} "
                    f"{diff_str:>8}  {note}"
                )
                results.append((sku, name, bom_price, kent_price, diff))
                save_result(conn, sku, name, kent_price, bom_price, url, it["division"])

        except RuntimeError as exc:
            errors.append((sku, name, str(exc)))
            print(f"{sku:<16} {name[:50]:<50} ${bom_price:>8.2f}  {'ERROR':>9}  {str(exc)[:40]}")

        if i < len(items):
            time.sleep(REQUEST_DELAY)

    conn.commit()
    conn.close()

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print(f"Scraped: {len(results)}/{len(items)} prices found")
    print(f"Errors:  {len(errors)}")
    print(f"Updates: {len(price_updates)} items need price correction")
    print(f"Skipped: {len(lot_diffs)} LOT items, {len(mismatch_diffs)} unit mismatches")

    if price_updates:
        total_delta = sum(new - old for _, old, new in price_updates)
        print(f"\n── Price corrections needed ({'+' if total_delta >= 0 else ''}{total_delta:.2f} total delta) ──")
        for name, old, new in sorted(price_updates, key=lambda x: abs(x[2] - x[1]), reverse=True):
            diff = new - old
            pct = (diff / old * 100) if old else 0
            print(f"  {name[:55]:<55} ${old:>9.2f} -> ${new:>9.2f}  ({diff:+.2f}, {pct:+.1f}%)")

        if auto_update:
            patch_bom_file(price_updates)
        else:
            print("\n  Run with --update to auto-patch bom_data.py")

    if errors:
        print(f"\n── Failed items ──")
        for sku, name, err in errors:
            print(f"  {sku}: {name[:45]} — {err[:60]}")

    print(f"\nResults saved to {DB_PATH}")


if __name__ == "__main__":
    main()
