#!/usr/bin/env python3
"""Apply curated price updates to bom_data.py from scrape results.

This script applies ONLY verified price corrections where the Kent.ca
scraped price matches the SAME product + unit as what's in the BOM.
LOT/allowance items and unit-mismatched items are excluded.
"""
import re
import sys

BOM_FILE = "bom_data.py"

# ── Curated price updates ────────────────────────────────────────────────────
# (item_name_substring, old_price, new_price, notes)
# Only items where the Kent.ca per-unit price matches the BOM per-unit basis.

UPDATES = [
    # Division 2: Site Work
    ("XPS Rigid Insulation Under Slab", 45.00, 50.39, "SKU 1133346"),
    ("XPS Perimeter / Wing Insulation", 45.00, 50.39, "SKU 1133346"),
    ("10-mil Poly Vapour Barrier", 89.00, 112.50, "SKU 1028030"),

    # Division 3: Framing
    ("2×6×10", 8.82, 10.88, "SKU 1016313"),
    ("2×4×8", 3.98, 4.28, "SKU 1016318"),
    ("2×4×10", 6.38, 5.97, "SKU 1016338"),
    ("12×16", 55.13, 62.27, "SKU 1016290"),
    ("Spruce Plywood (wall sheathing)", 40.19, 39.98, "SKU 1015823"),
    ("Spruce Plywood (roof deck)", 51.22, 54.38, "SKU 1015826"),
    ("Spruce Plywood (subfloor", 60.26, 63.98, "SKU 1015824"),
    ("Pressure Treated 2×6 Sill", 14.00, 14.25, "SKU 1016514"),
    ("Framing Nails", 65.00, 74.99, "SKU 1006763"),
    ("PL Premium Construction Adhesive", 8.00, 16.99, "SKU 1030223"),

    # Division 4: Exterior Envelope
    ("Tyvek HomeWrap", 180.00, 129.99, "SKU 1021749"),
    ("Triple-Pane Vinyl Casement", 450.00, 431.10, "SKU 1107802"),
    ("Steel Insulated Entry Door", 593.99, 593.99, "SKU 1606274 — ALREADY CORRECT IF FIRST RUN APPLIED"),
    ("Window & Door Flashing Tape", 30.00, 47.39, "SKU 1005887"),

    # Division 5: Roofing
    ("IKO StormShield Ice & Water", 70.98, 84.99, "SKU 1026762"),
    ("Drip Edge 10'", 10.99, 8.29, "SKU 1021389"),
    ("Roof Vent / Exhaust Vents", 40.00, 17.59, "SKU 1021383"),
    ("Roofing Nails", 30.00, 78.69, "SKU 1052309"),

    # Division 6: Insulation
    ("R-20 Fiberglass Batt 23", 144.99, 137.00, "SKU 1024744"),
    ("R-28 Fiberglass Batt", 132.99, 126.00, "SKU 1024751"),
    ("R-31 Fiberglass Batt", 88.07, 79.99, "SKU 1024752"),
    ("6-mil Polyethylene Vapour Barrier", 60.00, 89.99, "SKU 1028019"),
    ("Roxul Safe'n'Sound", 50.00, 153.72, "SKU 1021690"),
    ("Great Stuff Gaps & Cracks", 13.99, 13.44, "SKU 1080226"),
    ("Tuck Tape", 10.00, 10.66, "SKU 1194944"),

    # Division 7: Interior Finishes
    ("Sico Pro PVA Drywall Primer", 84.00, 73.99, "SKU 1058991"),
    ("Volcano 5.3mm Pewter", 88.19, 74.96, "SKU 1080257-PWT"),
    ("Cement Backer Board", 30.00, 39.98, "SKU 1021605"),
    ("MDF Baseboard Valupak", 62.89, 59.87, "SKU 1447728"),
    ("Closet Shelving & Rods", 50.00, 232.99, "SKU 1032867"),

    # Division 8: Plumbing
    ("Matte Black Vanity with White", 549.00, 499.00, "SKU 1697660"),
    ("PEX Plumbing", 60.00, 44.89, "SKU 1036755 — 1/2 inch"),
    ("PEX Plumbing", 80.00, 39.98, "SKU 1013992 — 3/4 inch"),
    ("Washer Box", 50.00, 19.12, "SKU 1020149"),

    # Division 9: Electrical
    ("100A Sub-Panel", 250.00, 156.49, "SKU 1013553"),
    ("14/2 NMD90 Wire", 120.00, 163.00, "SKU 1026025"),
    ("12/2 NMD90 Wire", 150.00, 242.00, "SKU 1026699"),
    ("Receptacles — 15A Tamper", 3.00, 2.09, "SKU 1004457"),
    ("GFCI Receptacles — 20A", 25.00, 43.09, "SKU 1507459"),
    ("Smoke / CO Combination", 40.00, 139.00, "SKU 1661640"),
    ("Bathroom Exhaust Fans", 80.00, 69.99, "SKU 1685342"),
    ("Weatherproof Exterior Receptacle", 30.00, 33.59, "SKU 1026018"),

    # Division 11: Kitchen
    ("Apartment-Size Refrigerator", 1445.00, 1395.00, "SKU 1461451"),

    # Division 4 entry door — needs separate line since regex order matters
    ("Steel Insulated Entry Door", 450.00, 593.99, "SKU 1606274"),
]

# ── Pack restructures ────────────────────────────────────────────────────────
# These items are sold as multi-packs but priced individually in the BOM.
# Restructure to match Kent's actual product packaging.
PACK_RESTRUCTURES = [
    # (name_substr, old_qty, old_price, new_qty, new_unit, new_price, note)
    ("Light Switches", 10, 3.00, 1, "PK", 34.95,
     "Kent sells 10-pack (SKU 1029553). $34.95/pk vs old $30 total."),
    ("LED Slim Recessed Pot Lights", 12, 15.00, 1, "PK", 87.99,
     "Kent sells 12-pack (SKU 1519938). $87.99/pk vs old $180 total."),
]


def format_price(price):
    """Format price to match bom_data.py conventions (2 decimal places)."""
    return f"{price:.2f}"


def patch_price(src, name_substr, old_price, new_price):
    """Replace a unit_price in the item block containing name_substr."""
    # Handle both literal Unicode and \\u00d7 escapes in the source file
    escaped_name = re.escape(name_substr[:35])
    # Also allow \u00d7 for × and \u2014 for —
    escaped_name = escaped_name.replace(re.escape("×"), r"(?:×|\\u00d7)")
    escaped_name = escaped_name.replace(re.escape("—"), r"(?:—|\\u2014)")

    old_price_str = format_price(old_price)
    new_price_str = format_price(new_price)

    # Use (?:[^"\\]|\\.)* to match "name" fields that contain escaped quotes \"
    name_char = r'(?:[^"\\]|\\.)*'
    pattern = re.compile(
        r'("name":\s*"' + name_char + escaped_name + name_char + r'"'
        r'.*?'
        r'"unit_price":\s*)' + re.escape(old_price_str),
        re.DOTALL
    )
    new_src, n = pattern.subn(r'\g<1>' + new_price_str, src, count=1)
    return new_src, n


def patch_pack(src, name_substr, old_qty, old_price, new_qty, new_unit, new_price):
    """Restructure a pack item: change qty, unit, and price."""
    escaped_name = re.escape(name_substr[:35])
    escaped_name = escaped_name.replace(re.escape("×"), r"(?:×|\\u00d7)")
    escaped_name = escaped_name.replace(re.escape("—"), r"(?:—|\\u2014)")

    old_price_str = format_price(old_price)
    new_price_str = format_price(new_price)

    name_char = r'(?:[^"\\]|\\.)*'
    pattern = re.compile(
        r'("name":\s*"' + name_char + escaped_name + name_char + r'".*?)'
        r'"qty":\s*' + str(old_qty) + r'(.*?)'
        r'"unit_price":\s*' + re.escape(old_price_str),
        re.DOTALL
    )
    m = pattern.search(src)
    if not m:
        return src, 0

    block_start = m.start()
    block_end = m.end()
    old_block = src[block_start:block_end]

    new_block = old_block
    new_block = re.sub(r'"qty":\s*' + str(old_qty), f'"qty": {new_qty}', new_block)
    new_block = re.sub(r'"unit":\s*"EA"', f'"unit": "{new_unit}"', new_block)
    new_block = re.sub(
        r'"unit_price":\s*' + re.escape(old_price_str),
        f'"unit_price": {new_price_str}',
        new_block,
    )

    return src[:block_start] + new_block + src[block_end:], 1


def main():
    dry_run = "--dry-run" in sys.argv

    with open(BOM_FILE) as f:
        src = f.read()

    total_patched = 0
    failed = []

    print(f"Applying {len(UPDATES)} price updates + {len(PACK_RESTRUCTURES)} pack restructures\n")

    # Price updates
    for name, old, new, note in UPDATES:
        new_src, n = patch_price(src, name, old, new)
        if n > 0:
            diff = new - old
            print(f"  ✓ {name[:55]:<55} ${old:>9.2f} → ${new:>9.2f}  ({diff:+.2f})")
            src = new_src
            total_patched += 1
        else:
            failed.append((name, old, new, note))
            print(f"  ✗ FAILED: {name[:50]} (${old} not found near name)")

    # Pack restructures
    for name, old_q, old_p, new_q, new_u, new_p, note in PACK_RESTRUCTURES:
        new_src, n = patch_pack(src, name, old_q, old_p, new_q, new_u, new_p)
        if n > 0:
            print(f"  ✓ {name[:55]:<55} {old_q}×${old_p} → {new_q}×${new_p} ({new_u})")
            src = new_src
            total_patched += 1
        else:
            failed.append((name, old_p, new_p, note))
            print(f"  ✗ FAILED: {name[:50]} pack restructure")

    print(f"\n{'─' * 70}")
    print(f"Patched: {total_patched}")
    print(f"Failed:  {len(failed)}")

    if failed:
        print("\nFailed items:")
        for name, old, new, note in failed:
            print(f"  {name}: ${old} → ${new} ({note})")

    if dry_run:
        print("\n[DRY RUN — no file written]")
    elif total_patched > 0:
        with open(BOM_FILE, "w") as f:
            f.write(src)
        print(f"\n✅ Wrote {BOM_FILE}")

    # Calculate impact
    from bom_data import ALL_DIVISIONS
    print("\nReload bom_data to see new totals.")


if __name__ == "__main__":
    main()
