"""Verify all 108 BOM URLs return HTTP 200."""
import requests
from bom_data import ALL_DIVISIONS

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
ok = 0
fail = 0
for d in ALL_DIVISIONS:
    for item in d["items"]:
        url = item.get("url", "")
        if not url:
            continue
        try:
            r = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                ok += 1
            else:
                fail += 1
                print(f"  {r.status_code} — {item['name']}: {url}")
        except Exception as e:
            fail += 1
            print(f"  ERROR — {item['name']}: {url} ({e})")

print(f"\n✅ {ok} OK | ❌ {fail} failed | Total: {ok + fail}")
