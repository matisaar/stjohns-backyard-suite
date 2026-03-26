"""Bill of Materials data for 430 sqft St. John's Backyard Suite.

This module contains:
1. The complete BOM with verified Kent.ca product links and prices
2. Quantity calculations based on the design spec
3. Cost summary with waste factor and HST

Design: 20' x 21.5' = 430 sqft, symmetrical, 2-bed / 2-bath / kitchen / laundry
        Mono-slope roof (8' low → 12' high), max 5m height
        2x6 wood frame, FPSF foundation, Zone 7A insulation
"""

# Kent.ca base URL
KENT_BASE = "https://kent.ca/en"

# Tax rate — Newfoundland & Labrador HST
NL_HST = 0.15

# Waste contingency
WASTE_FACTOR = 0.10


# ─── Division 1: General Requirements ────────────────────────────────────────

DIVISION_1 = {
    "name": "General Requirements",
    "items": [
        {
            "name": "Building Permit — City of St. John's",
            "qty": 1, "unit": "EA", "unit_price": 1500.00,
            "url": "https://www.stjohns.ca/en/building-development/permit-fees-and-rates.aspx",
            "notes": "~$10/$1k construction value + development charges. Call 709-576-8565 to confirm.",
        },
        {
            "name": "Engineered Drawings & Stamps",
            "qty": 1, "unit": "EA", "unit_price": 2500.00,
            "url": "https://pegnl.ca/",
            "notes": "PEGNL engineer ~$150-200/hr × 15-20 hrs. Typical $2k-4k for small residential.",
        },
        {
            "name": "Site Survey",
            "qty": 1, "unit": "EA", "unit_price": 500.00,
            "url": "https://www.anls.ca/",
            "notes": "ANLS surveyor, residential lot survey $300-800 in St. John's.",
        },
        {
            "name": "Portable Toilet Rental (3 months)",
            "qty": 1, "unit": "EA", "unit_price": 600.00,
            "url": "https://www.yellowpages.ca/search/si/1/Portable+Toilet+Rental/St+John%27s+NL",
            "notes": "~$175/mo + delivery/pickup. Industry avg $125-225/mo w/ weekly service.",
        },
        {
            "name": "Dumpster Rental (2 hauls)",
            "qty": 2, "unit": "EA", "unit_price": 500.00,
            "url": "https://www.yellowpages.ca/search/si/1/Waste+Bins+%26+Containers/St+John%27s+NL",
            "notes": "20-yard bin, $350-600/haul in Atlantic Canada incl disposal.",
        },
    ],
}


# ─── Division 2: Site Work & Foundation ───────────────────────────────────────

DIVISION_2 = {
    "name": "Site Work & Foundation",
    "items": [
        {
            "name": "Excavation (local contractor)",
            "qty": 430, "unit": "sqft", "unit_price": 8.00,
            "url": "https://www.yellowpages.ca/search/si/1/Excavation+Contractors/St+John%27s+NL",
            "notes": "Strip topsoil, excavate 18\" for FPSF. $6-12/sqft St. John's (rocky terrain).",
        },
        {
            "name": "4\" Gravel Base (3/4\" clear crush)",
            "qty": 16, "unit": "cu yd", "unit_price": 45.00,
            "url": f"{KENT_BASE}/3-4-gravel-bag-30-kg-1017010",
            "notes": "Compacted granular base under slab — local aggregate supplier",
            "image_url": "/static/images/1017010.jpg",
        },
        {
            "name": "2\" XPS Rigid Insulation Under Slab (R-10)",
            "qty": 14, "unit": "SH", "unit_price": 50.39,
            "url": f"{KENT_BASE}/2-x-2-x-8-xps-60-insulation-1133346",
            "notes": "4'x8' sheets, covers 430 sqft slab area (14 × 32 sqft = 448 sqft)",
            "image_url": "/static/images/1133346.jpg",
        },
        {
            "name": "2\" XPS Perimeter / Wing Insulation",
            "qty": 8, "unit": "SH", "unit_price": 50.39,
            "url": f"{KENT_BASE}/2-x-2-x-8-xps-60-insulation-1133346",
            "notes": "Frost-protected shallow foundation perimeter insulation",
            "image_url": "/static/images/1133346.jpg",
        },
        {
            "name": "10-mil Poly Vapour Barrier (under slab)",
            "qty": 1, "unit": "RL", "unit_price": 112.50,
            "url": f"{KENT_BASE}/100-x-240-x-6-mil-clear-vapour-barrier-2000-sqft-1028030",
            "notes": "20'x50' roll, moisture barrier under concrete slab",
            "image_url": "/static/images/1028030.jpg",
        },
        {
            "name": "Concrete — 4\" Slab + Thickened Edges",
            "qty": 5.5, "unit": "cu m", "unit_price": 250.00,
            "url": f"{KENT_BASE}/80-lb-bag-concrete-mix-1022011",
            "notes": "Ready-mix delivery, 25 MPa. ~5.5 m³ for 430 sqft × 4\" + 12\" thickened edge perimeter",
            "image_url": "/static/images/1022011.jpg",
        },
        {
            "name": "Rebar / Welded Wire Mesh",
            "qty": 430, "unit": "sqft", "unit_price": 0.75,
            "url": f"{KENT_BASE}/reinforced-wire-mesh-6-x-6-x-4-x-8-1015819",
            "notes": "6×6 W2.9×W2.9 mesh over full slab, rebar in thickened edges",
            "image_url": "/static/images/1015819.jpg",
        },
        {
            "name": "Perimeter Drain Tile + Filter Fabric + Gravel",
            "qty": 80, "unit": "LF", "unit_price": 3.00,
            "url": f"{KENT_BASE}/4-x-10-275-kpa-pvc-perforated-sewer-pipe-1014140",
            "notes": "4\" perforated pipe around foundation perimeter to daylight / sump",
            "image_url": "/static/images/1014140.jpg",
        },
        {
            "name": "Backfill & Final Grading (allowance)",
            "qty": 1, "unit": "EA", "unit_price": 500.00,
            "url": "https://www.yellowpages.ca/search/si/1/Excavation+Contractors/St+John%27s+NL",
            "notes": "Machine backfill + grade for drainage. Typical $300-800 small site.",
        },
    ],
}


# ─── Division 3: Framing ─────────────────────────────────────────────────────

DIVISION_3 = {
    "name": "Framing",
    "items": [
        {
            "name": "2×6×8' SPF Stud Kiln Dried (exterior walls)",
            "qty": 120, "unit": "EA", "unit_price": 6.48,
            "url": f"{KENT_BASE}/2-x-6-x-8-spf-stud-kiln-dried-1016278",
            "notes": "Exterior walls @ 16\" OC. Perimeter ~82 LF ÷ 1.33 = 62 + corners/headers/extras = ~120",
            "sku": "1016278",
            "image_url": "/static/images/1016278.jpg",
        },
        {
            "name": "2×6×10' SPF #2 & Better KD (headers, corners)",
            "qty": 20, "unit": "EA", "unit_price": 10.88,
            "url": f"{KENT_BASE}/2-x-6-x-10-2-better-spf-lumber-kiln-dried-1016313",
            "notes": "Built-up headers over windows/doors, corner assemblies",
            "sku": "1016313",
            "image_url": "/static/images/1016313.jpg",
        },
        {
            "name": "2×4×8' SPF Stud Kiln Dried (interior partitions)",
            "qty": 60, "unit": "EA", "unit_price": 4.28,
            "url": f"{KENT_BASE}/2-x-4-x-8-spf-stud-kiln-dried-1016318",
            "notes": "Interior walls: 2 bathroom walls + 2 bedroom walls + kitchen partition ≈60 LF / 1.33 = 45 + extras",
            "sku": "1016318",
            "image_url": "/static/images/1016318.jpg",
        },
        {
            "name": "2×4×12' SPF #2 & Better KD (misc framing)",
            "qty": 20, "unit": "EA", "unit_price": 7.66,
            "url": f"{KENT_BASE}/2-x-4-x-12-2-better-spf-lumber-kiln-dried-1016339",
            "notes": "Blocking, backing, cripples, misc framing needs",
            "sku": "1016339",
            "image_url": "/static/images/1016339.jpg",
        },
        {
            "name": "2×4×10' SPF #2 & Better KD",
            "qty": 12, "unit": "EA", "unit_price": 5.97,
            "url": f"{KENT_BASE}/2-x-4-x-10-2-better-spf-lumber-kiln-dried-1016338",
            "notes": "Top plates (doubled), additional blocking",
            "sku": "1016338",
            "image_url": "/static/images/1016338.jpg",
        },
        {
            "name": "2\u00d712\u00d716' SPF #2 & Better KD (roof rafters)",
            "qty": 24, "unit": "EA", "unit_price": 62.27,
            "url": f"{KENT_BASE}/2-x-12-x-16-2-better-spf-lumber-kiln-dried-1016290",
            "sku": "1016290",
            "notes": "Mono-slope roof rafters 16\" OC, 20' span w/ mid-span LVL beam support.",
        },
        {
            "name": "LVL Beam 1.75\u00d79.5\" (built-up header/ridge)",
            "qty": 3, "unit": "EA", "unit_price": 150.00,
            "url": f"{KENT_BASE}/search?q=lvl+beam",
            "notes": "Kent special order desk. 2 headers + 1 mid-span ridge beam. ~$8-12/LF typical.",
        },
        {
            "name": "1/2\" × 4' × 8' Spruce Plywood (wall sheathing)",
            "qty": 30, "unit": "SH", "unit_price": 39.98,
            "url": f"{KENT_BASE}/1-2-x-4-x-8-12-5mm-spruce-plywood-standard-1015823",
            "notes": "Exterior wall sheathing: ~82 LF perimeter × 8' H = 656 sqft ÷ 32 = ~21 sheets + gable ends = 30",
            "sku": "1015823",
            "image_url": "/static/images/1015823.jpg",
        },
        {
            "name": "5/8\" × 4' × 8' Spruce Plywood (roof deck)",
            "qty": 18, "unit": "SH", "unit_price": 54.38,
            "url": f"{KENT_BASE}/5-8-4-x-8-15-5mm-spruce-plywood-standard-1015826",
            "notes": "Roof sheathing: 430 sqft + slope factor + 2' overhang = ~530 sqft ÷ 32 = 17 sheets → 18",
            "sku": "1015826",
            "image_url": "/static/images/1015826.jpg",
        },
        {
            "name": "3/4\" × 4' × 8' Spruce Plywood (subfloor — if raised)",
            "qty": 0, "unit": "SH", "unit_price": 63.98,
            "url": f"{KENT_BASE}/3-4-x-4-x-8-18-5mm-spruce-plywood-standard-1015824",
            "notes": "NOT NEEDED for slab-on-grade. Included at qty=0 as reference for future scope change.",
            "image_url": "/static/images/1015824.jpg",
            "sku": "1015824",
        },
        {
            "name": "Pressure Treated 2×6 Sill Plates",
            "qty": 12, "unit": "EA", "unit_price": 14.25,
            "url": f"{KENT_BASE}/2-x-6-x-8-pressure-treated-lumber-1016514",
            "notes": "Bottom plates on concrete — must be pressure treated. ~82 LF = 12 × 8' pieces",
            "image_url": "/static/images/1016514.jpg",
        },
        {
            "name": "Simpson Strong-Tie Connectors & Hardware",
            "qty": 1, "unit": "LOT", "unit_price": 400.00,
            "url": f"{KENT_BASE}/galvanized-hurricane-tie-1013127",
            "notes": "Hurricane ties, joist hangers, post bases, hold-downs per engineered design",
            "image_url": "/static/images/1013127.jpg",
        },
        {
            "name": "Framing Nails — 3.25\" (16d sinker, 50 lb)",
            "qty": 2, "unit": "BX", "unit_price": 74.99,
            "url": f"{KENT_BASE}/3-1-4-prostrip-framing-nail-3000-box-1006763",
            "notes": "~100 lbs total for wall and roof framing",
            "image_url": "/static/images/1006763.jpg",
        },
        {
            "name": "Construction Screws & Misc Fasteners",
            "qty": 1, "unit": "LOT", "unit_price": 200.00,
            "url": f"{KENT_BASE}/construction-screws-8-x-2-1-2-1678499",
            "notes": "Deck screws, structural screws, lag bolts, anchor bolts, misc",
            "image_url": "/static/images/1678499.jpg",
        },
        {
            "name": "PL Premium Construction Adhesive",
            "qty": 10, "unit": "EA", "unit_price": 16.99,
            "url": f"{KENT_BASE}/pl-premium-max-1030223",
            "notes": "Subfloor/sheathing adhesive — glue-and-screw for rigidity",
            "image_url": "/static/images/1030223.jpg",
        },
    ],
}


# ─── Division 4: Exterior Envelope ───────────────────────────────────────────

DIVISION_4 = {
    "name": "Exterior Envelope",
    "items": [
        {
            "name": "Tyvek HomeWrap 9' × 100'",
            "qty": 2, "unit": "RL", "unit_price": 129.99,
            "url": f"{KENT_BASE}/tyvek-homewrap-100-x-9-house-wrap-1021749",
            "notes": "Weather-resistant barrier over wall sheathing. 2 rolls covers ~1,800 sqft (need ~700 sqft + overlaps)",
            "image_url": "/static/images/1021749.jpg",
        },
        {
            "name": "1.5\" XPS Rigid Exterior Continuous Insulation (R-7.5)",
            "qty": 30, "unit": "SH", "unit_price": 40.00,
            "url": f"{KENT_BASE}/sopra-xps-60-square-2-x-8-x-1-5-1694221",
            "notes": "4'x8' sheets over Tyvek. Brings wall to R-24 effective (R-20 batt + R-7.5 continuous). 30 × 32 = 960 sqft",
            "image_url": "/static/images/1694221.jpg",
        },
        {
            "name": "Mitten Oregon Pride Dutchlap Vinyl Siding (12'1\")",
            "qty": 50, "unit": "EA", "unit_price": 11.19,
            "url": f"{KENT_BASE}/oregon-pride-double-4-5-dutchlap-siding-1010820",
            "notes": "Exterior cladding — 50 pieces × ~9 sqft exposed = 450 sqft coverage (wall area ~650 sqft, minus windows/door)",
            "sku": "1010820",
            "image_url": "/static/images/1010820.jpg",
        },
        {
            "name": "Vinyl Siding Starter Strip, J-Channel, Corners",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/mitten-5-8-j-channel-12-1598067",
            "notes": "Starter strip ~82 LF, J-channel around 6 windows + 1 door, 4 outside corners, 2 inside corners",
            "image_url": "/static/images/1598067.jpg",
        },
        {
            "name": "Double 5\" Perforated Soffit (12' pieces)",
            "qty": 16, "unit": "EA", "unit_price": 12.42,
            "url": f"{KENT_BASE}/double-5-perforated-soffit-standard-1021390",
            "notes": "Soffit for 2' overhang on all sides: (82 LF perimeter × 2' ÷ ~10 sqft per piece = ~16 pcs)",
            "sku": "1021390",
            "image_url": "/static/images/1021390.jpg",
        },
        {
            "name": "Aluminum Fascia & Trim",
            "qty": 7, "unit": "EA", "unit_price": 20.39,
            "url": f"{KENT_BASE}/8-x-12-fascia-frost-white-1016978",
            "sku": "1016978",
            "notes": "8\" × 12' vinyl fascia, Frost White. 7 pcs × 12' = 84 LF (covers 82 LF perimeter + gable rake).",
            "image_url": "/static/images/1016978.jpg",
        },
        {
            "name": "Triple-Pane Vinyl Casement Windows (~30\"×48\")",
            "qty": 6, "unit": "EA", "unit_price": 431.10,
            "url": f"{KENT_BASE}/36-x-40-vision-left-hand-casement-window-1107802",
            "notes": "6 windows: 2 bedrooms (egress-sized, min 3.8 sqft openable), 2 bathrooms (small), 2 kitchen. Get local quotes from Kohltech or JELD-WEN NL dealers for triple-pane.",
            "image_url": "/static/images/1107802.jpg",
        },
        {
            "name": "Steel Insulated Entry Door — 36\" Black with Frame",
            "qty": 1, "unit": "EA", "unit_price": 593.99,
            "url": f"{KENT_BASE}/36-x80-6-panel-vinyl-clad-inswing-door-4-5-8-pvc-sill-1606274",
            "notes": "Pre-hung insulated steel door, black exterior finish. Modern B&W aesthetic. Single entrance.",
            "image_url": "/static/images/1606274.jpg",
        },
        {
            "name": "Window & Door Flashing Tape",
            "qty": 2, "unit": "RL", "unit_price": 47.39,
            "url": f"{KENT_BASE}/dupont-flashing-tape-75-x-4-1005887",
            "notes": "Self-adhering membrane flashing, 4\" × 75' — flash all window and door rough openings",
            "image_url": "/static/images/1005887.jpg",
        },
        {
            "name": "Exterior Caulking & Sealants",
            "qty": 1, "unit": "LOT", "unit_price": 100.00,
            "url": f"{KENT_BASE}/quad-max-sealant-1045814",
            "notes": "Polyurethane sealant for all exterior penetrations, window perimeters, siding joints",
            "image_url": "/static/images/1045814.jpg",
        },
    ],
}


# ─── Division 5: Roofing ─────────────────────────────────────────────────────

DIVISION_5 = {
    "name": "Roofing",
    "items": [
        {
            "name": "IKO Cambridge Architectural Shingles (Dual Black)",
            "qty": 16, "unit": "BD", "unit_price": 42.99,
            "url": f"{KENT_BASE}/40-7-8-x-13-3-4-cambridge-shingle-1010785",
            "notes": "~530 sqft roof area ÷ 33.3 sqft/bundle = 16 bundles (~5 squares). Architectural style, 30-yr warranty.",
            "sku": "1010785",
            "image_url": "/static/images/1010785.jpg",
        },
        {
            "name": "IKO StormShield Ice & Water Protector 36\"×65'",
            "qty": 2, "unit": "RL", "unit_price": 84.99,
            "url": f"{KENT_BASE}/stormshield-ice-water-protector-36-x-65-1026762",
            "notes": "Full coverage on mono-slope roof at 3:12 pitch recommended in NL. 2 rolls = 390 sqft. May need 3 for full coverage.",
            "sku": "1026762",
            "image_url": "/static/images/1026762.jpg",
        },
        {
            "name": "Organic Felt Underlayment 36\"×131'",
            "qty": 1, "unit": "RL", "unit_price": 44.99,
            "url": f"{KENT_BASE}/organic-fibers-black-saturated-felt-roofing-36-x-131-1026830",
            "notes": "#15 felt over remaining roof area not covered by ice & water shield",
            "sku": "1026830",
            "image_url": "/static/images/1026830.jpg",
        },
        {
            "name": "Drip Edge 10' (Pebble)",
            "qty": 12, "unit": "EA", "unit_price": 8.29,
            "url": f"{KENT_BASE}/10-x-2-1-2-x-1-roof-edge-drip-cap-1021389",
            "notes": "Full perimeter of roof: ~82 LF + 2 × 22' rakes = 126 LF → 13 pieces, use 12 + offcuts",
            "sku": "1021389",
            "image_url": "/static/images/1021389.jpg",
        },
        {
            "name": "Step Flashing 4\"×4\"×8\"",
            "qty": 20, "unit": "EA", "unit_price": 3.49,
            "url": f"{KENT_BASE}/step-flashing-4-x-4-x-8-1016918",
            "notes": "Where roof meets any wall projections or penetrations",
            "sku": "1016918",
            "image_url": "/static/images/1016918.jpg",
        },
        {
            "name": "Roof Vent / Exhaust Vents",
            "qty": 2, "unit": "EA", "unit_price": 17.59,
            "url": f"{KENT_BASE}/duraflo-slantback-roof-vent-1021383",
            "notes": "Static roof vents or ridge vent for attic ventilation. Required for shingle warranty.",
            "image_url": "/static/images/1021383.jpg",
        },
        {
            "name": "Thermocell Air Chutes 22.5\"×27\"",
            "qty": 20, "unit": "EA", "unit_price": 2.19,
            "url": f"{KENT_BASE}/thermocell-air-chutes-22-5-x-27-max-r-value-r36-1042887",
            "notes": "Maintain airflow between insulation and roof deck in each rafter bay",
            "sku": "1042887",
            "image_url": "/static/images/1042887.jpg",
        },
        {
            "name": "Roofing Nails (coil, 1-1/4\")",
            "qty": 2, "unit": "BX", "unit_price": 78.69,
            "url": f"{KENT_BASE}/1-1-4-ring-shank-15-mini-coil-nails-1052309",
            "notes": "Galvanized roofing nails for shingle and underlayment",
            "image_url": "/static/images/1052309.jpg",
        },
    ],
}


# ─── Division 6: Insulation & Air Barrier ─────────────────────────────────────

DIVISION_6 = {
    "name": "Insulation & Air Barrier",
    "items": [
        {
            "name": "Owens Corning R-20 Fiberglass Batt 15\" (78.3 sqft/bag)",
            "qty": 10, "unit": "BG", "unit_price": 93.99,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r20-47-x-15-x-6-78-3-sqft-1024741",
            "notes": "Exterior wall cavities: ~650 sqft net wall area ÷ 78.3 = 8.3 bags + 15% waste = 10 bags",
            "sku": "1024741",
            "image_url": "/static/images/1024741.jpg",
        },
        {
            "name": "Owens Corning R-20 Fiberglass Batt 23\" (120.1 sqft/bag)",
            "qty": 2, "unit": "BG", "unit_price": 137.00,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r20-47-x-23-x-6-120-1-sqft-1024744",
            "notes": "24\" OC areas if any, or for wider bays. 2 bags supplementary.",
            "sku": "1024744",
            "image_url": "/static/images/1024744.jpg",
        },
        {
            "name": "Owens Corning R-28 Fiberglass Batt 24\" (80 sqft/bag)",
            "qty": 6, "unit": "BG", "unit_price": 126.00,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r28-48-x-24-x-8-1-2-80-sqft-1024751",
            "notes": "Ceiling / roof cavity — first layer. 6 × 80 = 480 sqft covers full ceiling.",
            "sku": "1024751",
            "image_url": "/static/images/1024751.jpg",
        },
        {
            "name": "Owens Corning R-31 Fiberglass Batt 16\" (42.7 sqft/bag)",
            "qty": 4, "unit": "BG", "unit_price": 79.99,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r31-48-x-16-x-9-1-2-42-7-sqft-1024752",
            "notes": "Ceiling top-up layer to achieve effective R-50+. 4 × 42.7 = 171 sqft (supplement where depth allows).",
            "sku": "1024752",
            "image_url": "/static/images/1024752.jpg",
        },
        {
            "name": "6-mil Polyethylene Vapour Barrier",
            "qty": 2, "unit": "RL", "unit_price": 89.99,
            "url": f"{KENT_BASE}/100-x-144-x-6-mil-clear-vapour-barrier-1200-sqft-1028019",
            "notes": "Interior side of walls and ceiling — continuous air/vapour barrier per NBC. 10'×100' rolls.",
            "image_url": "/static/images/1028019.jpg",
        },
        {
            "name": "Roxul Safe'n'Sound Acoustic Batt (bathroom walls)",
            "qty": 3, "unit": "BG", "unit_price": 153.72,
            "url": f"{KENT_BASE}/safe-n-sound-3-x-16-25-x-48-65-sqft-1021690",
            "notes": "Sound insulation in shared bathroom/bedroom partition walls — mineral wool batts",
            "image_url": "/static/images/1021690.jpg",
        },
        {
            "name": "Great Stuff Gaps & Cracks Foam Sealant 12oz",
            "qty": 6, "unit": "EA", "unit_price": 13.44,
            "url": f"{KENT_BASE}/great-stuff-gaps-cracks-smart-dispenser-foam-sealant-12oz-1080226",
            "sku": "1080226",
            "notes": "Smart Dispenser spray foam — seal pipes, wires, rim joists, sill plate to slab.",
        },
        {
            "name": "Tuck Tape (Red Sheathing Tape)",
            "qty": 4, "unit": "RL", "unit_price": 10.66,
            "url": f"{KENT_BASE}/tuck-tape-contractor-grade-sheathing-tape-red-60mm-x-55m-1194944",
            "notes": "Seal all poly seams, sheathing joints. 60mm × 66m rolls.",
            "image_url": "/static/images/1194944.jpg",
        },
    ],
}


# ─── Division 7: Interior Finishes ────────────────────────────────────────────

DIVISION_7 = {
    "name": "Interior Finishes",
    "items": [
        {
            "name": "CGC 1/2\" × 4' × 8' UltraLight Drywall",
            "qty": 45, "unit": "SH", "unit_price": 17.82,
            "url": f"{KENT_BASE}/drywall-1-2-x-4-x-8-ultra-light-panel-1016148",
            "notes": "Walls + ceilings: ~1,600 sqft walls + 430 sqft ceiling = 2,030 sqft ÷ 32 = 63 sheets. 45 for walls, rest for ceiling.",
            "sku": "1016148",
            "image_url": "/static/images/1016148.jpg",
        },
        {
            "name": "CGC 1/2\" × 4' × 12' Tapered Edge Drywall",
            "qty": 12, "unit": "SH", "unit_price": 26.73,
            "url": f"{KENT_BASE}/drywall-1-2-x-4-x-12-tapered-edge-panel-1016149",
            "notes": "Ceiling panels — 12' length reduces joints. 12 × 48 sqft = 576 sqft (ceiling 430 sqft + waste).",
            "sku": "1016149",
            "image_url": "/static/images/1016149.jpg",
        },
        {
            "name": "CGC 5/8\" × 4' × 8' Type X Firecode Drywall",
            "qty": 4, "unit": "SH", "unit_price": 31.99,
            "url": f"{KENT_BASE}/drywall-firecode-5-8-x-4-x-8-type-x-panel-1016160",
            "notes": "Fire-rated drywall for furnace/utility areas or where required by code.",
            "sku": "1016160",
            "image_url": "/static/images/1016160.jpg",
        },
        {
            "name": "CGC 17L All-Purpose Lite Drywall Compound",
            "qty": 3, "unit": "EA", "unit_price": 32.87,
            "url": f"{KENT_BASE}/17-l-sheetrock-all-purpose-lite-drywall-compound-white-1021974",
            "notes": "3-coat system: tape coat, fill coat, finish coat.",
            "image_url": "/static/images/1021974.jpg",
            "sku": "1021974",
        },
        {
            "name": "Drywall Tape, Corner Bead, Screws Lot",
            "qty": 1, "unit": "LOT", "unit_price": 100.00,
            "url": f"{KENT_BASE}/vinyl-corner-bead-1-1-4-x-8-1016873",
            "notes": "Paper tape, vinyl corner bead, 1-1/4\" drywall screws, sandpaper",
            "image_url": "/static/images/1016873.jpg",
        },
        {
            "name": "Sico Pro PVA Drywall Primer White 18.9L",
            "qty": 1, "unit": "EA", "unit_price": 73.99,
            "url": f"{KENT_BASE}/sico-pro-pva-primer-white-18-9l-1058991",
            "sku": "1058991",
            "image_url": "/static/images/1058991.jpg",
            "notes": "White PVA primer — one coat all new drywall. ~1,800 sqft coverage per pail.",
        },
        {
            "name": "Sico Evolution Interior Eggshell Pure White 3.78L",
            "qty": 6, "unit": "EA", "unit_price": 68.99,
            "url": f"{KENT_BASE}/evolution-3-78-l-interior-eggshell-neutral-base-1015669-neu",
            "sku": "1015669-NEU",
            "image_url": "/static/images/1015669-NEU.jpg",
            "notes": "Bright white walls throughout — modern B&W aesthetic. 6 cans × 400 sqft = 2,400 sqft (2 coats on ~1,200 sqft).",
        },
        {
            "name": "Volcano 5.3mm Pewter Engineered Stone Core Vinyl Plank",
            "qty": 22, "unit": "BX", "unit_price": 74.96,
            "url": f"{KENT_BASE}/5-3mm-volcano-pewter-engineered-stone-core-vinyl-23-33-sf-1080257-pwt",
            "sku": "1080257-PWT",
            "image_url": "/static/images/1080257-PWT.jpg",
            "notes": "Dark walnut Pewter LVP — 23.33 sqft/box × 22 = 513 sqft (430 + 19% waste). Waterproof click-lock throughout.",
        },
        {
            "name": "White Large-Format Ceramic Wall Tile 12\"×24\" (shower walls)",
            "qty": 130, "unit": "sqft", "unit_price": 4.00,
            "url": f"{KENT_BASE}/12-x-24-white-plane-glossy-linea-wall-tile-15-5-sqft-box-1035109",
            "notes": "2 shower surrounds × ~65 sqft each. White 12×24 tile — modern B&W aesthetic contrast with dark floor.",
            "image_url": "/static/images/1035109.jpg",
        },
        {
            "name": "Cement Backer Board (Durock / HardieBacker)",
            "qty": 8, "unit": "SH", "unit_price": 39.98,
            "url": f"{KENT_BASE}/durock-1-2-x-3-x-5-cement-board-1021605",
            "notes": "1/2\" × 3' × 5' cement board behind all tiled shower areas — moisture-proof substrate.",
            "image_url": "/static/images/1021605.jpg",
        },
        {
            "name": "Thin-Set Mortar, Grout, Tile Trim",
            "qty": 1, "unit": "LOT", "unit_price": 144.00,
            "url": f"{KENT_BASE}/ultraflex-lht-mortar-22-7kg-1531122",
            "notes": "2× Mapei Ultraflex LHT 22.7kg (1531122) $29.81 + Flexcolor CQ grout (1015090) $62.84 + 2× Schluter Jolly 3/8\" PVC (1082329) $8.69 + spacers $2.99.",
        },
        {
            "name": "Alexandria 1/2\"×3-1/2\"×96\" Modern MDF Baseboard Valupak (10-pack)",
            "qty": 3, "unit": "PK", "unit_price": 59.87,
            "url": f"{KENT_BASE}/1-2-x-3-1-2-x-8-modern-mdf-baseboard-valupak-10-pack-1447728",
            "sku": "1447728",
            "image_url": "/static/images/1447728.jpg",
            "notes": "Clean modern profile, pre-primed white. 10×8' per pack = 80 LF × 3 packs = 240 LF (covers 200 LF + waste).",
        },
        {
            "name": "Pocket Door Kit — 30\" Modern White",
            "qty": 4, "unit": "EA", "unit_price": 159.00,
            "url": f"{KENT_BASE}/pocket-door-30-pre-assembled-1389850",
            "notes": "4 pocket doors: 2 bedrooms + 2 bathrooms. White flat-panel slab with matte black flush pulls.",
            "image_url": "/static/images/1389850.jpg",
        },
        {
            "name": "Matte Black Pocket Door Pull Sets (privacy + passage)",
            "qty": 4, "unit": "EA", "unit_price": 19.80,
            "url": f"{KENT_BASE}/pocket-door-lock-round-privacy-1010873",
            "notes": "2 privacy (bath) + 2 passage (bedroom). Matte black flush pulls — B&W modern theme.",
            "image_url": "/static/images/1010873.jpg",
        },
        {
            "name": "Closet Shelving & Rods",
            "qty": 2, "unit": "EA", "unit_price": 232.99,
            "url": f"{KENT_BASE}/shelftrack-4-6-closet-organizer-kit-1032867",
            "notes": "Wire shelf + rod kit per bedroom closet. ~4' wide each.",
            "image_url": "/static/images/1032867.jpg",
        },
    ],
}


# ─── Division 8: Plumbing ────────────────────────────────────────────────────

DIVISION_8 = {
    "name": "Plumbing",
    "items": [
        {
            "name": "40-Gallon Electric Water Heater",
            "qty": 1, "unit": "EA", "unit_price": 595.00,
            "url": f"{KENT_BASE}/182l-6-1-year-electric-water-heater-1766016",
            "notes": "Standard electric tank water heater. Adequate for 2-person suite. NL electricity is cheap.",
            "image_url": "/static/images/1766016.jpg",
        },
        {
            "name": "Modern White Elongated Toilet — Dual Flush",
            "qty": 2, "unit": "EA", "unit_price": 229.99,
            "url": f"{KENT_BASE}/tidal-3-5-4-8lpf-elongated-front-dual-flush-1-piece-toilet-1579329",
            "notes": "Elongated bowl, dual flush, WaterSense certified. Clean modern white skirted base.",
            "image_url": "/static/images/1579329.jpg",
        },
        {
            "name": "24\" Modern Matte Black Vanity with White Ceramic Top",
            "qty": 2, "unit": "EA", "unit_price": 499.00,
            "url": f"{KENT_BASE}/24-vanity-with-drawer-1697660",
            "notes": "Matte black cabinet + white integrated sink top — B&W modern theme. 24\" fits compact bathrooms.",
            "image_url": "/static/images/1697660.jpg",
        },
        {
            "name": "Shower Stall 32\"×32\" (acrylic, 3-wall)",
            "qty": 2, "unit": "EA", "unit_price": 397.99,
            "url": f"{KENT_BASE}/finesse-4832-white-centre-drain-shower-base-1023986",
            "notes": "3-piece acrylic shower — no bathtub (saves space). OR tile the shower with backer board + tile.",
            "image_url": "/static/images/1023986.jpg",
        },
        {
            "name": "Matte Black Pressure-Balanced Shower Valve + Trim",
            "qty": 2, "unit": "EA", "unit_price": 132.00,
            "url": f"{KENT_BASE}/principals-shower-faucet-1202042",
            "notes": "Matte black single-handle trim — matches B&W design. Pressure-balanced per code.",
            "image_url": "/static/images/1202042.jpg",
        },
        {
            "name": "Matte Black Single-Handle Bathroom Faucet",
            "qty": 2, "unit": "EA", "unit_price": 132.00,
            "url": f"{KENT_BASE}/principals-shower-faucet-1202042",
            "notes": "Principals matte black single-handle lavatory faucet — matches shower valve and vanity. Single-hole mount.",
        },
        {
            "name": "Kitchen Sink — 25\" Undermount Stainless Steel",
            "qty": 1, "unit": "EA", "unit_price": 299.99,
            "url": f"{KENT_BASE}/single-bowl-undermount-sink-1391411",
            "notes": "Single-bowl SS sink, 25\" — fits compact kitchen countertop.",
            "image_url": "/static/images/1391411.jpg",
        },
        {
            "name": "Matte Black Single-Handle Pull-Down Kitchen Faucet",
            "qty": 1, "unit": "EA", "unit_price": 234.99,
            "url": f"{KENT_BASE}/banting-pulldown-kitchen-faucet-matte-black-1199456",
            "notes": "Matte black pull-down faucet — matches anthracite kitchen theme.",
            "image_url": "/static/images/1199456.jpg",
        },
        {
            "name": "PEX Plumbing — 1/2\" × 100' (red + blue)",
            "qty": 2, "unit": "RL", "unit_price": 44.89,
            "url": f"{KENT_BASE}/super-pex-red-1-2-x-100-coil-1036755",
            "notes": "Hot and cold supply — 200 LF total. PEX-A or PEX-B with expansion or crimp fittings.",
            "image_url": "/static/images/1036755.jpg",
        },
        {
            "name": "PEX Plumbing — 3/4\" × 50' (main supply)",
            "qty": 1, "unit": "RL", "unit_price": 39.98,
            "url": f"{KENT_BASE}/superpex-3-4-x-50-white-pex-pipe-1013992",
            "notes": "3/4\" main supply from house to manifold.",
            "image_url": "/static/images/1013992.jpg",
        },
        {
            "name": "PEX Fittings, Manifold, Valves",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/1-2-x-3-4-pex-inlet-x-close-end-6-branch-manifold-1013949",
            "notes": "Manifold system, shut-off valves, supply stops, elbows, tees, crimp rings.",
            "image_url": "/static/images/1013949.jpg",
        },
        {
            "name": "ABS/PVC Drain Pipe & Fittings",
            "qty": 1, "unit": "LOT", "unit_price": 350.00,
            "url": f"{KENT_BASE}/3-abs-pipe-adapter-1001871",
            "notes": "3\" main drain, 2\" branch drains, 1-1/2\" sink/lav drains, P-traps, wyes, cleanouts, vent pipe.",
            "image_url": "/static/images/1001871.jpg",
        },
        {
            "name": "Washer Box (hot/cold supply + drain)",
            "qty": 1, "unit": "EA", "unit_price": 19.12,
            "url": f"{KENT_BASE}/washing-machine-box-1020149",
            "notes": "Recessed washer outlet box with supply valves and drain connection.",
            "image_url": "/static/images/1020149.jpg",
        },
        {
            "name": "Plumber Labor — Rough-in + Finish",
            "qty": 1, "unit": "EA", "unit_price": 4000.00,
            "url": "https://www.yellowpages.ca/search/si/1/Plumbers/St+John%27s+NL",
            "notes": "NL journeyman ~$90/hr × 45 hrs. Rough-in DWV + supply, finish fixtures. 2 visits.",
        },
    ],
}


# ─── Division 9: Electrical ──────────────────────────────────────────────────

DIVISION_9 = {
    "name": "Electrical",
    "items": [
        {
            "name": "100A Sub-Panel (20-space)",
            "qty": 1, "unit": "EA", "unit_price": 156.49,
            "url": f"{KENT_BASE}/100a-8-15-circuit-load-center-sub-panel-1013553",
            "notes": "Fed from main house panel or separate meter. 100A adequate for ~430 sqft suite.",
            "image_url": "/static/images/1013553.jpg",
        },
        {
            "name": "14/2 NMD90 Wire — 150m spool",
            "qty": 2, "unit": "RL", "unit_price": 163.00,
            "url": f"{KENT_BASE}/14-2-nmd90-75m-electrical-wire-blue-1026025",
            "notes": "General lighting + receptacle circuits (15A). 300m total covers ~10 circuits.",
            "image_url": "/static/images/1026025.jpg",
        },
        {
            "name": "12/2 NMD90 Wire — 75m spool",
            "qty": 1, "unit": "RL", "unit_price": 242.00,
            "url": f"{KENT_BASE}/12-2-nmd90-75m-romex-simpull-electrical-wire-1026699",
            "notes": "Kitchen small appliance circuits + bathroom circuits (20A) per CEC code.",
            "image_url": "/static/images/1026699.jpg",
        },
        {
            "name": "10/3 NMD90 Wire — 15m",
            "qty": 1, "unit": "EA", "unit_price": 80.00,
            "url": f"{KENT_BASE}/10-3-nmd90-75m-electrical-wire-orange-1026026",
            "notes": "Dedicated circuits: electric range (40A) and electric dryer (30A).",
            "image_url": "/static/images/1026026.jpg",
        },
        {
            "name": "Receptacles — 15A Tamper-Resistant",
            "qty": 18, "unit": "EA", "unit_price": 2.09,
            "url": f"{KENT_BASE}/15-a-duplex-receptacle-1004457",
            "notes": "General receptacles throughout — bedrooms, kitchen counter, hallway.",
            "image_url": "/static/images/1004457.jpg",
        },
        {
            "name": "GFCI Receptacles — 20A (kitchen & bath)",
            "qty": 4, "unit": "EA", "unit_price": 43.09,
            "url": f"{KENT_BASE}/tamper-resistant-gfci-20amp-1507459",
            "notes": "Required within 1.5m of sinks per CEC: 2 bathrooms + 2 kitchen counter locations.",
            "image_url": "/static/images/1507459.jpg",
        },
        {
            "name": "Light Switches (single-pole + 3-way)",
            "qty": 1, "unit": "PK", "unit_price": 34.95,
            "url": f"{KENT_BASE}/3-way-switch-10-pack-1029553",
            "notes": "Mix of single-pole and 3-way switches for each room + hallway.",
            "image_url": "/static/images/1029553.jpg",
        },
        {
            "name": "LED Slim Recessed Pot Lights 4\" (IC-rated, black trim)",
            "qty": 1, "unit": "PK", "unit_price": 87.99,
            "url": f"{KENT_BASE}/4-led-recessed-pro-12-pack-1519938",
            "notes": "Slim profile, matte black trim ring. 12 total: 3/bedroom, 2/bathroom, 2 kitchen, 2 hallway.",
            "image_url": "/static/images/1519938.jpg",
        },
        {
            "name": "Bathroom Exhaust Fans (80 CFM + light)",
            "qty": 2, "unit": "EA", "unit_price": 69.99,
            "url": f"{KENT_BASE}/80-cfm-0-6-sone-bathroom-fan-1685342",
            "notes": "Required in each bathroom. Vented to exterior through roof or wall.",
            "image_url": "/static/images/1685342.jpg",
        },
        {
            "name": "Smoke / CO Combination Detectors",
            "qty": 4, "unit": "EA", "unit_price": 139.00,
            "url": f"{KENT_BASE}/hardwired-interconnected-combination-smoke-co-alarm-1661640",
            "notes": "Interconnected: 1 per bedroom, 1 hallway outside bedrooms, 1 kitchen area. Per NBC/NFPA.",
            "image_url": "/static/images/1661640.jpg",
        },
        {
            "name": "Electrical Boxes, Connectors & Wire Staples",
            "qty": 1, "unit": "LOT", "unit_price": 200.00,
            "url": f"{KENT_BASE}/device-box-6-pack-2-x-3-x-2-5-1111670",
            "notes": "Single-gang, double-gang, octagon boxes. NM connectors, wire staples, wire nuts.",
            "image_url": "/static/images/1111670.jpg",
        },
        {
            "name": "Weatherproof Exterior Receptacle + Cover",
            "qty": 1, "unit": "EA", "unit_price": 33.59,
            "url": f"{KENT_BASE}/kraloy-pvc-2-gang-weatherproof-switch-gfci-cover-1026018",
            "notes": "GFCI-protected exterior receptacle at entrance — required by code.",
            "image_url": "/static/images/1026018.jpg",
        },
        {
            "name": "Electrician Labor — Rough-in + Finish",
            "qty": 1, "unit": "EA", "unit_price": 3500.00,
            "url": "https://www.yellowpages.ca/search/si/1/Electricians/St+John%27s+NL",
            "notes": "NL journeyman ~$85/hr × 40 hrs. Sub-panel, 10+ circuits, devices, fixtures.",
        },
    ],
}


# ─── Division 10: HVAC ───────────────────────────────────────────────────────

DIVISION_10 = {
    "name": "HVAC",
    "items": [
        {
            "name": "Ductless Mini-Split Heat Pump — 18,000 BTU",
            "qty": 1, "unit": "EA", "unit_price": 1553.00,
            "url": f"{KENT_BASE}/18-000-btu-hyper-heat-ductless-mini-split-outdoor-1034429",
            "notes": "Outdoor condenser unit (Perfect Aire hyper-heat, -30°C rated). Indoor head unit sold separately. Mount in kitchen/hall to serve whole suite.",
            "image_url": "/static/images/1034429.jpg",
        },
        {
            "name": "Electric Baseboard Heaters (1500W, 6')",
            "qty": 2, "unit": "EA", "unit_price": 102.00,
            "url": f"{KENT_BASE}/baseboard-240v-1500w-66-1652016",
            "notes": "Supplementary heat in each bedroom — backup for extreme cold days. Thermostat-controlled.",
            "image_url": "/static/images/1652016.jpg",
        },
        {
            "name": "HRV — Heat Recovery Ventilator (small unit)",
            "qty": 1, "unit": "EA", "unit_price": 1279.00,
            "url": f"{KENT_BASE}/heat-recovery-ventilator-air-exchanger-1400849",
            "notes": "Required by code for tight construction. Recovers ~70% heat from exhaust air. Lifebreath or vänEE brand.",
            "image_url": "/static/images/1400849.jpg",
        },
        {
            "name": "HRV Ducting, Grilles & Dampers",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/6-x-25-silver-insulated-air-duct-1014547",
            "notes": "6\" insulated flex duct, exterior wall caps, interior grilles (supply + exhaust), dampers.",
            "image_url": "/static/images/1014547.jpg",
        },
        {
            "name": "HVAC Installation Labor",
            "qty": 1, "unit": "EA", "unit_price": 2000.00,
            "url": "https://www.yellowpages.ca/search/si/1/Heating+Contractors/St+John%27s+NL",
            "notes": "Mini-split install ~$1,200 + HRV ducting ~$800. Typical $1,500-2,500 in NL.",
        },
    ],
}


# ─── Division 11: Kitchen ────────────────────────────────────────────────────

DIVISION_11 = {
    "name": "Kitchen",
    "items": [
        {
            "name": "IKEA METOD + NICKEBO Matte Anthracite Kitchen (8 LF)",
            "qty": 1, "unit": "SET", "unit_price": 2500.00,
            "url": "https://www.ikea.com/ca/en/p/nickebo-door-matte-anthracite-70537861/",
            "image_url": "/static/images/kitchen-nickebo.jpg",
            "notes": "8 LF: base (4 LF) + upper (4 LF). METOD frames + NICKEBO matte anthracite doors — sleek modern black kitchen.",
        },
        {
            "name": "White Laminate Countertop — 8' Post-Formed",
            "qty": 1, "unit": "EA", "unit_price": 300.00,
            "url": f"{KENT_BASE}/25-x-8-2300-kitchen-countertop-1015537",
            "notes": "Bright white laminate — high contrast with anthracite cabinets. 25\" deep, 8' length.",
            "image_url": "/static/images/1015537.jpg",
        },
        {
            "name": "24\" Apartment-Size Electric Range — Black/Stainless",
            "qty": 1, "unit": "EA", "unit_price": 1795.00,
            "url": f"{KENT_BASE}/24-electric-range-upswept-spillguard-cooktop-1461599",
            "notes": "24\" freestanding electric range, black or black stainless finish. GE, Frigidaire, or Danby.",
            "image_url": "/static/images/1461599.jpg",
        },
        {
            "name": "24\" Apartment-Size Refrigerator — Black/Stainless",
            "qty": 1, "unit": "EA", "unit_price": 1395.00,
            "url": f"{KENT_BASE}/24-bottom-freezer-refrigerator-12-9cf-1461451",
            "notes": "24\" counter-depth, 10–12 cu ft. Black or black stainless to match kitchen theme.",
            "image_url": "/static/images/1461451.jpg",
        },
        {
            "name": "Black Under-Cabinet Range Hood — 24\"",
            "qty": 1, "unit": "EA", "unit_price": 1694.00,
            "url": f"{KENT_BASE}/500-series-24-under-cabinet-range-hood-stainless-steel-1462473",
            "notes": "Black finish matches anthracite cabinet theme. Ducted to exterior preferred.",
            "image_url": "/static/images/1462473.jpg",
        },
    ],
}


# ─── Division 12: Laundry ────────────────────────────────────────────────────

DIVISION_12 = {
    "name": "Laundry",
    "items": [
        {
            "name": "GE 24\" Front Load Washer/Dryer Combo — Ventless",
            "qty": 1, "unit": "EA", "unit_price": 1395.00,
            "url": f"{KENT_BASE}/24-front-load-washer-dryer-combo-ventless-2-4-cu-ft-1462204",
            "sku": "1462204",
            "notes": "GE GFQ14ESSNWW, 24\" compact front-load combo. Ventless — no duct needed. Steam wash, auto wash+dry, fits closet.",
            "image_url": "/static/images/1462204.jpg",
        },
    ],
}


# ─── Assemble all divisions ──────────────────────────────────────────────────

ALL_DIVISIONS = [
    DIVISION_1, DIVISION_2, DIVISION_3, DIVISION_4, DIVISION_5, DIVISION_6,
    DIVISION_7, DIVISION_8, DIVISION_9, DIVISION_10, DIVISION_11, DIVISION_12,
]


def calculate_division_total(division):
    """Calculate total cost for one division."""
    return sum(item["qty"] * item["unit_price"] for item in division["items"])


def calculate_bom_summary():
    """Return full BOM cost summary."""
    subtotals = []
    for div in ALL_DIVISIONS:
        total = calculate_division_total(div)
        subtotals.append({"name": div["name"], "total": total})

    materials_subtotal = sum(s["total"] for s in subtotals)
    waste = materials_subtotal * WASTE_FACTOR
    subtotal_with_waste = materials_subtotal + waste
    hst = subtotal_with_waste * NL_HST
    grand_total = subtotal_with_waste + hst

    return {
        "divisions": subtotals,
        "materials_subtotal": materials_subtotal,
        "waste_contingency": waste,
        "subtotal_with_waste": subtotal_with_waste,
        "hst": hst,
        "grand_total": grand_total,
    }


def get_all_linked_products():
    """Return a flat list of all BOM items that have a Kent.ca or store URL."""
    products = []
    for div in ALL_DIVISIONS:
        for item in div["items"]:
            if item.get("url"):
                products.append({
                    "division": div["name"],
                    "name": item["name"],
                    "qty": item["qty"],
                    "unit": item["unit"],
                    "unit_price": item["unit_price"],
                    "extended": item["qty"] * item["unit_price"],
                    "url": item["url"],
                    "sku": item.get("sku", ""),
                    "notes": item.get("notes", ""),
                })
    return products


# Quick sanity check when run directly
if __name__ == "__main__":
    summary = calculate_bom_summary()
    print("=" * 60)
    print("ST. JOHN'S 430 SQFT BACKYARD SUITE — BOM SUMMARY")
    print("=" * 60)
    for d in summary["divisions"]:
        print(f"  {d['name']:<35} ${d['total']:>10,.2f}")
    print("-" * 60)
    print(f"  {'Materials Subtotal':<35} ${summary['materials_subtotal']:>10,.2f}")
    print(f"  {'10% Waste & Contingency':<35} ${summary['waste_contingency']:>10,.2f}")
    print(f"  {'Subtotal with Contingency':<35} ${summary['subtotal_with_waste']:>10,.2f}")
    print(f"  {'15% NL HST':<35} ${summary['hst']:>10,.2f}")
    print("=" * 60)
    print(f"  {'GRAND TOTAL':<35} ${summary['grand_total']:>10,.2f}")
    print("=" * 60)

    linked = get_all_linked_products()
    print(f"\n{len(linked)} items with product links")
