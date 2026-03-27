#!/usr/bin/env python3
"""Verify specific Kent.ca prices"""
import urllib.request
import re
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}

items = [
    ("XPS Insulation", "https://kent.ca/en/sopra-xps-60-square-2-x-8-x-1-5-1694221"),
    ("10/3 NMD90 Wire", "https://kent.ca/en/10-3-nmd90-75m-electrical-wire-orange-1026026"),
    ("IKO Shingles", "https://kent.ca/en/40-7-8-x-13-3-4-cambridge-shingle-1010785"),
    ("Countertop", "https://kent.ca/en/25-x-8-2300-kitchen-countertop-1015537"),
]

for name, url in items:
    print(f"\n{'='*60}")
    print(f"Checking: {name}")
    print(f"URL: {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="replace")
        print(f"Page size: {len(html)} bytes")

        # All strategies
        # Magento finalPrice
        m = re.search(r'"finalPrice"\s*:\s*\{\s*"amount"\s*:\s*([0-9]+(?:\.[0-9]{1,2})?)', html)
        print(f"  Magento finalPrice: {m.group(1) if m else 'NOT FOUND'}")

        # data-price-amount
        dpa = re.findall(r'data-price-amount="([\d.]+)"', html)
        print(f"  data-price-amount: {dpa}")

        # OG meta
        og = re.findall(r'og:price:amount.*?content="([\d.]+)"', html)
        print(f"  OG price: {og}")

        # JSON-LD
        jld_prices = []
        for blob in re.findall(r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
            try:
                data = json.loads(blob)
                items_check = [data] if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for item in items_check:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        offers = item.get("offers", {})
                        if isinstance(offers, dict) and "price" in offers:
                            jld_prices.append(offers["price"])
            except:
                pass
        print(f"  JSON-LD price: {jld_prices}")

        # All dollar amounts
        all_p = sorted(set(re.findall(r'\$(\d+\.\d{2})', html)))
        print(f"  All $ amounts: {all_p[:15]}")

    except Exception as e:
        print(f"  ERROR: {e}")

    time.sleep(1)
