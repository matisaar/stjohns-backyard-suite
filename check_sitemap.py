"""Check Kent.ca sitemap for product URLs."""
import requests
import re

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

# Check robots.txt first
try:
    r = session.get("https://kent.ca/robots.txt", timeout=10)
    print(f"robots.txt: {r.status_code}")
    if r.status_code == 200:
        print(r.text[:3000])
except Exception as e:
    print(f"robots.txt error: {e}")

print("\n" + "=" * 50)

# Check sitemap
for sm_url in [
    "https://kent.ca/sitemap.xml",
    "https://kent.ca/pub/sitemap.xml", 
    "https://kent.ca/en/sitemap.xml",
    "https://kent.ca/pub/media/sitemap.xml",
]:
    try:
        r = session.get(sm_url, timeout=10)
        print(f"\n{r.status_code} {sm_url}")
        if r.status_code == 200:
            print(f"  Size: {len(r.text)} bytes")
            # Check if it's a sitemap index (pointing to sub-sitemaps)
            sub_sitemaps = re.findall(r"<loc>([^<]+\.xml[^<]*)</loc>", r.text)
            if sub_sitemaps:
                print(f"  Sub-sitemaps: {len(sub_sitemaps)}")
                for sm in sub_sitemaps[:10]:
                    print(f"    {sm}")
            
            # Look directly for our SKUs
            for sku in ["1058991", "1015669", "1142112", "1447728"]:
                if sku in r.text:
                    matches = re.findall(r"<loc>([^<]*" + sku + r"[^<]*)</loc>", r.text)
                    print(f"  Found SKU {sku}: {matches}")
    except Exception as e:
        print(f"  Error: {e}")
