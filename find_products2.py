"""Second round: targeted sitemap search for items missed in first round."""
import requests
import xml.etree.ElementTree as ET

print("Downloading Kent.ca sitemap...")
r = requests.get("https://kent.ca/en/sitemap.xml", timeout=60)
root = ET.fromstring(r.content)
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
all_urls = [loc.text for loc in root.findall('.//s:loc', ns) if loc.text]

def search(label, terms):
    """Search sitemap for URLs containing ALL or ANY of the terms."""
    results = []
    for url in all_urls:
        ul = url.lower()
        # Must contain all terms
        if all(t.lower() in ul for t in terms):
            results.append(url)
    results.sort(key=len)
    print(f"\n--- {label} (all of: {terms}) ---")
    if results:
        for u in results[:8]:
            print(f"  {u}")
    else:
        print("  (none)")

# XPS insulation board
search("XPS insulation", ["xps"])
search("Rigid insulation foam", ["rigid", "foam"])
search("SM/Solex insulation board", ["insulation", "board"])
search("Styrofoam insulation", ["styrofoam"])

# Vapour barrier
search("Vapour barrier", ["vapour", "barrier"])
search("Poly sheeting", ["poly", "sheeting"])
search("Poly film", ["poly", "film"])
search("Poly 6 mil", ["6-mil"])

# Pressure treated lumber
search("PT 2x6", ["pressure", "treated"])

# Tyvek HomeWrap roll
search("Tyvek HomeWrap", ["tyvek", "home"])
search("House wrap", ["house", "wrap"])
search("Building wrap", ["building-wrap"])

# 12/2 NMD90 wire
search("12-2 NMD90 wire", ["12-2", "nmd"])
search("12/2 wire", ["12-2", "wire"])

# 10/3 NMD90 wire
search("10-3 NMD90 wire", ["10-3", "nmd"])
search("10/3 wire", ["10-3", "wire"])

# PEX pipe roll
search("PEX pipe 1/2 100", ["pex", "100"])
search("PEX pipe", ["pex", "pipe"])
search("PEX tubing", ["pex", "tub"])

# Smoke/CO detector
search("Smoke alarm", ["smoke", "alarm"])
search("Smoke detector", ["smoke", "detect"])
search("Carbon monoxide", ["carbon", "monoxide"])
search("CO alarm", ["co-alarm"])

# LED recessed/pot light 4"
search("Slim LED recessed", ["slim", "led"])
search("LED recessed", ["led", "recessed"])
search("Pot light 4", ["pot-light"])

# 24" appliances
search("24 inch range", ["24", "range", "electric"])
search("24 fridge/refrigerator", ["24", "refrigerator"])
search("Apartment range", ["apartment", "range"])
search("Compact fridge", ["compact", "refrigerator"])

# Mini split unit
search("Mini split 18000", ["mini-split", "18"])
search("Mini split unit", ["mini-split", "btu"])
search("Ductless", ["ductless"])

# Stackable washer dryer
search("Washer dryer", ["washer", "dryer"])
search("Compact washer", ["compact", "washer"])

# White ceramic tile 12x24
search("12x24 tile", ["12", "24", "tile"])
search("White wall tile", ["white", "wall", "tile"])
search("Ceramic tile large", ["ceramic", "tile"])

# Shower 32x32
search("32 shower", ["32", "shower"])
search("Acrylic shower base", ["acrylic", "shower"])

# Shower valve
search("Shower faucet", ["shower", "faucet"])
search("Shower valve", ["shower", "valve"])

# Water heater electric
search("Electric water heater", ["electric", "water", "heater"])
search("Water heater 40", ["water-heater"])
search("Giant water heater", ["giant", "water"])

# Toilet
search("Elongated toilet", ["elongated", "toilet"])
search("Dual flush toilet", ["dual", "flush", "toilet"])
search("One piece toilet", ["one-piece", "toilet"])

# 24 vanity
search("24 vanity", ["24", "vanity"])

# Laminate countertop kitchen
search("Laminate countertop", ["laminate", "countertop"])
search("Post-formed countertop", ["post-form"])
search("Kitchen countertop", ["kitchen", "countertop"])

# 24 range hood
search("24 range hood", ["24", "range-hood"])
search("Under cabinet range hood", ["under-cabinet", "range-hood"])

# Matte black faucet pulldown
search("Matte black kitchen faucet", ["matte", "black", "kitchen", "faucet"])
search("Black pulldown faucet", ["black", "pull"])

# Matte black door pull
search("Matte black flush pull", ["matte", "black", "flush"])
search("Black pocket door", ["black", "pocket"])
search("Privacy pocket lock", ["privacy", "pocket"])

# Closet wire shelf
search("Wire closet shelf", ["wire", "shelf", "closet"])
search("Closet organizer", ["closet", "organiz"])

# Simpson connector
search("Joist hanger", ["joist", "hanger"])
search("Hurricane tie", ["hurricane", "tie"])
search("Framing connector", ["framing", "connector"])
