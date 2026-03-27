#!/usr/bin/env python3
"""Quick script to verify IKO shingles price on Kent.ca"""
import urllib.request
import re
import json

url = 'https://www.kent.ca/en/building-materials/roofing/roof-shingles/40-7-8-x-13-3-4-cambridge-shingle-1010785'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})
resp = urllib.request.urlopen(req, timeout=30)
html = resp.read().decode('utf-8', errors='replace')

print(f"Page size: {len(html)} bytes")

# Strategy 1: JSON-LD
jld = re.findall(r'"price"\s*:\s*"?(\d+\.?\d*)"?', html)
print(f'JSON-LD/price matches: {jld}')

# Strategy 2: og:price
og = re.findall(r'og:price:amount.*?content="([\d.]+)"', html)
print(f'OG price: {og}')

# Strategy 3: data-price-amount
dpa = re.findall(r'data-price-amount="([\d.]+)"', html)
print(f'data-price-amount: {dpa}')

# Strategy 4: span.price
sp = re.findall(r'<span class="price">\s*\$?([\d,.]+)', html)
print(f'span.price: {sp}')

# Strategy 5: Magento finalPrice
mag = re.findall(r'"finalPrice":\{[^}]*"amount":([\d.]+)', html)
print(f'Magento finalPrice: {mag}')
magb = re.findall(r'"basePrice":\{[^}]*"amount":([\d.]+)', html)
print(f'Magento basePrice: {magb}')
magr = re.findall(r'"regular_price":\{[^}]*"amount":([\d.]+)', html)
print(f'Magento regularPrice: {magr}')

# Check for specific prices
for p in ['48.99', '42.99']:
    if p in html:
        idx = html.index(p)
        ctx = html[max(0,idx-150):idx+50]
        print(f'\nFOUND {p} at pos {idx}')
        print(f'Context: ...{ctx}...')
    else:
        print(f'\n{p} NOT found in page')

# Look for jsonConfig or priceBox
configs = re.findall(r'"jsonConfig"\s*:\s*(\{.*?\})\s*[,}]', html[:50000])
if configs:
    print(f'\njsonConfig found ({len(configs)} matches)')

# Look for all unique dollar amounts
all_prices = re.findall(r'\$(\d+\.\d{2})', html)
unique = sorted(set(all_prices))
print(f'\nAll unique dollar amounts on page: {unique}')
