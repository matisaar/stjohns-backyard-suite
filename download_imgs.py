#!/usr/bin/env python3
"""Download Kent.ca product images for new BOM items."""
import urllib.request, os

imgs = {
    "1080226": "https://kent.ca/media/catalog/product/cache/large_image/1080226.png",
    "1462201": "https://kent.ca/media/catalog/product/cache/large_image/1462201.png",
    "1531122": "https://kent.ca/media/catalog/product/cache/large_image/1531122.png",
    "1015090": "https://kent.ca/media/catalog/product/cache/large_image/1015090.png",
    "1016290": "https://kent.ca/media/catalog/product/cache/large_image/1016290.png",
}
outdir = "web/static/images"
for sku, url in imgs.items():
    out = os.path.join(outdir, f"{sku}.jpg")
    if os.path.exists(out):
        print(f"{sku}: already exists")
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        if len(data) == 84065:
            print(f"{sku}: placeholder ({len(data)} bytes), skipping")
        else:
            with open(out, "wb") as f:
                f.write(data)
            print(f"{sku}: saved ({len(data)} bytes)")
    except Exception as e:
        print(f"{sku}: error - {e}")
