"""Download product images locally so they render on Vercel."""
import urllib.request
import os

IMG_DIR = "web/static/images"
os.makedirs(IMG_DIR, exist_ok=True)

images = {
    "lvp-clarovista.jpg": "https://kent.ca/media/catalog/product/1/1/1142112-AEO_1.jpg?quality=80&fit=bounds&height=300&width=300",
    "baseboard-alexandria.jpg": "https://kent.ca/media/catalog/product/1/4/1447728_1_1.jpg?quality=80&fit=bounds&height=300&width=300",
    "paint-sico-primer.jpg": "https://kent.ca/media/catalog/product/1/0/1058991_1.jpg?quality=80&fit=bounds&height=300&width=300",
    "paint-sico-evolution.jpg": "https://kent.ca/media/catalog/product/1/0/1015669-NEU_1.jpg?quality=80&fit=bounds&height=300&width=300",
    "kitchen-nickebo.jpg": "https://www.ikea.com/ca/en/images/products/nickebo-door-matte-anthracite__1013735_pe829891_s5.jpg",
}

for fname, url in images.items():
    path = os.path.join(IMG_DIR, fname)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK   {fname}: {len(data):,} bytes")
    except Exception as e:
        print(f"FAIL {fname}: {e}")
