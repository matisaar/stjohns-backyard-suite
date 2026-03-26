"""Search Kent.ca sitemap for products matching BOM items without URLs."""
import requests
import re
import xml.etree.ElementTree as ET

# Keywords to search in the Kent.ca sitemap for each item
SEARCH_TERMS = {
    # Site Work & Foundation
    "xps rigid insulation": ["xps", "rigid", "insulation"],
    "poly vapour barrier": ["poly", "vapour", "barrier"],
    # Framing
    "pressure treated 2x6": ["pressure-treated", "2-x-6"],
    "simpson strong-tie": ["simpson", "strong-tie"],
    "framing nails 16d": ["framing-nail", "16d", "sinker"],
    "pl premium adhesive": ["pl-premium", "adhesive"],
    "construction screws": ["construction-screw"],
    # Exterior
    "tyvek homewrap": ["tyvek", "homewrap", "house-wrap"],
    "vinyl siding starter": ["starter-strip", "j-channel"],
    "fascia": ["aluminum-fascia", "fascia-trim"],
    "vinyl casement window": ["casement-window", "vinyl-window"],
    "steel entry door": ["steel-door", "entry-door", "insulated-door"],
    "flashing tape": ["flashing-tape"],
    "caulking sealant": ["caulking", "sealant", "sikaflex"],
    # Roofing
    "roof vent": ["roof-vent", "exhaust-vent", "maximum-vent"],
    "roofing nails coil": ["roofing-nail", "coil-nail"],
    # Insulation
    "polyethylene vapour": ["polyethylene", "vapour-barrier", "6-mil"],
    "roxul safensound": ["roxul", "safe-n-sound", "safe-and-sound", "rockwool", "safensound"],
    "great stuff foam": ["great-stuff", "spray-foam", "gap-filler"],
    "tuck tape": ["tuck-tape", "sheathing-tape", "red-tape"],
    # Interior Finishes
    "drywall tape corner bead": ["drywall-tape", "corner-bead"],
    "ceramic wall tile 12x24": ["ceramic-wall-tile", "12-x-24", "wall-tile"],
    "cement backer board": ["backer-board", "durock", "hardiebacker", "cement-board"],
    "thin-set mortar": ["thin-set", "mortar", "thinset"],
    "grout": ["grout", "tile-grout"],
    "pocket door": ["pocket-door"],
    # Plumbing
    "water heater 40": ["water-heater", "40-gallon", "electric-water"],
    "toilet dual flush": ["toilet", "dual-flush", "elongated"],
    "vanity 24": ["vanity", "24-inch", "matte-black-vanity"],
    "shower stall 32": ["shower-stall", "shower-kit", "acrylic-shower"],
    "shower valve matte black": ["shower-valve", "pressure-balance"],
    "undermount sink": ["undermount-sink", "stainless-steel-sink", "kitchen-sink"],
    "kitchen faucet matte black": ["kitchen-faucet", "pull-down-faucet", "matte-black-faucet"],
    "pex 1/2": ["pex", "1-2-x-100"],
    "pex 3/4": ["pex", "3-4-x-50"],
    "pex fittings": ["pex-fitting", "manifold", "sharkbite"],
    "abs drain pipe": ["abs-pipe", "abs-drain", "pvc-drain"],
    "washer box": ["washer-box", "washing-machine-box", "supply-box"],
    # Electrical
    "sub-panel 100a": ["sub-panel", "100-amp", "breaker-panel", "loadcentre"],
    "14/2 nmd90": ["14-2", "nmd90", "nmd-90"],
    "12/2 nmd90": ["12-2", "nmd90"],
    "10/3 nmd90": ["10-3", "nmd90"],
    "receptacle 15a": ["receptacle", "15-amp", "tamper-resistant"],
    "gfci 20a": ["gfci", "20-amp"],
    "light switch": ["light-switch", "single-pole", "3-way-switch", "decora"],
    "led recessed pot light": ["pot-light", "recessed-light", "slim-led", "4-inch"],
    "bathroom exhaust fan": ["exhaust-fan", "bath-fan", "80-cfm"],
    "smoke co detector": ["smoke-detector", "co-detector", "combination-alarm"],
    "electrical boxes": ["electrical-box", "device-box"],
    "weatherproof receptacle": ["weatherproof", "exterior-receptacle", "gfci-outdoor"],
    # HVAC
    "mini-split heat pump": ["mini-split", "ductless", "heat-pump", "18000-btu"],
    "baseboard heater": ["baseboard-heater", "electric-baseboard", "1500w"],
    "hrv heat recovery": ["hrv", "heat-recovery-ventilator"],
    # Kitchen
    "laminate countertop": ["laminate-countertop", "post-formed", "countertop"],
    "electric range 24": ["electric-range", "apartment-size", "24-inch-range"],
    "refrigerator 24": ["refrigerator", "apartment-size-fridge", "24-inch-fridge"],
    "range hood 24": ["range-hood", "under-cabinet"],
    # Laundry
    "stackable washer dryer": ["stackable", "washer-dryer", "compact-washer"],
    "dryer vent kit": ["dryer-vent", "vent-kit"],
    # Interior finish extras
    "closet shelving": ["closet-shelf", "closet-rod", "wire-shelf"],
    "pocket door pull": ["pocket-door-pull", "flush-pull", "privacy-lock"],
}

print("Downloading Kent.ca sitemap (15MB)...")
r = requests.get("https://kent.ca/en/sitemap.xml", timeout=60)
print(f"Downloaded: {len(r.content)} bytes, status {r.status_code}")

# Parse all URLs from sitemap
root = ET.fromstring(r.content)
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
all_urls = [loc.text for loc in root.findall('.//s:loc', ns) if loc.text]
print(f"Total sitemap URLs: {len(all_urls)}")

# Search for each item
print("\n=== SEARCH RESULTS ===\n")
found = {}
for item_key, keywords in SEARCH_TERMS.items():
    matches = []
    for url in all_urls:
        url_lower = url.lower()
        # Check if any keyword matches
        for kw in keywords:
            if kw.lower() in url_lower:
                matches.append(url)
                break
    
    if matches:
        # Deduplicate and pick best match (prefer shorter URLs, exact matches)
        unique = list(set(matches))
        unique.sort(key=len)
        found[item_key] = unique[:5]  # top 5
        print(f"✓ {item_key}")
        for u in unique[:5]:
            print(f"    {u}")
    else:
        print(f"✗ {item_key} — no matches")
    print()

print(f"\nFound matches for {len(found)}/{len(SEARCH_TERMS)} search terms")
