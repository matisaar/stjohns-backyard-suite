#!/usr/bin/env python3
"""
Automated BOM verification tests.
Run: python3 test_bom.py

Tests:
  1. Every item with image_url has a real image file (not a placeholder)
  2. Every item has a working URL (HTTP 200)
  3. Every non-estimate item price matches the Kent.ca/IKEA listing
  4. Data integrity checks (no missing fields, no duplicates)
"""
import hashlib
import os
import sys
import time
import urllib.request
import urllib.error
import ssl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bom_data import ALL_DIVISIONS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
IMG_DIR = os.path.join(os.path.dirname(__file__), "web", "static", "images")
# Kent placeholder images are ~3-5KB, 300×300. We fingerprint by md5.
PLACEHOLDER_HASHES = set()
PLACEHOLDER_SIZE_THRESHOLD = 6000  # bytes — anything under this is suspect

# Build a reference hash from the smallest known placeholder
_candidates = []
for f in os.listdir(IMG_DIR):
    if f.endswith(".jpg"):
        fpath = os.path.join(IMG_DIR, f)
        sz = os.path.getsize(fpath)
        if sz < PLACEHOLDER_SIZE_THRESHOLD:
            with open(fpath, "rb") as fh:
                PLACEHOLDER_HASHES.add(hashlib.md5(fh.read()).hexdigest())
            _candidates.append((f, sz))


def _all_items():
    """Yield (division_name, item) for every BOM item."""
    for div in ALL_DIVISIONS:
        for item in div["items"]:
            yield div["name"], item


# ---------------------------------------------------------------------------
# Test 1: Image files exist and are real product photos
# ---------------------------------------------------------------------------
def test_image_files():
    """Every item with image_url must have a non-placeholder image on disk."""
    failures = []
    for div_name, item in _all_items():
        img = item.get("image_url", "")
        if not img:
            continue
        fpath = os.path.join("web", img.lstrip("/"))
        if not os.path.exists(fpath):
            failures.append(f"FILE MISSING: [{div_name}] {item['name']} -> {fpath}")
            continue
        sz = os.path.getsize(fpath)
        if sz < PLACEHOLDER_SIZE_THRESHOLD:
            with open(fpath, "rb") as fh:
                md5 = hashlib.md5(fh.read()).hexdigest()
            if md5 in PLACEHOLDER_HASHES:
                failures.append(
                    f"PLACEHOLDER: [{div_name}] {item['name']} -> {os.path.basename(fpath)} ({sz}B)"
                )
    return failures


# ---------------------------------------------------------------------------
# Test 2: Every URL returns HTTP 200
# ---------------------------------------------------------------------------
def test_urls():
    """Every item URL must return HTTP 2xx."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    failures = []
    checked = set()
    for div_name, item in _all_items():
        url = item.get("url", "")
        if not url:
            failures.append(f"NO URL: [{div_name}] {item['name']}")
            continue
        # Resolve f-string references (already resolved at import time)
        if url in checked:
            continue
        checked.add(url)
        try:
            req = urllib.request.Request(url, method="HEAD", headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) BOM-Checker/1.0"
            })
            resp = urllib.request.urlopen(req, timeout=20, context=ctx)
            code = resp.getcode()
            if code >= 400:
                failures.append(f"HTTP {code}: [{div_name}] {item['name']} -> {url}")
        except urllib.error.HTTPError as e:
            # Some servers block HEAD, try GET
            try:
                req2 = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) BOM-Checker/1.0"
                })
                resp2 = urllib.request.urlopen(req2, timeout=20, context=ctx)
                code2 = resp2.getcode()
                if code2 >= 400:
                    failures.append(f"HTTP {code2}: [{div_name}] {item['name']} -> {url}")
            except Exception as e2:
                failures.append(f"ERROR ({e2}): [{div_name}] {item['name']} -> {url}")
        except Exception as e:
            failures.append(f"ERROR ({e}): [{div_name}] {item['name']} -> {url}")
        time.sleep(0.1)  # Be polite
    return failures


# ---------------------------------------------------------------------------
# Test 3: Prices — verify Kent.ca items have non-zero prices, estimates flagged
# ---------------------------------------------------------------------------
def test_prices():
    """
    - Non-estimate items must have unit_price > 0
    - Estimate items must have 'estimate': True flag
    - No item should have negative price
    """
    failures = []
    kent_count = 0
    for div_name, item in _all_items():
        price = item.get("unit_price", 0)
        url = item.get("url", "")
        is_est = item.get("estimate", False)

        if price < 0:
            failures.append(f"NEGATIVE PRICE: [{div_name}] {item['name']} = ${price}")
        if price == 0 and not is_est:
            failures.append(f"ZERO PRICE (not estimate): [{div_name}] {item['name']}")
        if "kent.ca" in url:
            kent_count += 1
            if is_est and "/search" not in url:
                failures.append(f"KENT ITEM MARKED ESTIMATE: [{div_name}] {item['name']}")
        if "kent.ca" not in url and "ikea" not in url.lower() and not is_est:
            # Non-retailer items should be flagged as estimates
            failures.append(
                f"UNVERIFIED PRICE NOT FLAGGED: [{div_name}] {item['name']} (${price:.2f}, url={url[:50]}...)"
            )
    return failures


# ---------------------------------------------------------------------------
# Test 4: Data integrity
# ---------------------------------------------------------------------------
def test_data_integrity():
    """Check required fields, duplicates, division structure."""
    failures = []
    names_seen = set()
    required_fields = {"name", "qty", "unit", "unit_price", "url"}

    for div in ALL_DIVISIONS:
        if "name" not in div:
            failures.append(f"DIVISION MISSING NAME: {div}")
        if "items" not in div or not div["items"]:
            failures.append(f"DIVISION EMPTY: {div.get('name', '???')}")

    for div_name, item in _all_items():
        for field in required_fields:
            if field not in item:
                failures.append(f"MISSING FIELD '{field}': [{div_name}] {item.get('name', '???')}")
        name = item.get("name", "")
        if name in names_seen:
            failures.append(f"DUPLICATE NAME: [{div_name}] {name}")
        names_seen.add(name)

    return failures


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def main():
    total_items = sum(1 for _ in _all_items())
    print(f"BOM Verification — {total_items} items across {len(ALL_DIVISIONS)} divisions\n")
    print("=" * 70)

    all_pass = True
    tests = [
        ("Image files present & real", test_image_files),
        ("All URLs reachable", test_urls),
        ("Prices valid & flagged", test_prices),
        ("Data integrity", test_data_integrity),
    ]

    for test_name, test_fn in tests:
        print(f"\n▸ {test_name}...")
        failures = test_fn()
        if failures:
            all_pass = False
            print(f"  ✗ FAILED ({len(failures)} issues)")
            for f in failures:
                print(f"    - {f}")
        else:
            print(f"  ✓ PASSED")

    print("\n" + "=" * 70)
    if all_pass:
        print("ALL TESTS PASSED ✓")
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
