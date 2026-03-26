#!/usr/bin/env python3
"""Scrape Kent.ca prices for St. John's store (10 Stavanger Dr) for all SKU'd BOM items."""
import urllib.request
import json
import re
import time

# St. John's store cookie — Kent uses "store_code" cookie
# We need to find the right store ID first, then pass it as a cookie
STORE_COOKIE = "store=st_johns"  # try common patterns

SKUS_AND_URLS = [
    ("1016278", "2x6x8 SPF Stud", 6.48, "/en/2-x-6-x-8-spf-stud-kiln-dried-1016278"),
    ("1016313", "2x6x10 SPF", 10.88, "/en/2-x-6-x-10-spf-no-2-better-kd-1016313"),
    ("1016318", "2x4x8 SPF Stud", 3.98, "/en/2-x-4-x-8-spf-stud-kiln-dried-1016318"),
    ("1016339", "2x4x12 SPF", 7.66, "/en/2-x-4-x-12-spf-no-2-better-kd-1016339"),
    ("1016338", "2x4x10 SPF", 6.38, "/en/2-x-4-x-10-spf-no-2-better-kd-1016338"),
    ("1015823", "1/2 Spruce Plywood", 39.98, "/en/1-2-x-4-x-8-spruce-plywood-1015823"),
    ("1015826", "5/8 Spruce Plywood", 54.38, "/en/5-8-x-4-x-8-spruce-plywood-1015826"),
    ("1015824", "3/4 Spruce Plywood", 63.98, "/en/3-4-x-4-x-8-spruce-plywood-1015824"),
    ("1010820", "Vinyl Siding", 11.19, "/en/mitten-oregon-pride-dutchlap-vinyl-siding-12-1-1010820"),
    ("1021390", "Perforated Soffit", 2.48, "/en/double-5-perforated-soffit-12-pieces-1021390"),
    ("1010785", "IKO Cambridge Shingles", 40.99, "/en/iko-cambridge-shingles-dual-black-1010785"),
    ("1026762", "IKO Ice & Water", 84.99, "/en/iko-stormshield-ice-water-protector-36-x65-1026762"),
    ("1026830", "Felt Underlayment", 44.99, "/en/organic-felt-underlayment-36-x131-1026830"),
    ("1021389", "Drip Edge", 8.29, "/en/drip-edge-10-pebble-1021389"),
    ("1016918", "Step Flashing", 3.49, "/en/step-flashing-4-x4-x8-1016918"),
    ("1042887", "Thermocell Air Chutes", 2.19, "/en/thermocell-air-chutes-22-5-x27-1042887"),
    ("1024741", "R-20 Batt 15in", 89.57, "/en/owens-corning-r-20-fiberglass-batt-15-78-3-sqft-bag-1024741"),
    ("1024744", "R-20 Batt 23in", 137.00, "/en/owens-corning-r-20-fiberglass-batt-23-120-1-sqft-bag-1024744"),
    ("1024751", "R-28 Batt", 126.00, "/en/owens-corning-r-28-fiberglass-batt-24-80-sqft-bag-1024751"),
    ("1024752", "R-31 Batt", 79.99, "/en/owens-corning-r-31-fiberglass-batt-16-42-7-sqft-bag-1024752"),
    ("1016148", "1/2 UltraLight Drywall", 17.82, "/en/cgc-1-2-x-4-x-8-ultralight-drywall-1016148"),
    ("1016149", "1/2 12ft Drywall", 26.73, "/en/cgc-1-2-x-4-x-12-tapered-edge-drywall-1016149"),
    ("1016160", "5/8 Type X Drywall", 31.99, "/en/cgc-5-8-x-4-x-8-type-x-firecode-drywall-1016160"),
    ("1021974", "Drywall Compound 17L", 32.87, "/en/cgc-17l-all-purpose-lite-drywall-compound-1021974"),
    ("1058991", "Sico Primer 18.9L", 84.00, "/en/sico-pro-pva-drywall-primer-white-18-9l-1058991"),
    ("1015669-NEU", "Sico Evolution Paint", 68.99, "/en/sico-evolution-interior-eggshell-pure-white-3-78l-1015669-neu"),
    ("1080257-PWT", "Volcano Pewter LVP", 88.19, "/en/5-3mm-volcano-pewter-engineered-stone-core-vinyl-23-33-sf-1080257-pwt"),
    ("1447728", "MDF Baseboard Valupak", 50.89, "/en/alexandria-1-2-x3-1-2-x96-modern-mdf-baseboard-valupak-1447728"),
]

BASE = "https://kent.ca"

results = []
for sku, name, bom_price, path in SKUS_AND_URLS:
    url = BASE + path
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Cookie": "store_view=en; selected_store=st-johns",
            "Accept": "text/html",
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")

        # Try to find price in JSON-LD or meta tags
        price = None

        # Look for "price" in JSON-LD structured data
        json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for blob in json_ld:
            try:
                data = json.loads(blob)
                if isinstance(data, dict):
                    offers = data.get("offers", {})
                    if isinstance(offers, dict) and "price" in offers:
                        price = float(offers["price"])
                        break
                    elif isinstance(offers, list):
                        for o in offers:
                            if "price" in o:
                                price = float(o["price"])
                                break
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback: look for meta property="product:price:amount"
        if price is None:
            m = re.search(r'<meta\s+property="product:price:amount"\s+content="([^"]+)"', html)
            if m:
                price = float(m.group(1))

        # Fallback: look for data-price-amount
        if price is None:
            m = re.search(r'data-price-amount="([^"]+)"', html)
            if m:
                price = float(m.group(1))

        # Fallback: span.price pattern
        if price is None:
            m = re.search(r'<span[^>]*class="price"[^>]*>\s*\$([0-9]+\.[0-9]+)', html)
            if m:
                price = float(m.group(1))

        if price is not None:
            diff = price - bom_price
            flag = "" if abs(diff) < 0.01 else f"  DIFF {diff:+.2f}"
            results.append((sku, name, bom_price, price, diff))
            print(f"{sku:15s} {name:30s}  BOM ${bom_price:>8.2f}  Kent ${price:>8.2f}{flag}")
        else:
            results.append((sku, name, bom_price, None, None))
            print(f"{sku:15s} {name:30s}  BOM ${bom_price:>8.2f}  Kent: PRICE NOT FOUND")

    except Exception as e:
        results.append((sku, name, bom_price, None, None))
        print(f"{sku:15s} {name:30s}  BOM ${bom_price:>8.2f}  ERROR: {e}")

    time.sleep(0.15)

# Summary
print("\n" + "=" * 80)
changed = [(r[0], r[1], r[2], r[3], r[4]) for r in results if r[3] is not None and abs(r[4]) >= 0.01]
print(f"\nTotal items checked: {len(results)}")
print(f"Prices found: {sum(1 for r in results if r[3] is not None)}")
print(f"Prices that differ: {len(changed)}")
if changed:
    print("\nItems needing update:")
    for sku, name, old, new, diff in changed:
        print(f"  {sku}: ${old:.2f} -> ${new:.2f} ({diff:+.2f})")
