"""Download product images for all BOM items that don't have one yet."""
import os, re, requests, time
from bom_data import ALL_DIVISIONS

DEST = "web/static/images"
os.makedirs(DEST, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def extract_sku(url):
    """Extract SKU from Kent.ca URL (last number segment)."""
    m = re.search(r'-(\d{5,})$', url.rstrip('/'))
    return m.group(1) if m else None

def download_kent_image(sku):
    """Try multiple Kent.ca image URL patterns."""
    patterns = [
        f"https://kent.ca/media/catalog/product/{sku[0]}/{sku[1]}/{sku}_1.jpg",
        f"https://kent.ca/media/catalog/product/{sku[0]}/{sku[1]}/{sku}_1_1.jpg",
        f"https://kent.ca/media/catalog/product/{sku[0]}/{sku[1]}/{sku}_1_2.jpg",
        f"https://kent.ca/media/catalog/product/{sku[0]}/{sku[1]}/{sku}_2.jpg",
    ]
    for pat in patterns:
        try:
            r = requests.get(pat, headers=HEADERS, timeout=15)
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
        except:
            pass
    return None

downloaded = 0
skipped = 0
failed = []

for d in ALL_DIVISIONS:
    for item in d["items"]:
        # Skip if already has image
        if item.get("image_url"):
            skipped += 1
            continue

        url = item.get("url", "")
        name = item["name"]

        # Only download for Kent.ca URLs
        if "kent.ca" not in url:
            print(f"  SKIP (not Kent): {name}")
            continue

        sku = extract_sku(url)
        if not sku:
            print(f"  SKIP (no SKU): {name} — {url}")
            continue

        dest_path = os.path.join(DEST, f"{sku}.jpg")
        if os.path.exists(dest_path):
            print(f"  EXISTS: {sku}.jpg — {name}")
            downloaded += 1
            continue

        img_data = download_kent_image(sku)
        if img_data:
            with open(dest_path, "wb") as f:
                f.write(img_data)
            print(f"  ✅ {sku}.jpg ({len(img_data)//1024}KB) — {name}")
            downloaded += 1
            time.sleep(0.3)
        else:
            print(f"  ❌ FAILED: {sku} — {name}")
            failed.append((name, sku))

print(f"\nDone: {downloaded} downloaded, {skipped} already had images, {len(failed)} failed")
if failed:
    print("\nFailed items:")
    for name, sku in failed:
        print(f"  {sku}: {name}")
