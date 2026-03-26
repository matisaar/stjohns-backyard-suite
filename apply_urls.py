"""Apply all found Kent.ca product URLs to bom_data.py items that are missing URLs."""
import re

KENT_BASE = "https://kent.ca/en"

# Mapping: item name substring → new URL
URL_MAP = {
    # Division 2 - Foundation
    "2\" XPS Rigid Insulation Under Slab": f"{KENT_BASE}/2-x-2-x-8-xps-60-insulation-1133346",
    "2\" XPS Perimeter / Wing": f"{KENT_BASE}/2-x-2-x-8-xps-60-insulation-1133346",

    # Division 3 - Framing
    "Pressure Treated 2×6 Sill": f"{KENT_BASE}/2-x-6-x-8-pressure-treated-lumber-1016514",
    "Simpson Strong-Tie Connectors": f"{KENT_BASE}/galvanized-hurricane-tie-1013127",
    "Construction Screws & Misc": f"{KENT_BASE}/construction-screws-8-x-2-1-2-1678499",
    "PL Premium Construction": f"{KENT_BASE}/pl-premium-max-1030223",

    # Division 4 - Exterior
    "Tyvek HomeWrap 9": f"{KENT_BASE}/tyvek-homewrap-100-x-9-house-wrap-1021749",
    "1.5\" XPS Rigid Exterior": f"{KENT_BASE}/sopra-xps-60-square-2-x-8-x-1-5-1694221",
    "Vinyl Siding Starter Strip": f"{KENT_BASE}/mitten-5-8-j-channel-12-1598067",
    "Window & Door Flashing Tape": f"{KENT_BASE}/dupont-flashing-tape-75-x-4-1005887",
    "Exterior Caulking & Sealants": f"{KENT_BASE}/quad-max-sealant-1045814",

    # Division 5 - Roofing
    "Roof Vent / Exhaust": f"{KENT_BASE}/duraflo-slantback-roof-vent-1021383",
    "Roofing Nails (coil": f"{KENT_BASE}/1-1-4-ring-shank-15-mini-coil-nails-1052309",

    # Division 6 - Insulation
    "6-mil Polyethylene Vapour": f"{KENT_BASE}/100-x-144-x-6-mil-clear-vapour-barrier-1200-sqft-1028019",
    "Roxul Safe'n'Sound": f"{KENT_BASE}/safe-n-sound-3-x-16-25-x-48-65-sqft-1021690",
    "Great Stuff Spray Foam": f"{KENT_BASE}/handi-foam-ii-605-insulating-spray-foam-sealant-1121865",
    "Tuck Tape (Red": f"{KENT_BASE}/tuck-tape-contractor-grade-sheathing-tape-red-60mm-x-55m-1194944",

    # Division 7 - Interior Finishes
    "Drywall Tape, Corner Bead": f"{KENT_BASE}/vinyl-corner-bead-1-1-4-x-8-1016873",
    'White Large-Format Ceramic Wall Tile 12"×24"': f"{KENT_BASE}/12-x-24-white-plane-glossy-linea-wall-tile-15-5-sqft-box-1035109",
    "Cement Backer Board": f"{KENT_BASE}/durock-1-2-x-3-x-5-cement-board-1021605",
    "Thin-Set Mortar, Grout": f"{KENT_BASE}/12-x24-artiquity-ceramic-tile-17-49-sf-bx-1397727",
    "Pocket Door Kit": f"{KENT_BASE}/pocket-door-30-pre-assembled-1389850",
    "Matte Black Pocket Door Pull": f"{KENT_BASE}/pocket-door-lock-round-privacy-1010873",
    "Closet Shelving & Rods": f"{KENT_BASE}/shelftrack-4-6-closet-organizer-kit-1032867",

    # Division 8 - Plumbing
    "40-Gallon Electric Water Heater": f"{KENT_BASE}/182l-6-1-year-electric-water-heater-1766016",
    "Modern White Elongated Toilet": f"{KENT_BASE}/tidal-3-5-4-8lpf-elongated-front-dual-flush-1-piece-toilet-1579329",
    '24" Modern Matte Black Vanity': f"{KENT_BASE}/24-vanity-with-drawer-1697660",
    'Shower Stall 32"×32"': f"{KENT_BASE}/finesse-4832-white-centre-drain-shower-base-1023986",
    "Matte Black Pressure-Balanced Shower": f"{KENT_BASE}/principals-shower-faucet-1202042",
    "Kitchen Sink — 25": f"{KENT_BASE}/single-bowl-undermount-sink-1391411",
    "Matte Black Single-Handle Pull-Down Kitchen": f"{KENT_BASE}/banting-pulldown-kitchen-faucet-matte-black-1199456",
    'PEX Plumbing — 1/2" × 100': f"{KENT_BASE}/super-pex-red-1-2-x-100-coil-1036755",
    'PEX Plumbing — 3/4" × 50': f"{KENT_BASE}/superpex-3-4-x-50-white-pex-pipe-1013992",
    "PEX Fittings, Manifold": f"{KENT_BASE}/1-2-x-3-4-pex-inlet-x-close-end-6-branch-manifold-1013949",
    "ABS/PVC Drain Pipe": f"{KENT_BASE}/3-abs-pipe-adapter-1001871",
    "Washer Box (hot/cold": f"{KENT_BASE}/washing-machine-box-1020149",

    # Division 9 - Electrical
    "100A Sub-Panel": f"{KENT_BASE}/100a-8-15-circuit-load-center-sub-panel-1013553",
    "14/2 NMD90 Wire": f"{KENT_BASE}/14-2-nmd90-75m-electrical-wire-blue-1026025",
    "12/2 NMD90 Wire": f"{KENT_BASE}/12-2-nmd90-75m-romex-simpull-electrical-wire-1026699",
    "10/3 NMD90 Wire": f"{KENT_BASE}/10-3-nmd90-75m-electrical-wire-orange-1026026",
    "Receptacles — 15A": f"{KENT_BASE}/15-a-duplex-receptacle-1004457",
    "GFCI Receptacles — 20A": f"{KENT_BASE}/tamper-resistant-gfci-20amp-1507459",
    "Light Switches (single": f"{KENT_BASE}/3-way-switch-10-pack-1029553",
    "LED Slim Recessed Pot Lights": f"{KENT_BASE}/4-led-recessed-pro-12-pack-1519938",
    "Bathroom Exhaust Fans": f"{KENT_BASE}/80-cfm-0-6-sone-bathroom-fan-1685342",
    "Smoke / CO Combination": f"{KENT_BASE}/hardwired-interconnected-combination-smoke-co-alarm-1661640",
    "Electrical Boxes, Connectors": f"{KENT_BASE}/device-box-6-pack-2-x-3-x-2-5-1111670",
    "Weatherproof Exterior": f"{KENT_BASE}/kraloy-pvc-2-gang-weatherproof-switch-gfci-cover-1026018",

    # Division 10 - HVAC
    "Ductless Mini-Split Heat Pump": f"{KENT_BASE}/18-000-btu-hyper-heat-ductless-mini-split-outdoor-1034429",
    "Electric Baseboard Heaters": f"{KENT_BASE}/baseboard-240v-1500w-66-1652016",
    "HRV — Heat Recovery": f"{KENT_BASE}/heat-recovery-ventilator-air-exchanger-1400849",

    # Division 11 - Kitchen
    "White Laminate Countertop": f"{KENT_BASE}/25-x-8-2300-kitchen-countertop-1015537",
    '24" Apartment-Size Electric Range': f"{KENT_BASE}/24-electric-range-upswept-spillguard-cooktop-1461599",
    '24" Apartment-Size Refrigerator': f"{KENT_BASE}/24-bottom-freezer-refrigerator-12-9cf-1461451",
    "Black Under-Cabinet Range Hood": f"{KENT_BASE}/500-series-24-under-cabinet-range-hood-stainless-steel-1462473",

    # Division 12 - Laundry
    "Stackable Washer/Dryer": f"{KENT_BASE}/stacked-washer-dryer-electric-laundry-center-1461896",
    "Dryer Vent Kit": f"{KENT_BASE}/dryer-vent-block-scalloped-with-sleeve-bulk-black-1420879",
}

# Read bom_data.py
with open("bom_data.py", "r") as f:
    content = f.read()

updated = 0
skipped = 0

for name_substr, new_url in URL_MAP.items():
    # Find the item block containing this name
    # Pattern: "name": "...name_substr...", followed eventually by "url": "..." or "url": None
    # We need to replace the url value
    
    # Escape special regex chars in name
    escaped = re.escape(name_substr)
    
    # Match the item's name line, then find the url line nearby (within ~5 lines)
    # Look for the url field that's currently empty string or None
    pattern = rf'("name":\s*"[^"]*{escaped}[^"]*".*?)"url":\s*(""|None)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        old_url_section = match.group(0)
        # Replace the url value
        new_url_section = re.sub(
            r'"url":\s*(""|None)',
            f'"url": f"{{KENT_BASE}}/{new_url.split("/en/", 1)[1]}"' if new_url.startswith("https://kent.ca/en/") else f'"url": "{new_url}"',
            old_url_section
        )
        content = content.replace(old_url_section, new_url_section, 1)
        updated += 1
        print(f"  ✓ {name_substr}")
    else:
        # Check if it already has a URL
        check = re.search(rf'"name":\s*"[^"]*{escaped}', content)
        if check:
            print(f"  ⊘ {name_substr} — already has URL or pattern mismatch")
            skipped += 1
        else:
            print(f"  ✗ {name_substr} — item not found")
            skipped += 1

# Write back
with open("bom_data.py", "w") as f:
    f.write(content)

print(f"\nDone: {updated} URLs added, {skipped} skipped")
