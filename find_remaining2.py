"""Find remaining hard-to-find items on Kent.ca sitemap."""
import requests, xml.etree.ElementTree as ET

r = requests.get('https://kent.ca/en/sitemap.xml', timeout=60)
root = ET.fromstring(r.content)
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [l.text for l in root.findall('.//s:loc', ns) if l.text]

print('=== EXTERIOR DOORS ===')
for u in urls:
    ul = u.lower()
    if ('6-panel' in ul or 'colonist' in ul or 'flush-steel' in ul or 'prehung' in ul or 'pre-hung' in ul) and ('door' in ul):
        print(u)

print('\n=== STEEL DOOR 36 ===')
for u in urls:
    ul = u.lower()
    if '36' in ul and ('steel' in ul) and ('x-79' in ul or 'x-80' in ul or 'door' in ul) and 'refrigerator' not in ul and 'french' not in ul and '/shop/' not in ul and 'roller' not in ul and 'guard' not in ul and 'sliding' not in ul and 'screen' not in ul:
        print(u)

print('\n=== ENTRY DOOR (full) ===')
for u in urls:
    ul = u.lower()
    if 'entry-door' in ul and '/shop/' not in ul:
        print(u)

print('\n=== EXTERIOR DOOR ===')
for u in urls:
    ul = u.lower()
    if 'exterior-door' in ul or 'exterior-steel' in ul:
        print(u)

print('\n=== ALUMINUM FASCIA ===')
for u in urls:
    ul = u.lower()
    if 'fascia' in ul and ('white' in ul or 'brown' in ul or 'black' in ul) and 'deckfast' not in ul and 'culture' not in ul:
        print(u)

print('\n=== INSULATED DUCT ===')
for u in urls:
    ul = u.lower()
    if 'insulated' in ul and 'duct' in ul:
        print(u)

print('\n=== FLEX DUCT ===')
for u in urls:
    ul = u.lower()
    if 'flex' in ul and 'duct' in ul:
        print(u)

print('\n=== 6 INCH DUCT ===')
for u in urls:
    ul = u.lower()
    if '6' in ul and 'duct' in ul and 'product' not in ul and 'shop' not in ul:
        print(u)
