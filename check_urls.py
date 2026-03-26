"""Test all product URLs in bom_data.py and report which are broken (404/redirect)."""
import requests
import re
import sys

# Extract all Kent URLs from the rendered data
sys.path.insert(0, '.')
from bom_data import ALL_DIVISIONS

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

ok = []
broken = []

for d in ALL_DIVISIONS:
    for item in d['items']:
        url = item.get('url') or ''
        if not url or url == '':
            continue
        name = item['name']
        sku = item.get('sku', '')
        
        try:
            resp = session.head(url, allow_redirects=True, timeout=10)
            status = resp.status_code
            final_url = resp.url
            
            if status == 200 and '/404' not in final_url and 'page-not-found' not in final_url:
                ok.append((name, sku, url, status))
                print(f"  OK  {status} | {name} | {url}")
            else:
                broken.append((name, sku, url, status, final_url))
                print(f" 404  {status} | {name} | {url}")
                if final_url != url:
                    print(f"       -> {final_url}")
        except Exception as e:
            broken.append((name, sku, url, 0, str(e)))
            print(f" ERR  {name} | {url} | {e}")

print(f"\n{'='*60}")
print(f"OK: {len(ok)}")
print(f"BROKEN: {len(broken)}")
print(f"{'='*60}")

if broken:
    print("\nBroken URLs:")
    for name, sku, url, status, final in broken:
        print(f"  {name} (SKU: {sku})")
        print(f"    {url}")
        print(f"    Status: {status} -> {final}")
        print()
