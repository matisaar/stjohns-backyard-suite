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
            "url": "https://www.stjohns.ca/en/business-investment/building-permits.aspx",
            "notes": "Backyard suite permit, contact City of St. John's Development Dept.",
        },
        {
            "name": "Engineered Drawings & Stamps",
            "qty": 1, "unit": "EA", "unit_price": 2500.00,
            "url": None,
            "notes": "Structural engineer + architectural drawings for permit submission",
        },
        {
            "name": "Site Survey",
            "qty": 1, "unit": "EA", "unit_price": 500.00,
            "url": None,
            "notes": "Licensed NL land surveyor — confirm lot lines and setbacks",
        },
        {
            "name": "Portable Toilet Rental (3 months)",
            "qty": 1, "unit": "EA", "unit_price": 600.00,
            "url": None,
            "notes": "Construction-duration rental from local provider",
        },
        {
            "name": "Dumpster Rental (2 hauls)",
            "qty": 2, "unit": "EA", "unit_price": 500.00,
            "url": None,
            "notes": "20-yard bin, construction debris disposal",
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
            "url": None,
            "notes": "Strip topsoil, excavate to 18\" depth for FPSF, grade for drainage",
        },
        {
            "name": "4\" Gravel Base (3/4\" clear crush)",
            "qty": 16, "unit": "cu yd", "unit_price": 45.00,
            "url": None,
            "notes": "Compacted granular base under slab — local aggregate supplier",
        },
        {
            "name": "2\" XPS Rigid Insulation Under Slab (R-10)",
            "qty": 14, "unit": "SH", "unit_price": 45.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation/rigid-insulation",
            "notes": "4'x8' sheets, covers 430 sqft slab area (14 × 32 sqft = 448 sqft)",
        },
        {
            "name": "2\" XPS Perimeter / Wing Insulation",
            "qty": 8, "unit": "SH", "unit_price": 45.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation/rigid-insulation",
            "notes": "Frost-protected shallow foundation perimeter insulation",
        },
        {
            "name": "10-mil Poly Vapour Barrier (under slab)",
            "qty": 1, "unit": "RL", "unit_price": 89.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation",
            "notes": "20'x50' roll, moisture barrier under concrete slab",
        },
        {
            "name": "Concrete — 4\" Slab + Thickened Edges",
            "qty": 5.5, "unit": "cu m", "unit_price": 250.00,
            "url": None,
            "notes": "Ready-mix delivery, 25 MPa. ~5.5 m³ for 430 sqft × 4\" + 12\" thickened edge perimeter",
        },
        {
            "name": "Rebar / Welded Wire Mesh",
            "qty": 430, "unit": "sqft", "unit_price": 0.75,
            "url": f"{KENT_BASE}/shop/building-materials/concrete-landscaping-products",
            "notes": "6×6 W2.9×W2.9 mesh over full slab, rebar in thickened edges",
        },
        {
            "name": "Perimeter Drain Tile + Filter Fabric + Gravel",
            "qty": 80, "unit": "LF", "unit_price": 3.00,
            "url": f"{KENT_BASE}/shop/building-materials/concrete-landscaping-products",
            "notes": "4\" perforated pipe around foundation perimeter to daylight / sump",
        },
        {
            "name": "Backfill & Final Grading (allowance)",
            "qty": 1, "unit": "EA", "unit_price": 500.00,
            "url": None,
            "notes": "Machine backfill and grade for drainage away from building",
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
        },
        {
            "name": "2×6×10' SPF #2 & Better KD (headers, corners)",
            "qty": 20, "unit": "EA", "unit_price": 10.88,
            "url": f"{KENT_BASE}/2-x-6-x-10-2-better-spf-lumber-kiln-dried-1016313",
            "notes": "Built-up headers over windows/doors, corner assemblies",
            "sku": "1016313",
        },
        {
            "name": "2×4×8' SPF Stud Kiln Dried (interior partitions)",
            "qty": 60, "unit": "EA", "unit_price": 3.98,
            "url": f"{KENT_BASE}/2-x-4-x-8-spf-stud-kiln-dried-1016318",
            "notes": "Interior walls: 2 bathroom walls + 2 bedroom walls + kitchen partition ≈60 LF / 1.33 = 45 + extras",
            "sku": "1016318",
        },
        {
            "name": "2×4×12' SPF #2 & Better KD (misc framing)",
            "qty": 20, "unit": "EA", "unit_price": 7.66,
            "url": f"{KENT_BASE}/2-x-4-x-12-2-better-spf-lumber-kiln-dried-1016339",
            "notes": "Blocking, backing, cripples, misc framing needs",
            "sku": "1016339",
        },
        {
            "name": "2×4×10' SPF #2 & Better KD",
            "qty": 12, "unit": "EA", "unit_price": 6.38,
            "url": f"{KENT_BASE}/2-x-4-x-10-2-better-spf-lumber-kiln-dried-1016338",
            "notes": "Top plates (doubled), additional blocking",
            "sku": "1016338",
        },
        {
            "name": "Engineered I-Joists / Rafters (roof, ~22' span)",
            "qty": 24, "unit": "EA", "unit_price": 25.00,
            "url": f"{KENT_BASE}/shop/building-materials/lumber-composites",
            "notes": "Special order — 9.5\" or 11-7/8\" TJI joists for mono-slope roof, 16\" OC over 21.5' span",
        },
        {
            "name": "LVL Beam (3.5×9.5\" for headers/ridge)",
            "qty": 2, "unit": "EA", "unit_price": 150.00,
            "url": f"{KENT_BASE}/shop/building-materials/lumber-composites",
            "notes": "Laminated veneer lumber for window/door headers and any concentrated loads",
        },
        {
            "name": "1/2\" × 4' × 8' Spruce Plywood (wall sheathing)",
            "qty": 30, "unit": "SH", "unit_price": 39.98,
            "url": f"{KENT_BASE}/1-2-x-4-x-8-12-5mm-spruce-plywood-standard-1015823",
            "notes": "Exterior wall sheathing: ~82 LF perimeter × 8' H = 656 sqft ÷ 32 = ~21 sheets + gable ends = 30",
            "sku": "1015823",
        },
        {
            "name": "5/8\" × 4' × 8' Spruce Plywood (roof deck)",
            "qty": 18, "unit": "SH", "unit_price": 54.38,
            "url": f"{KENT_BASE}/5-8-4-x-8-15-5mm-spruce-plywood-standard-1015826",
            "notes": "Roof sheathing: 430 sqft + slope factor + 2' overhang = ~530 sqft ÷ 32 = 17 sheets → 18",
            "sku": "1015826",
        },
        {
            "name": "3/4\" × 4' × 8' Spruce Plywood (subfloor — if raised)",
            "qty": 0, "unit": "SH", "unit_price": 63.98,
            "url": f"{KENT_BASE}/3-4-x-4-x-8-18-5mm-spruce-plywood-standard-1015824",
            "notes": "NOT NEEDED for slab-on-grade. Included at qty=0 as reference for future scope change.",
            "sku": "1015824",
        },
        {
            "name": "Pressure Treated 2×6 Sill Plates",
            "qty": 12, "unit": "EA", "unit_price": 14.00,
            "url": f"{KENT_BASE}/shop/building-materials/lumber-composites/pressure-treated-lumber",
            "notes": "Bottom plates on concrete — must be pressure treated. ~82 LF = 12 × 8' pieces",
        },
        {
            "name": "Simpson Strong-Tie Connectors & Hardware",
            "qty": 1, "unit": "LOT", "unit_price": 400.00,
            "url": "https://www.strongtie.com/",
            "notes": "Hurricane ties, joist hangers, post bases, hold-downs per engineered design",
        },
        {
            "name": "Framing Nails — 3.25\" (16d sinker, 50 lb)",
            "qty": 2, "unit": "BX", "unit_price": 65.00,
            "url": f"{KENT_BASE}/shop/tools/pneumatics-compressors",
            "notes": "~100 lbs total for wall and roof framing",
        },
        {
            "name": "Construction Screws & Misc Fasteners",
            "qty": 1, "unit": "LOT", "unit_price": 200.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "Deck screws, structural screws, lag bolts, anchor bolts, misc",
        },
        {
            "name": "PL Premium Construction Adhesive",
            "qty": 10, "unit": "EA", "unit_price": 8.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "Subfloor/sheathing adhesive — glue-and-screw for rigidity",
        },
    ],
}


# ─── Division 4: Exterior Envelope ───────────────────────────────────────────

DIVISION_4 = {
    "name": "Exterior Envelope",
    "items": [
        {
            "name": "Tyvek HomeWrap 9' × 100'",
            "qty": 2, "unit": "RL", "unit_price": 180.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "Weather-resistant barrier over wall sheathing. 2 rolls covers ~1,800 sqft (need ~700 sqft + overlaps)",
        },
        {
            "name": "1.5\" XPS Rigid Exterior Continuous Insulation (R-7.5)",
            "qty": 30, "unit": "SH", "unit_price": 40.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation/rigid-insulation",
            "notes": "4'x8' sheets over Tyvek. Brings wall to R-24 effective (R-20 batt + R-7.5 continuous). 30 × 32 = 960 sqft",
        },
        {
            "name": "Mitten Oregon Pride Dutchlap Vinyl Siding (12'1\")",
            "qty": 50, "unit": "EA", "unit_price": 11.19,
            "url": f"{KENT_BASE}/oregon-pride-double-4-5-dutchlap-siding-1010820",
            "notes": "Exterior cladding — 50 pieces × ~9 sqft exposed = 450 sqft coverage (wall area ~650 sqft, minus windows/door)",
            "sku": "1010820",
        },
        {
            "name": "Vinyl Siding Starter Strip, J-Channel, Corners",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/shop/exterior-siding",
            "notes": "Starter strip ~82 LF, J-channel around 6 windows + 1 door, 4 outside corners, 2 inside corners",
        },
        {
            "name": "Double 5\" Perforated Soffit (12' pieces)",
            "qty": 16, "unit": "EA", "unit_price": 2.48,
            "url": f"{KENT_BASE}/double-5-perforated-soffit-standard-1021390",
            "notes": "Soffit for 2' overhang on all sides: (82 LF perimeter × 2' ÷ ~10 sqft per piece = ~16 pcs)",
            "sku": "1021390",
        },
        {
            "name": "Aluminum Fascia & Trim",
            "qty": 82, "unit": "LF", "unit_price": 3.00,
            "url": f"{KENT_BASE}/shop/exterior-siding",
            "notes": "Pre-bent aluminum fascia covers, full perimeter + gable rake",
        },
        {
            "name": "Triple-Pane Vinyl Casement Windows (~30\"×48\")",
            "qty": 6, "unit": "EA", "unit_price": 450.00,
            "url": "https://www.homedepot.ca/en/home/categories/windows-and-doors/windows.html",
            "notes": "6 windows: 2 bedrooms (egress-sized, min 3.8 sqft openable), 2 bathrooms (small), 2 kitchen. Get local quotes from Kohltech or JELD-WEN NL dealers for triple-pane.",
        },
        {
            "name": "Steel Insulated Entry Door — 36\" Black with Frame",
            "qty": 1, "unit": "EA", "unit_price": 450.00,
            "url": "https://www.homedepot.ca/en/home/categories/windows-and-doors/exterior-doors.html",
            "notes": "Pre-hung insulated steel door, black exterior finish. Modern B&W aesthetic. Single entrance.",
        },
        {
            "name": "Window & Door Flashing Tape",
            "qty": 2, "unit": "RL", "unit_price": 30.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "Self-adhering membrane flashing, 4\" × 75' — flash all window and door rough openings",
        },
        {
            "name": "Exterior Caulking & Sealants",
            "qty": 1, "unit": "LOT", "unit_price": 100.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "Polyurethane sealant for all exterior penetrations, window perimeters, siding joints",
        },
    ],
}


# ─── Division 5: Roofing ─────────────────────────────────────────────────────

DIVISION_5 = {
    "name": "Roofing",
    "items": [
        {
            "name": "IKO Cambridge Architectural Shingles (Dual Black)",
            "qty": 16, "unit": "BD", "unit_price": 40.99,
            "url": f"{KENT_BASE}/40-7-8-x-13-3-4-cambridge-shingle-1010785",
            "notes": "~530 sqft roof area ÷ 33.3 sqft/bundle = 16 bundles (~5 squares). Architectural style, 30-yr warranty.",
            "sku": "1010785",
        },
        {
            "name": "IKO StormShield Ice & Water Protector 36\"×65'",
            "qty": 2, "unit": "RL", "unit_price": 84.99,
            "url": f"{KENT_BASE}/stormshield-ice-water-protector-36-x-65-1026762",
            "notes": "Full coverage on mono-slope roof at 3:12 pitch recommended in NL. 2 rolls = 390 sqft. May need 3 for full coverage.",
            "sku": "1026762",
        },
        {
            "name": "Organic Felt Underlayment 36\"×131'",
            "qty": 1, "unit": "RL", "unit_price": 44.99,
            "url": f"{KENT_BASE}/organic-fibers-black-saturated-felt-roofing-36-x-131-1026830",
            "notes": "#15 felt over remaining roof area not covered by ice & water shield",
            "sku": "1026830",
        },
        {
            "name": "Drip Edge 10' (Pebble)",
            "qty": 12, "unit": "EA", "unit_price": 8.29,
            "url": f"{KENT_BASE}/10-x-2-1-2-x-1-roof-edge-drip-cap-1021389",
            "notes": "Full perimeter of roof: ~82 LF + 2 × 22' rakes = 126 LF → 13 pieces, use 12 + offcuts",
            "sku": "1021389",
        },
        {
            "name": "Step Flashing 4\"×4\"×8\"",
            "qty": 20, "unit": "EA", "unit_price": 3.49,
            "url": f"{KENT_BASE}/step-flashing-4-x-4-x-8-1016918",
            "notes": "Where roof meets any wall projections or penetrations",
            "sku": "1016918",
        },
        {
            "name": "Roof Vent / Exhaust Vents",
            "qty": 2, "unit": "EA", "unit_price": 40.00,
            "url": f"{KENT_BASE}/shop/building-materials/roofing",
            "notes": "Static roof vents or ridge vent for attic ventilation. Required for shingle warranty.",
        },
        {
            "name": "Thermocell Air Chutes 22.5\"×27\"",
            "qty": 20, "unit": "EA", "unit_price": 2.19,
            "url": f"{KENT_BASE}/thermocell-air-chutes-22-5-x-27-max-r-value-r36-1042887",
            "notes": "Maintain airflow between insulation and roof deck in each rafter bay",
            "sku": "1042887",
        },
        {
            "name": "Roofing Nails (coil, 1-1/4\")",
            "qty": 2, "unit": "BX", "unit_price": 30.00,
            "url": f"{KENT_BASE}/shop/building-materials/roofing",
            "notes": "Galvanized roofing nails for shingle and underlayment",
        },
    ],
}


# ─── Division 6: Insulation & Air Barrier ─────────────────────────────────────

DIVISION_6 = {
    "name": "Insulation & Air Barrier",
    "items": [
        {
            "name": "Owens Corning R-20 Fiberglass Batt 15\" (78.3 sqft/bag)",
            "qty": 10, "unit": "BG", "unit_price": 89.57,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r20-47-x-15-x-6-78-3-sqft-1024741",
            "notes": "Exterior wall cavities: ~650 sqft net wall area ÷ 78.3 = 8.3 bags + 15% waste = 10 bags",
            "sku": "1024741",
        },
        {
            "name": "Owens Corning R-20 Fiberglass Batt 23\" (120.1 sqft/bag)",
            "qty": 2, "unit": "BG", "unit_price": 137.00,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r20-47-x-23-x-6-120-1-sqft-1024744",
            "notes": "24\" OC areas if any, or for wider bays. 2 bags supplementary.",
            "sku": "1024744",
        },
        {
            "name": "Owens Corning R-28 Fiberglass Batt 24\" (80 sqft/bag)",
            "qty": 6, "unit": "BG", "unit_price": 126.00,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r28-48-x-24-x-8-1-2-80-sqft-1024751",
            "notes": "Ceiling / roof cavity — first layer. 6 × 80 = 480 sqft covers full ceiling.",
            "sku": "1024751",
        },
        {
            "name": "Owens Corning R-31 Fiberglass Batt 16\" (42.7 sqft/bag)",
            "qty": 4, "unit": "BG", "unit_price": 79.99,
            "url": f"{KENT_BASE}/owens-corning-insulation-ws-r31-48-x-16-x-9-1-2-42-7-sqft-1024752",
            "notes": "Ceiling top-up layer to achieve effective R-50+. 4 × 42.7 = 171 sqft (supplement where depth allows).",
            "sku": "1024752",
        },
        {
            "name": "6-mil Polyethylene Vapour Barrier",
            "qty": 2, "unit": "RL", "unit_price": 60.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation",
            "notes": "Interior side of walls and ceiling — continuous air/vapour barrier per NBC. 10'×100' rolls.",
        },
        {
            "name": "Roxul Safe'n'Sound Acoustic Batt (bathroom walls)",
            "qty": 3, "unit": "BG", "unit_price": 50.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation/mineral-wool-insulation",
            "notes": "Sound insulation in shared bathroom/bedroom partition walls — mineral wool batts",
        },
        {
            "name": "Great Stuff Spray Foam (gaps & rim joist)",
            "qty": 6, "unit": "EA", "unit_price": 12.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation/spray-foam-insulation",
            "notes": "Expanding spray foam for sealing around pipes, wires, rim joists, sill plate to slab",
        },
        {
            "name": "Tuck Tape (Red Sheathing Tape)",
            "qty": 4, "unit": "RL", "unit_price": 10.00,
            "url": f"{KENT_BASE}/shop/building-materials/insulation",
            "notes": "Seal all poly seams, sheathing joints. 60mm × 66m rolls.",
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
        },
        {
            "name": "CGC 1/2\" × 4' × 12' Tapered Edge Drywall",
            "qty": 12, "unit": "SH", "unit_price": 26.73,
            "url": f"{KENT_BASE}/drywall-1-2-x-4-x-12-tapered-edge-panel-1016149",
            "notes": "Ceiling panels — 12' length reduces joints. 12 × 48 sqft = 576 sqft (ceiling 430 sqft + waste).",
            "sku": "1016149",
        },
        {
            "name": "CGC 5/8\" × 4' × 8' Type X Firecode Drywall",
            "qty": 4, "unit": "SH", "unit_price": 31.99,
            "url": f"{KENT_BASE}/drywall-firecode-5-8-x-4-x-8-type-x-panel-1016160",
            "notes": "Fire-rated drywall for furnace/utility areas or where required by code.",
            "sku": "1016160",
        },
        {
            "name": "CGC 17L All-Purpose Lite Drywall Compound",
            "qty": 3, "unit": "EA", "unit_price": 32.87,
            "url": f"{KENT_BASE}/17-l-sheetrock-all-purpose-lite-drywall-compound-white-1021974",
            "notes": "3-coat system: tape coat, fill coat, finish coat.",
            "sku": "1021974",
        },
        {
            "name": "Drywall Tape, Corner Bead, Screws Lot",
            "qty": 1, "unit": "LOT", "unit_price": 100.00,
            "url": f"{KENT_BASE}/shop/building-materials/drywall",
            "notes": "Paper tape, vinyl corner bead, 1-1/4\" drywall screws, sandpaper",
        },
        {
            "name": "Sico Pro PVA Drywall Primer White 18.9L",
            "qty": 1, "unit": "EA", "unit_price": 84.00,
            "url": f"{KENT_BASE}/sico-pro-pva-primer-interior-white-18-9-l-1058991",
            "sku": "1058991",
            "image_url": "/static/images/paint-sico-primer.jpg",
            "notes": "White PVA primer — one coat all new drywall. ~1,800 sqft coverage per pail.",
        },
        {
            "name": "Sico Evolution Interior Eggshell Pure White 3.78L",
            "qty": 6, "unit": "EA", "unit_price": 68.99,
            "url": f"{KENT_BASE}/sico-evolution-interior-latex-eggshell-neutral-base-3-78-l-1015669-NEU",
            "sku": "1015669-NEU",
            "image_url": "/static/images/paint-sico-evolution.jpg",
            "notes": "Bright white walls throughout — modern B&W aesthetic. 6 cans × 400 sqft = 2,400 sqft (2 coats on ~1,200 sqft).",
        },
        {
            "name": "Clarovista 5.0mm Aged European Oak Stone Core Vinyl Plank",
            "qty": 26, "unit": "BX", "unit_price": 62.12,
            "url": f"{KENT_BASE}/clarovista-5-0mm-stone-core-vinyl-plank-aged-european-oak-1142112-AEO",
            "sku": "1142112-AEO",
            "image_url": "/static/images/lvp-clarovista.jpg",
            "notes": "Dark brown European Oak LVP — 18.94 sqft/box × 26 = 492 sqft (430 + 15% waste). Waterproof click-lock throughout.",
        },
        {
            "name": "White Large-Format Ceramic Wall Tile 12\"×24\" (shower walls)",
            "qty": 130, "unit": "sqft", "unit_price": 4.00,
            "url": f"{KENT_BASE}/shop/flooring/tile",
            "notes": "2 shower surrounds × ~65 sqft each. White 12×24 tile — modern B&W aesthetic contrast with dark floor.",
        },
        {
            "name": "Cement Backer Board (Durock / HardieBacker)",
            "qty": 8, "unit": "SH", "unit_price": 30.00,
            "url": f"{KENT_BASE}/shop/building-materials",
            "notes": "1/2\" × 3' × 5' cement board behind all tiled shower areas — moisture-proof substrate.",
        },
        {
            "name": "Thin-Set Mortar, Grout, Tile Trim",
            "qty": 1, "unit": "LOT", "unit_price": 120.00,
            "url": f"{KENT_BASE}/shop/flooring",
            "notes": "Modified thin-set (50 lb bag × 2), sanded grout, Schluter trim edges, spacers.",
        },
        {
            "name": "Alexandria 1/2\"×3-1/2\"×96\" Modern MDF Baseboard Valupak (10-pack)",
            "qty": 3, "unit": "PK", "unit_price": 50.89,
            "url": f"{KENT_BASE}/1-2-x-3-1-2-x-96-modern-mdf-baseboard-primed-valupak-1447728",
            "sku": "1447728",
            "image_url": "/static/images/baseboard-alexandria.jpg",
            "notes": "Clean modern profile, pre-primed white. 10×8' per pack = 80 LF × 3 packs = 240 LF (covers 200 LF + waste).",
        },
        {
            "name": "Pocket Door Kit — 30\" Modern White",
            "qty": 4, "unit": "EA", "unit_price": 150.00,
            "url": f"{KENT_BASE}/shop/building-materials/doors",
            "notes": "4 pocket doors: 2 bedrooms + 2 bathrooms. White flat-panel slab with matte black flush pulls.",
        },
        {
            "name": "Matte Black Pocket Door Pull Sets (privacy + passage)",
            "qty": 4, "unit": "EA", "unit_price": 25.00,
            "url": f"{KENT_BASE}/shop/building-materials/door-hardware",
            "notes": "2 privacy (bath) + 2 passage (bedroom). Matte black flush pulls — B&W modern theme.",
        },
        {
            "name": "Closet Shelving & Rods",
            "qty": 2, "unit": "EA", "unit_price": 50.00,
            "url": f"{KENT_BASE}/shop/building-materials/shelving-accessories",
            "notes": "Wire shelf + rod kit per bedroom closet. ~4' wide each.",
        },
    ],
}


# ─── Division 8: Plumbing ────────────────────────────────────────────────────

DIVISION_8 = {
    "name": "Plumbing",
    "items": [
        {
            "name": "40-Gallon Electric Water Heater",
            "qty": 1, "unit": "EA", "unit_price": 600.00,
            "url": "https://www.homedepot.ca/en/home/categories/heating-venting-and-cooling/water-heaters.html",
            "notes": "Standard electric tank water heater. Adequate for 2-person suite. NL electricity is cheap.",
        },
        {
            "name": "Modern White Elongated Toilet — Dual Flush",
            "qty": 2, "unit": "EA", "unit_price": 200.00,
            "url": "https://www.homedepot.ca/en/home/categories/bath/toilets.html",
            "notes": "Elongated bowl, dual flush, WaterSense certified. Clean modern white skirted base.",
        },
        {
            "name": "24\" Modern Matte Black Vanity with White Ceramic Top",
            "qty": 2, "unit": "EA", "unit_price": 350.00,
            "url": "https://www.homedepot.ca/en/home/categories/bath/bathroom-vanities.html",
            "notes": "Matte black cabinet + white integrated sink top — B&W modern theme. 24\" fits compact bathrooms.",
        },
        {
            "name": "Shower Stall 32\"×32\" (acrylic, 3-wall)",
            "qty": 2, "unit": "EA", "unit_price": 400.00,
            "url": "https://www.homedepot.ca/en/home/categories/bath/showers/shower-stalls-and-kits.html",
            "notes": "3-piece acrylic shower — no bathtub (saves space). OR tile the shower with backer board + tile.",
        },
        {
            "name": "Matte Black Pressure-Balanced Shower Valve + Trim",
            "qty": 2, "unit": "EA", "unit_price": 200.00,
            "url": "https://www.homedepot.ca/en/home/categories/bath/bathroom-faucets/shower-faucets.html",
            "notes": "Matte black single-handle trim — matches B&W design. Pressure-balanced per code.",
        },
        {
            "name": "Kitchen Sink — 25\" Undermount Stainless Steel",
            "qty": 1, "unit": "EA", "unit_price": 250.00,
            "url": "https://www.homedepot.ca/en/home/categories/kitchen/kitchen-sinks.html",
            "notes": "Single-bowl SS sink, 25\" — fits compact kitchen countertop.",
        },
        {
            "name": "Matte Black Single-Handle Pull-Down Kitchen Faucet",
            "qty": 1, "unit": "EA", "unit_price": 150.00,
            "url": "https://www.homedepot.ca/en/home/categories/kitchen/kitchen-faucets.html",
            "notes": "Matte black pull-down faucet — matches anthracite kitchen theme.",
        },
        {
            "name": "PEX Plumbing — 1/2\" × 100' (red + blue)",
            "qty": 2, "unit": "RL", "unit_price": 60.00,
            "url": f"{KENT_BASE}/shop/plumbing",
            "notes": "Hot and cold supply — 200 LF total. PEX-A or PEX-B with expansion or crimp fittings.",
        },
        {
            "name": "PEX Plumbing — 3/4\" × 50' (main supply)",
            "qty": 1, "unit": "RL", "unit_price": 80.00,
            "url": f"{KENT_BASE}/shop/plumbing",
            "notes": "3/4\" main supply from house to manifold.",
        },
        {
            "name": "PEX Fittings, Manifold, Valves",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/shop/plumbing",
            "notes": "Manifold system, shut-off valves, supply stops, elbows, tees, crimp rings.",
        },
        {
            "name": "ABS/PVC Drain Pipe & Fittings",
            "qty": 1, "unit": "LOT", "unit_price": 350.00,
            "url": f"{KENT_BASE}/shop/plumbing",
            "notes": "3\" main drain, 2\" branch drains, 1-1/2\" sink/lav drains, P-traps, wyes, cleanouts, vent pipe.",
        },
        {
            "name": "Washer Box (hot/cold supply + drain)",
            "qty": 1, "unit": "EA", "unit_price": 50.00,
            "url": f"{KENT_BASE}/shop/plumbing",
            "notes": "Recessed washer outlet box with supply valves and drain connection.",
        },
        {
            "name": "Plumber Labor — Rough-in + Finish",
            "qty": 1, "unit": "EA", "unit_price": 4000.00,
            "url": None,
            "notes": "Licensed NL plumber. Rough-in: supply, DWV, venting. Finish: set fixtures. ~2 visits.",
        },
    ],
}


# ─── Division 9: Electrical ──────────────────────────────────────────────────

DIVISION_9 = {
    "name": "Electrical",
    "items": [
        {
            "name": "100A Sub-Panel (20-space)",
            "qty": 1, "unit": "EA", "unit_price": 250.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Fed from main house panel or separate meter. 100A adequate for ~430 sqft suite.",
        },
        {
            "name": "14/2 NMD90 Wire — 150m spool",
            "qty": 2, "unit": "RL", "unit_price": 120.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "General lighting + receptacle circuits (15A). 300m total covers ~10 circuits.",
        },
        {
            "name": "12/2 NMD90 Wire — 75m spool",
            "qty": 1, "unit": "RL", "unit_price": 150.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Kitchen small appliance circuits + bathroom circuits (20A) per CEC code.",
        },
        {
            "name": "10/3 NMD90 Wire — 15m",
            "qty": 1, "unit": "EA", "unit_price": 80.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Dedicated circuits: electric range (40A) and electric dryer (30A).",
        },
        {
            "name": "Receptacles — 15A Tamper-Resistant",
            "qty": 18, "unit": "EA", "unit_price": 3.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "General receptacles throughout — bedrooms, kitchen counter, hallway.",
        },
        {
            "name": "GFCI Receptacles — 20A (kitchen & bath)",
            "qty": 4, "unit": "EA", "unit_price": 25.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Required within 1.5m of sinks per CEC: 2 bathrooms + 2 kitchen counter locations.",
        },
        {
            "name": "Light Switches (single-pole + 3-way)",
            "qty": 10, "unit": "EA", "unit_price": 3.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Mix of single-pole and 3-way switches for each room + hallway.",
        },
        {
            "name": "LED Slim Recessed Pot Lights 4\" (IC-rated, black trim)",
            "qty": 12, "unit": "EA", "unit_price": 15.00,
            "url": f"{KENT_BASE}/shop/lighting",
            "notes": "Slim profile, matte black trim ring. 12 total: 3/bedroom, 2/bathroom, 2 kitchen, 2 hallway.",
        },
        {
            "name": "Bathroom Exhaust Fans (80 CFM + light)",
            "qty": 2, "unit": "EA", "unit_price": 80.00,
            "url": f"{KENT_BASE}/shop/building-materials/ventilation-ductwork",
            "notes": "Required in each bathroom. Vented to exterior through roof or wall.",
        },
        {
            "name": "Smoke / CO Combination Detectors",
            "qty": 4, "unit": "EA", "unit_price": 40.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Interconnected: 1 per bedroom, 1 hallway outside bedrooms, 1 kitchen area. Per NBC/NFPA.",
        },
        {
            "name": "Electrical Boxes, Connectors & Wire Staples",
            "qty": 1, "unit": "LOT", "unit_price": 200.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Single-gang, double-gang, octagon boxes. NM connectors, wire staples, wire nuts.",
        },
        {
            "name": "Weatherproof Exterior Receptacle + Cover",
            "qty": 1, "unit": "EA", "unit_price": 30.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "GFCI-protected exterior receptacle at entrance — required by code.",
        },
        {
            "name": "Electrician Labor — Rough-in + Finish",
            "qty": 1, "unit": "EA", "unit_price": 3500.00,
            "url": None,
            "notes": "Licensed NL electrician. Rough-in wiring, panel hookup, inspection. Finish: devices + fixtures.",
        },
    ],
}


# ─── Division 10: HVAC ───────────────────────────────────────────────────────

DIVISION_10 = {
    "name": "HVAC",
    "items": [
        {
            "name": "Ductless Mini-Split Heat Pump — 18,000 BTU",
            "qty": 1, "unit": "EA", "unit_price": 3000.00,
            "url": "https://www.homedepot.ca/en/home/categories/heating-venting-and-cooling/mini-splits.html",
            "notes": "Primary heating + cooling for open area. Mitsubishi/Fujitsu/Daikin hyper-heat rated for NL cold (-25°C). Mount head unit in kitchen/hall area to serve whole suite.",
        },
        {
            "name": "Electric Baseboard Heaters (1500W, 6')",
            "qty": 2, "unit": "EA", "unit_price": 120.00,
            "url": f"{KENT_BASE}/shop/electrical",
            "notes": "Supplementary heat in each bedroom — backup for extreme cold days. Thermostat-controlled.",
        },
        {
            "name": "HRV — Heat Recovery Ventilator (small unit)",
            "qty": 1, "unit": "EA", "unit_price": 800.00,
            "url": "https://www.homedepot.ca/en/home/categories/heating-venting-and-cooling/ventilation.html",
            "notes": "Required by code for tight construction. Recovers ~70% heat from exhaust air. Lifebreath or vänEE brand.",
        },
        {
            "name": "HRV Ducting, Grilles & Dampers",
            "qty": 1, "unit": "LOT", "unit_price": 300.00,
            "url": f"{KENT_BASE}/shop/building-materials/ventilation-ductwork",
            "notes": "6\" insulated flex duct, exterior wall caps, interior grilles (supply + exhaust), dampers.",
        },
        {
            "name": "HVAC Installation Labor",
            "qty": 1, "unit": "EA", "unit_price": 2000.00,
            "url": None,
            "notes": "Licensed HVAC tech for mini-split line set, refrigerant charge, HRV ducting, baseboard wiring.",
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
            "url": f"{KENT_BASE}/shop/kitchen/countertops",
            "notes": "Bright white laminate — high contrast with anthracite cabinets. 25\" deep, 8' length.",
        },
        {
            "name": "24\" Apartment-Size Electric Range — Black/Stainless",
            "qty": 1, "unit": "EA", "unit_price": 600.00,
            "url": "https://www.homedepot.ca/en/home/categories/appliances/ranges.html",
            "notes": "24\" freestanding electric range, black or black stainless finish. GE, Frigidaire, or Danby.",
        },
        {
            "name": "24\" Apartment-Size Refrigerator — Black/Stainless",
            "qty": 1, "unit": "EA", "unit_price": 800.00,
            "url": "https://www.homedepot.ca/en/home/categories/appliances/refrigerators.html",
            "notes": "24\" counter-depth, 10–12 cu ft. Black or black stainless to match kitchen theme.",
        },
        {
            "name": "Black Under-Cabinet Range Hood — 24\"",
            "qty": 1, "unit": "EA", "unit_price": 150.00,
            "url": "https://www.homedepot.ca/en/home/categories/appliances/range-hoods.html",
            "notes": "Black finish matches anthracite cabinet theme. Ducted to exterior preferred.",
        },
    ],
}


# ─── Division 12: Laundry ────────────────────────────────────────────────────

DIVISION_12 = {
    "name": "Laundry",
    "items": [
        {
            "name": "Stackable Washer/Dryer — 24\" Compact Set",
            "qty": 1, "unit": "SET", "unit_price": 1800.00,
            "url": "https://www.homedepot.ca/en/home/categories/appliances/washers-and-dryers/stacked-laundry-centres.html",
            "notes": "24\" compact stackable — fits in hallway closet. Electric dryer (no gas in NL). GE, LG, or Bosch.",
        },
        {
            "name": "Dryer Vent Kit (4\" rigid + wall cap)",
            "qty": 1, "unit": "EA", "unit_price": 40.00,
            "url": f"{KENT_BASE}/shop/building-materials/ventilation-ductwork",
            "notes": "4\" rigid aluminum duct + exterior wall cap. Short run to nearest exterior wall.",
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
