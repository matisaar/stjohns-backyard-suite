"""Verify the correct URLs found via sitemap."""
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

urls = {
    "Sico PVA Primer": "https://kent.ca/en/sico-pro-pva-primer-white-18-9l-1058991",
    "Sico Evolution": "https://kent.ca/en/evolution-3-78-l-interior-eggshell-neutral-base-1015669-neu",
    "Clarovista LVP": "https://kent.ca/en/5-0-mm-aged-european-oak-stone-core-vinyl-plank-18-94-sf-bx-1142112-aeo",
    "Alexandria Base": "https://kent.ca/en/1-2-x-3-1-2-x-8-modern-mdf-baseboard-valupak-10-pack-1447728",
}

# Also check St Johns building permit page
urls["Building Permit"] = "https://www.stjohns.ca/en/living-in-st-johns/building-permits.aspx"
urls["Building Permit v2"] = "https://www.stjohns.ca/living-in-st-johns/building-permits"
urls["Building Permit v3"] = "https://www.stjohns.ca/en/living-in-st-johns/building-permits"

for name, url in urls.items():
    try:
        r = session.head(url, allow_redirects=True, timeout=10)
        status = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
        final = f" -> {r.url}" if r.url != url else ""
        print(f"  {status} | {name} | {url}{final}")
    except Exception as e:
        print(f"  ERR | {name} | {e}")
