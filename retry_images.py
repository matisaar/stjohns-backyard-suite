"""Retry downloading images with alternate URL pattern for placeholder SKUs."""
import urllib.request
import os
import hashlib

IMG_DIR = "web/static/images"
PLACEHOLDER_HASH = "ee559393b198ebb8261ac9a6ce88767d"

retry_skus = [
    "1016278", "1016313", "1016339", "1016338",
    "1024741", "1024744", "1024751", "1024752",
    "1021974", "1058991",
]

for sku in retry_skus:
    c1, c2 = sku[0], sku[1]
    url = f"https://kent.ca/media/catalog/product/{c1}/{c2}/{sku}_1_1.jpg?quality=80&fit=bounds&height=300&width=300"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        h = hashlib.md5(data).hexdigest()
        if h != PLACEHOLDER_HASH and len(data) > 500:
            path = os.path.join(IMG_DIR, f"{sku}.jpg")
            with open(path, "wb") as f:
                f.write(data)
            print(f"OK   {sku}: {len(data):,} bytes (alt URL)")
        else:
            print(f"SAME {sku}: still placeholder")
    except Exception as e:
        print(f"FAIL {sku}: {e}")
