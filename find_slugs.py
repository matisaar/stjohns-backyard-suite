"""Try many URL slug variations for the 4 broken Kent.ca products."""
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
})

BASE = "https://kent.ca/en"

# For each broken product, try many URL slug variations
products = {
    "Sico PVA Primer 18.9L (1058991)": [
        f"{BASE}/sico-pro-pva-primer-sealer-white-18-9-l-1058991",
        f"{BASE}/sico-pro-pva-primer-sealer-18-9-l-white-1058991",
        f"{BASE}/interior-pva-primer-sealer-white-18-9-l-1058991",
        f"{BASE}/sico-pro-pva-interior-primer-sealer-white-18-9-l-1058991",
        f"{BASE}/sico-pro-primer-sealer-interior-pva-white-18-9-l-1058991",
        f"{BASE}/pro-pva-drywall-primer-interior-white-18-9l-1058991",
        f"{BASE}/sico-pro-pva-drywall-primer-sealer-interior-white-18-9l-1058991",
        f"{BASE}/primer-pva-interior-white-18-9-l-1058991",
        f"{BASE}/sico-pro-pva-drywall-sealer-primer-white-18-9l-1058991",
        f"{BASE}/sico-pva-primer-interior-white-18-9l-1058991",
        f"{BASE}/pva-drywall-primer-interior-white-18-9l-1058991",
        f"{BASE}/sico-pro-interior-pva-drywall-primer-sealer-white-18-9-l-1058991",
    ],
    "Sico Evolution Eggshell (1015669-NEU)": [
        f"{BASE}/sico-evolution-interior-latex-eggshell-neutral-base-3-78-l-1015669-NEU",
        f"{BASE}/sico-evolution-interior-eggshell-neutral-base-3-78-l-1015669-NEU",
        f"{BASE}/sico-evolution-eggshell-interior-neutral-base-3-78-l-1015669-NEU",
        f"{BASE}/sico-evolution-interior-latex-eggshell-3-78-l-neutral-base-1015669-NEU",
        f"{BASE}/interior-latex-eggshell-neutral-base-3-78-l-1015669-NEU",
        f"{BASE}/sico-evolution-eggshell-neutral-base-3-78l-1015669-NEU",
        f"{BASE}/evolution-interior-eggshell-neutral-base-3-78-l-1015669-NEU",
        f"{BASE}/sico-evolution-interior-eggshell-3-78-l-neutral-1015669-NEU",
        f"{BASE}/sico-evolution-latex-eggshell-interior-neutral-base-3-78l-1015669-NEU",
    ],
    "Clarovista Vinyl Plank (1142112-AEO)": [
        f"{BASE}/clarovista-5-0mm-stone-core-vinyl-plank-aged-european-oak-1142112-AEO",
        f"{BASE}/clarovista-5mm-stone-core-vinyl-plank-aged-european-oak-1142112-AEO",
        f"{BASE}/clarovista-stone-core-vinyl-plank-aged-european-oak-1142112-AEO",
        f"{BASE}/clarovista-5-0mm-vinyl-plank-aged-european-oak-1142112-AEO",
        f"{BASE}/clarovista-vinyl-plank-aged-european-oak-5mm-1142112-AEO",
        f"{BASE}/vinyl-plank-aged-european-oak-5-0mm-1142112-AEO",
        f"{BASE}/clarovista-5-0-mm-stone-core-vinyl-plank-aged-european-oak-1142112-AEO",
        f"{BASE}/stone-core-vinyl-plank-aged-european-oak-5mm-1142112-AEO",
    ],
    "Alexandria Baseboard (1447728)": [
        f"{BASE}/1-2-x-3-1-2-x-96-modern-mdf-baseboard-primed-valupak-1447728",
        f"{BASE}/modern-mdf-baseboard-1-2-x-3-1-2-x-96-primed-valupak-1447728",
        f"{BASE}/alexandria-modern-mdf-baseboard-primed-valupak-1447728",
        f"{BASE}/mdf-baseboard-1-2-x-3-1-2-x-96-primed-valupak-1447728",
        f"{BASE}/1-2-x-3-1-2-x-96-mdf-baseboard-modern-primed-valupak-1447728",
        f"{BASE}/1-2-x-3-1-2-x-96-modern-baseboard-primed-mdf-valupak-1447728",
        f"{BASE}/alexandria-1-2-x-3-1-2-x-96-modern-mdf-baseboard-primed-valupak-1447728",
        f"{BASE}/modern-mdf-primed-baseboard-1-2-x-3-1-2-x-96-valupak-1447728",
    ],
}

for product_name, urls in products.items():
    print(f"\n{'='*50}")
    print(f"Trying: {product_name}")
    found = False
    for url in urls:
        try:
            r = session.head(url, allow_redirects=True, timeout=10)
            if r.status_code == 200:
                print(f"  FOUND! {url}")
                found = True
                break
            else:
                # Just print a dot for 404s
                pass
        except Exception as e:
            pass
    if not found:
        print(f"  NOT FOUND after {len(urls)} attempts")
        
        # Last resort: try fetching a known-working URL to extract the slug pattern
        # by looking at the product page HTML for canonical URLs
        print(f"  Trying GET with follow redirects...")
        for url in urls[:3]:
            try:
                r = session.get(url, allow_redirects=True, timeout=10)
                if r.status_code == 200 and r.url != url:
                    print(f"  Redirected to: {r.url}")
                    found = True
                    break
            except:
                pass
        if not found:
            print(f"  Still not found")
