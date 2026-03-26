"""Search Kent.ca GraphQL API for product URLs by SKU."""
import requests
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Store": "en",
})

graphql_url = "https://kent.ca/graphql"

skus = ["1058991", "1015669-NEU", "1142112-AEO", "1447728"]

for sku in skus:
    query = {
        "query": """
        {
          products(filter: { sku: { eq: "%s" } }) {
            items {
              name
              sku
              url_key
              url_suffix
              price_range {
                minimum_price {
                  regular_price { value currency }
                }
              }
            }
          }
        }
        """ % sku
    }
    try:
        r = session.post(graphql_url, json=query, timeout=15)
        print(f"SKU {sku}: status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("products", {}).get("items", [])
            if items:
                for item in items:
                    url_key = item.get("url_key", "")
                    suffix = item.get("url_suffix", "")
                    print(f"  Name: {item['name']}")
                    print(f"  URL: https://kent.ca/en/{url_key}{suffix}")
                    price = item.get("price_range", {}).get("minimum_price", {}).get("regular_price", {})
                    print(f"  Price: {price}")
            else:
                print(f"  No products found for this SKU")
        else:
            print(f"  Response: {r.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Also try without the suffix variants
print("=" * 50)
print("Trying base SKUs without suffixes...")
for sku in ["1058991", "1015669", "1142112", "1447728"]:
    query = {
        "query": """
        {
          products(filter: { sku: { eq: "%s" } }) {
            items {
              name
              sku
              url_key
              url_suffix
            }
          }
        }
        """ % sku
    }
    try:
        r = session.post(graphql_url, json=query, timeout=15)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("products", {}).get("items", [])
            if items:
                for item in items:
                    url_key = item.get("url_key", "")
                    suffix = item.get("url_suffix", "")
                    print(f"  SKU {sku}: {item['name']} -> https://kent.ca/en/{url_key}{suffix}")
            else:
                print(f"  SKU {sku}: not found")
        else:
            print(f"  SKU {sku}: status {r.status_code}")
    except Exception as e:
        print(f"  SKU {sku}: {e}")

# Also try a text search
print("\n" + "=" * 50)
print("Trying text search...")
for term in ["sico pva primer 18.9", "sico evolution eggshell", "clarovista vinyl plank", "alexandria baseboard valupak"]:
    query = {
        "query": """
        {
          products(search: "%s", pageSize: 3) {
            items {
              name
              sku
              url_key
              url_suffix
            }
          }
        }
        """ % term
    }
    try:
        r = session.post(graphql_url, json=query, timeout=15)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("products", {}).get("items", [])
            if items:
                for item in items:
                    url_key = item.get("url_key", "")
                    suffix = item.get("url_suffix", "")
                    print(f"  '{term}': {item['name']} (SKU: {item['sku']}) -> https://kent.ca/en/{url_key}{suffix}")
            else:
                print(f"  '{term}': no results")
        else:
            print(f"  '{term}': status {r.status_code}")
    except Exception as e:
        print(f"  '{term}': {e}")
