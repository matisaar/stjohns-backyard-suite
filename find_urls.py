"""Search Kent.ca for correct product URLs by SKU number."""
import requests
import re
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-CA,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
})

skus = ['1058991', '1015669', '1142112', '1447728']

for sku in skus:
    print(f"\n{'='*50}")
    print(f"Searching for SKU: {sku}")
    
    # Try direct product URL patterns
    # Kent uses pattern: kent.ca/en/PRODUCT-SLUG-SKU
    # Try the search API
    search_url = f"https://kent.ca/en/catalogsearch/result/?q={sku}"
    
    try:
        resp = session.get(search_url, timeout=15)
        print(f"  Search status: {resp.status_code}")
        
        if resp.status_code == 200:
            # Look for product links in the HTML
            # Kent product links contain the SKU
            links = re.findall(r'href="(https?://kent\.ca/en/[^"]*' + sku + r'[^"]*)"', resp.text)
            if links:
                unique = list(set(links))
                for link in unique:
                    print(f"  Found: {link}")
                    # Verify it works  
                    check = session.head(link, allow_redirects=True, timeout=10)
                    print(f"    Status: {check.status_code}")
            else:
                # Try to find any product links
                all_links = re.findall(r'href="(https?://kent\.ca/en/[a-z0-9-]+-\d{7}[^"]*)"', resp.text)
                if all_links:
                    print(f"  No exact match, but found products:")
                    for l in list(set(all_links))[:5]:
                        print(f"    {l}")
                else:
                    print(f"  No product links found in search results")
                    # Dump a snippet for debugging
                    if 'no results' in resp.text.lower() or 'no result' in resp.text.lower():
                        print("  Search returned no results")
        else:
            print(f"  Failed with status {resp.status_code}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # Also try common URL slug variations directly
    print(f"\n  Trying direct URL patterns...")
    
    # Pattern: try with just the SKU at the end
    test_urls = []
    if sku == '1058991':
        test_urls = [
            f"https://kent.ca/en/sico-pro-pva-primer-white-18-9-l-{sku}",
            f"https://kent.ca/en/sico-pro-pva-drywall-primer-white-18-9l-{sku}",
            f"https://kent.ca/en/sico-pva-primer-interior-white-18-9l-{sku}",
        ]
    elif sku == '1015669':
        test_urls = [
            f"https://kent.ca/en/sico-evolution-interior-eggshell-neutral-base-3-78l-{sku}-NEU",
            f"https://kent.ca/en/sico-evolution-interior-eggshell-pure-white-3-78l-{sku}-NEU",
            f"https://kent.ca/en/sico-evolution-eggshell-neutral-base-3-78-l-{sku}-NEU",
        ]
    elif sku == '1142112':
        test_urls = [
            f"https://kent.ca/en/clarovista-5mm-stone-core-vinyl-plank-aged-european-oak-{sku}-AEO",
            f"https://kent.ca/en/clarovista-stone-core-vinyl-plank-aged-european-oak-{sku}-AEO",
            f"https://kent.ca/en/clarovista-5-0mm-vinyl-plank-aged-european-oak-{sku}-AEO",
        ]
    elif sku == '1447728':
        test_urls = [
            f"https://kent.ca/en/1-2-x-3-1-2-x-96-modern-mdf-baseboard-primed-{sku}",
            f"https://kent.ca/en/alexandria-modern-mdf-baseboard-primed-valupak-{sku}",
            f"https://kent.ca/en/modern-mdf-baseboard-primed-valupak-{sku}",
        ]
    
    for test_url in test_urls:
        try:
            check = session.head(test_url, allow_redirects=True, timeout=10)
            final = check.url
            is_404 = check.status_code == 404 or '/404' in final
            status = "404" if is_404 else f"OK {check.status_code}"
            print(f"    {status} | {test_url}")
        except Exception as e:
            print(f"    ERR | {test_url} | {e}")
