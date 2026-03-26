"""Search Kent.ca sitemap for remaining 20 items without URLs."""
import requests
import xml.etree.ElementTree as ET

print("Downloading Kent.ca sitemap...")
r = requests.get("https://kent.ca/en/sitemap.xml", timeout=60)
root = ET.fromstring(r.content)
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
all_urls = [loc.text for loc in root.findall('.//s:loc', ns) if loc.text]

def search(label, terms):
    results = []
    for url in all_urls:
        ul = url.lower()
        if all(t.lower() in ul for t in terms):
            results.append(url)
    results.sort(key=len)
    print(f"\n--- {label} ---")
    if results:
        for u in results[:6]:
            print(f"  {u}")
    else:
        print("  (none)")

# Gravel / aggregate
search("Gravel / crushed stone", ["gravel"])
search("Patio stone base", ["crush"])

# Rebar / wire mesh
search("Rebar", ["rebar"])
search("Wire mesh", ["wire", "mesh"])
search("Welded wire", ["welded"])

# Concrete / ready-mix
search("Concrete mix", ["concrete", "mix"])
search("Concrete bag", ["concrete"])

# Drain tile / weeping tile
search("Drain tile", ["drain", "tile", "pipe"])
search("Weeping tile", ["weeping"])
search("Filter fabric", ["filter", "fabric"])
search("Perforated drain pipe", ["perforated", "pipe"])
search("Landscape fabric", ["landscape", "fabric"])

# Engineered I-joist / TJI
search("I-joist", ["i-joist"])
search("TJI joist", ["tji"])
search("Engineered joist", ["engineered"])

# LVL beam
search("LVL beam", ["lvl"])
search("Laminated beam", ["laminated", "beam"])
search("Microllam", ["microllam"])

# Framing nails 3.25 / 16d
search("Framing nails 3", ["framing", "nail", "3"])
search("16d nails", ["16d"])
search("Framing nails bulk", ["framing", "nail"])

# Aluminum fascia
search("Aluminum fascia", ["aluminum", "fascia"])
search("Fascia cover", ["fascia"])
search("Metal fascia", ["metal", "fascia"])

# Triple-pane windows
search("Casement window 30", ["casement", "window", "30"])
search("Casement window", ["casement-window"])
search("Vision window", ["vision", "window"])

# Steel insulated entry door
search("Steel insulated door", ["steel", "insulated", "door"])
search("Steel entry door", ["steel", "entry"])
search("Pre-hung steel door", ["pre-hung", "door"])
search("36 steel door", ["36", "steel", "door"])

# HRV ducting
search("HRV duct", ["hrv", "duct"])
search("HRV filter", ["hrv", "filter"])
search("Flexible duct insulated", ["insulated", "flex", "duct"])
search("Flex duct 6", ["flex", "duct", "6"])
search("Duct grille", ["duct", "grille"])
