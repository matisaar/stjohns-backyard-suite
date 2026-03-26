"""Download product images locally so they render on Vercel."""
import urllib.request
import os

IMG_DIR = "web/static/images"
os.makedirs(IMG_DIR, exist_ok=True)

# All Kent.ca SKUs — image URL pattern: /media/catalog/product/{c1}/{c2}/{sku}_1.jpg
KENT_SKUS = [
    "1016278",    # 2x6x8 SPF stud
    "1016313",    # 2x6x10 SPF
    "1016318",    # 2x4x8 SPF stud
    "1016339",    # 2x4x12 SPF
    "1016338",    # 2x4x10 SPF
    "1015823",    # 1/2 plywood
    "1015826",    # 5/8 plywood
    "1010820",    # vinyl siding
    "1021390",    # soffit
    "1010785",    # shingles
    "1026762",    # ice & water
    "1026830",    # felt underlayment
    "1021389",    # drip edge
    "1016918",    # step flashing
    "1042887",    # air chutes
    "1024741",    # R-20 15"
    "1024744",    # R-20 23"
    "1024751",    # R-28
    "1024752",    # R-31
    "1016148",    # 1/2" drywall 4x8
    "1016149",    # 1/2" drywall 4x12
    "1016160",    # 5/8" firecode drywall
    "1021974",    # drywall compound
    "1058991",    # Sico primer
    "1015669-NEU",# Sico Evolution paint
    "1142112-AEO",# Clarovista LVP
    "1447728",    # Alexandria baseboard
]

# Non-Kent images
EXTRA = {
    "kitchen-nickebo.jpg": "https://www.ikea.com/ca/en/images/products/nickebo-door-matte-anthracite__1126853_pe875878_s5.jpg?f=s",
}


def kent_image_url(sku):
    c1, c2 = sku[0], sku[1]
    return f"https://kent.ca/media/catalog/product/{c1}/{c2}/{sku}_1.jpg?quality=80&fit=bounds&height=300&width=300"


ok, fail = 0, 0
for sku in KENT_SKUS:
    fname = f"{sku}.jpg"
    path = os.path.join(IMG_DIR, fname)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(f"SKIP {fname} (exists)")
        ok += 1
        continue
    url = kent_image_url(sku)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        if len(data) < 500:
            print(f"TINY {fname}: {len(data)} bytes — skipping")
            fail += 1
            continue
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK   {fname}: {len(data):,} bytes")
        ok += 1
    except Exception as e:
        print(f"FAIL {fname}: {e}")
        fail += 1

for fname, url in EXTRA.items():
    path = os.path.join(IMG_DIR, fname)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(f"SKIP {fname} (exists)")
        ok += 1
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK   {fname}: {len(data):,} bytes")
        ok += 1
    except Exception as e:
        print(f"FAIL {fname}: {e}")
        fail += 1

print(f"\nDone: {ok} OK, {fail} failed")
