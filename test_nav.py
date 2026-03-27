"""Verify nav consistency across all pages."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web.app import app

client = app.test_client()

for path in ['/', '/model', '/render', '/finishes']:
    resp = client.get(path)
    html = resp.data.decode()
    has_nav = 'class="site-nav"' in html
    has_bom = 'href="/"' in html and '>BOM<' in html
    has_model = 'href="/model"' in html
    has_render = 'href="/render"' in html
    has_finish = 'href="/finishes"' in html
    print(f"{path:15s}  nav={has_nav}  bom={has_bom}  model={has_model}  render={has_render}  finishes={has_finish}")
    # Check no old nav-pill remains
    if 'nav-pill' in html:
        print(f"  ⚠ OLD nav-pill found in {path}!")
    if 'Back to BOM' in html:
        print(f"  ⚠ OLD 'Back to BOM' found in {path}!")
