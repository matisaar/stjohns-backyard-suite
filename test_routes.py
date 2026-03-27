"""Quick route test — checks all pages render without errors."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web.app import app

client = app.test_client()

for path in ['/', '/model', '/render', '/finishes']:
    resp = client.get(path)
    status = '✓' if resp.status_code == 200 else '✗'
    print(f"  {status} {path:15s}  → {resp.status_code}  ({len(resp.data)} bytes)")

print("\nAll routes OK!" if all(
    client.get(p).status_code == 200
    for p in ['/', '/model', '/render', '/finishes']
) else "\n⚠ FAILURES detected")
