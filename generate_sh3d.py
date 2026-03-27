#!/usr/bin/env python3
"""
generate_sh3d.py — Generate Sweet Home 3D (.sh3d) file programmatically.

St. John's 430 sqft Backyard Suite — 97 Mayor Ave
2 Bedrooms · 2 Ensuites · Shared Kitchen · Utility Room
All dimensions from Kent.ca and Home Depot product listings.

Usage:
    python3 generate_sh3d.py
    → outputs stjohns_suite.sh3d
    → open in Sweet Home 3D (File > Open)

Workflow:
    1. Edit dimensions/layout below
    2. Re-run this script
    3. Re-open .sh3d in Sweet Home 3D
    4. Repeat until perfect
"""

import zipfile
import xml.etree.ElementTree as ET
import io
import math
import os

# ═══════════════════════════════════════════════════════
#  UNIT CONVERSION
# ═══════════════════════════════════════════════════════
CM = 2.54  # 1 inch = 2.54 cm

def cm(inches):
    """Convert inches to centimeters for SH3D."""
    return round(inches * CM, 2)

def rgb_int(r, g, b):
    """RGB (0-255) to SH3D integer color."""
    return (r << 16) | (g << 8) | b

def color_hex(color_int):
    """Convert integer color to 8-char uppercase hex for SH3D XML."""
    return format(color_int & 0xFFFFFFFF, '08X')


# ═══════════════════════════════════════════════════════
#  BUILDING CONFIGURATION
# ═══════════════════════════════════════════════════════

# Overall building envelope (inches, outer face to outer face)
W = 258              # 21'-6" width  (east-west)
D = 240              # 20'-0" depth  (north-south)
EXT_T = 5.5          # 2×6 exterior wall thickness
INT_T = 4.5          # 2×4 + drywall interior partition
CEIL_H = 96          # 8'-0" ceiling height

# Interior clear dimensions (inner face of exterior walls)
INNER_N = EXT_T                # 5.5"
INNER_S = D - EXT_T            # 234.5"
INNER_W = EXT_T                # 5.5"
INNER_E = W - EXT_T            # 252.5"

# ── FLOOR PLAN LAYOUT ──
#
#  Plan view — origin (0,0) = NORTHWEST corner
#  X increases EAST, Y increases SOUTH
#
#     x=0  P1_X        P2_X    x=W
#      ┌──────┬──────────┬──────┐  y=0  (North, ENTRANCE)
#      │      │  MAIN    │      │
#      │ BED  │ ENTRANCE │ BED  │
#      │  A   │  SHARED  │  B   │  Top zone
#      │      │  KITCHEN │      │
#      ├──────┼──────────┼──────┤  y=DIV_Y  (E-W divider)
#      │ EN-  │  SHARED  │ EN-  │
#      │SUITE │ UTILITY  │SUITE │  Bottom zone
#      │  A   │  ROOM    │  B   │
#      └──────┴──────────┴──────┘  y=D  (South)
#
#  6 rooms: Bedroom A, Shared Kitchen, Bedroom B (top)
#           Ensuite A, Shared Utility Room, Ensuite B (bottom)

# ── Partition positions (centerline, inches from origin) ──
DIV_Y  = 140        # E-W divider: top bedrooms+kitchen / bottom ensuites+utility
P1_X   = 86         # N-S left: Bedroom A | Kitchen  AND  Ensuite A | Utility
P2_X   = 168        # N-S right: Kitchen | Bedroom B  AND  Utility | Ensuite B

# Derived interior edges
TOP_S = DIV_Y - INT_T / 2           # south edge of top zone
BOT_N = DIV_Y + INT_T / 2           # north edge of bottom zone
P1_L  = P1_X - INT_T / 2            # east edge of BedA / EnsuiteA
P1_R  = P1_X + INT_T / 2            # west edge of Kitchen / Utility
P2_L  = P2_X - INT_T / 2            # east edge of Kitchen / Utility
P2_R  = P2_X + INT_T / 2            # west edge of BedB / EnsuiteB

# ── Room dimensions (interior clear, inches) ──
def room_sqft(w_in, d_in):
    return (w_in * d_in) / 144

BEDA_W = P1_L - INNER_W             # Bedroom A width
KIT_W  = P2_L - P1_R                # Kitchen / Utility width
BEDB_W = INNER_E - P2_R             # Bedroom B width
TOP_D  = TOP_S - INNER_N            # Top row depth (bedrooms + kitchen)
BOT_D  = INNER_S - BOT_N            # Bottom row depth (ensuites + utility)

# ── Window positions ──
# Kent Atlantic 36"×40" Casement (SKU 1107802) — 7 total
WIN_W    = 36     # window width
WIN_H    = 40     # window height
WIN_SILL = 36     # sill height from floor

# North wall: 1 per bedroom (skip kitchen — door goes there)
NORTH_WIN = [44, 211]
# South wall: 1 in utility area
SOUTH_WIN = [W // 2]
# West wall: 1 in Bedroom A, 1 in Ensuite A
WEST_WIN = [72, 189]
# East wall: 1 in Bedroom B, 1 in Ensuite B
EAST_WIN = [72, 189]

# ── Main entrance door (north wall center, into kitchen) ──
# Dusco Moderna 34"×80" Full Lite Black Steel (HD SKU 1001728121)
DOOR_X   = W // 2    # center X on north wall
DOOR_W   = 34
DOOR_H   = 80

# ── Fixture specs (inches) — scraped from Kent.ca / Home Depot ──
TOILET       = {"w": 15, "d": 28, "h": 28, "price": 269.99,
                "sku": "Kent 1579329", "name": "Clarovista Tidal 1-pc"}
VANITY       = {"w": 24, "d": 18, "h": 34, "price": 549.00,
                "sku": "Kent 1697660", "name": "24\" Vanity Matte Black"}
SHOWER       = {"w": 32, "d": 48, "h": 78, "price": 397.99,
                "sku": "Kent 1023986", "name": "Maax Finesse 48×32"}
WATER_HEATER = {"w": 18, "d": 18, "h": 48, "price": 595.00,
                "sku": "Kent 1766016", "name": "GSW 182L Electric"}
RANGE        = {"w": 24, "d": 25, "h": 36, "price": 1795.00,
                "sku": "Kent 1461599", "name": "Whirlpool 24\" Electric"}
FRIDGE       = {"w": 24, "d": 29, "h": 60, "price": 1445.00,
                "sku": "Kent 1461451", "name": "Whirlpool 24\" BtmFrzr"}
HOOD         = {"w": 24, "d": 20, "h": 10, "price": 1694.00,
                "sku": "Kent 1462473", "name": "Bosch 24\" Under-Cabinet"}
SINK         = {"w": 25, "d": 18, "h": 9,  "price": 299.99,
                "sku": "Kent 1391411", "name": "25\" SS Undermount"}
COUNTER      = {"w": 96, "d": 25, "h": 36, "price": 2800.00}
CONDENSER    = {"w": 33, "d": 12, "h": 24, "price": 1553.00,
                "sku": "Kent 1034429", "name": "Perfect Aire 18kBTU"}
MINI_HEAD    = {"w": 32, "d": 8,  "h": 12}
HRV          = {"w": 24, "d": 17, "h": 12, "price": 1279.00,
                "sku": "Kent 1400849", "name": "Venmar HRV110"}
PANEL        = {"w": 15, "d": 3.75, "h": 20, "price": 156.49,
                "sku": "Kent 1013553", "name": "Schneider QO 100A"}
WASHER       = {"w": 24, "d": 25, "h": 34, "price": 1395.00,
                "sku": "Kent 1462204", "name": "GE 24\" Combo W/D"}
BASEBOARD    = {"w": 66, "d": 3, "h": 8, "price": 102.00,
                "sku": "Kent 1652016", "name": "1500W 66\" Baseboard"}
POCKET_DOOR  = {"w": 30, "d": 2, "h": 80, "price": 159.00,
                "sku": "Kent 1389850"}
DINING_TABLE = {"w": 36, "d": 30, "h": 30}
DINING_CHAIR = {"w": 16, "d": 16, "h": 32}
BED          = {"w": 54, "d": 75, "h": 24}   # Full/Double bed 54×75
NIGHTSTAND   = {"w": 18, "d": 16, "h": 24}

# ── Material colors ──
# Floors — brighter, distinct per room type
COL_LVP       = rgb_int(178, 154, 120)     # Warm oak LVP (visible in plan)
COL_BED_FLOOR = rgb_int(195, 175, 145)     # Lighter warm wood (bedrooms)
COL_TILE      = rgb_int(210, 225, 235)     # Soft blue-white tile (baths)
COL_LNDY_TILE = rgb_int(200, 210, 205)    # Soft green-gray tile (laundry)
COL_KITCHEN   = rgb_int(215, 195, 160)     # Warm kitchen LVP
COL_CEILING   = rgb_int(255, 255, 255)     # Pure White (Sico Evolution)

# Walls
COL_EXT       = rgb_int(115, 135, 110)     # Mitten Oregon Pride vinyl siding
COL_DRYWALL   = rgb_int(240, 240, 240)     # White drywall interior
COL_ACCENT    = rgb_int(70, 90, 90)        # Dark accent wall (kitchen north)

# Fixtures
COL_TOILET    = rgb_int(250, 250, 250)
COL_VANITY    = rgb_int(30, 30, 30)        # Matte black
COL_SHOWER    = rgb_int(235, 235, 240)
COL_WH        = rgb_int(210, 210, 210)
COL_RANGE     = rgb_int(55, 55, 55)        # Black stainless
COL_FRIDGE    = rgb_int(55, 55, 55)
COL_HOOD      = rgb_int(35, 35, 35)
COL_SINK      = rgb_int(175, 180, 185)     # Stainless
COL_COUNTER   = rgb_int(245, 245, 245)     # White laminate top
COL_CABINET   = rgb_int(38, 38, 42)        # IKEA NICKEBO anthracite
COL_TABLE     = rgb_int(140, 100, 60)      # Wood dining table
COL_CHAIR     = rgb_int(60, 60, 60)        # Dark chair
COL_COND      = rgb_int(205, 205, 205)
COL_HEAD      = rgb_int(240, 240, 240)
COL_HRV       = rgb_int(170, 170, 170)
COL_PANEL     = rgb_int(130, 130, 130)
COL_WASHER    = rgb_int(242, 242, 242)
COL_BASEBOARD = rgb_int(240, 240, 240)
COL_DOOR      = rgb_int(20, 20, 30)        # Dusco Moderna matte black
COL_WINDOW    = rgb_int(190, 210, 230)
COL_POCKET    = rgb_int(240, 240, 240)     # White interior door
COL_BED       = rgb_int(180, 165, 150)     # Warm beige bed
COL_PILLOW    = rgb_int(230, 225, 220)     # Off-white pillow
COL_NSTAND    = rgb_int(100, 80, 60)       # Dark wood nightstand


# ═══════════════════════════════════════════════════════
#  XML GENERATION
# ═══════════════════════════════════════════════════════

def build_home_xml():
    """Build the complete Home.xml for Sweet Home 3D."""

    root = ET.Element("home")
    root.set("version", "7200")
    root.set("name", "St. John's 430 sqft Backyard Suite — 97 Mayor Ave")
    root.set("camera", "topCamera")
    root.set("wallHeight", str(cm(CEIL_H)))
    root.set("basePlanLocked", "false")
    root.set("furnitureSortedProperty", "NAME")
    root.set("furnitureDescendingSorted", "false")

    # Furniture table visible columns
    for prop in ["NAME", "WIDTH", "DEPTH", "HEIGHT", "VISIBLE", "PRICE"]:
        p = ET.SubElement(root, "furnitureVisibleProperty")
        p.set("name", prop)

    # ── Environment ──
    env = ET.SubElement(root, "environment")
    env.set("groundColor", color_hex(rgb_int(120, 150, 95)))
    env.set("skyColor", color_hex(rgb_int(195, 220, 248)))
    env.set("lightColor", color_hex(rgb_int(240, 240, 240)))
    env.set("wallsAlpha", "0")
    env.set("drawingMode", "FILL")
    env.set("photoWidth", "1024")
    env.set("photoHeight", "768")
    env.set("photoAspectRatio", "VIEW_3D_RATIO")
    env.set("photoQuality", "2")
    env.set("videoWidth", "640")
    env.set("videoAspectRatio", "RATIO_4_3")
    env.set("videoQuality", "1")
    env.set("videoFrameRate", "25")

    # ── Compass (St. John's NL: 47.56°N, 52.71°W) ──
    compass = ET.SubElement(root, "compass")
    compass.set("x", str(cm(W / 2)))
    compass.set("y", str(cm(D / 2)))
    compass.set("diameter", "100")
    compass.set("northDirection", "0")
    compass.set("longitude", str(round(math.radians(-52.71), 5)))
    compass.set("latitude", str(round(math.radians(47.56), 5)))
    compass.set("timeZone", "America/St_Johns")
    compass.set("visible", "true")

    # ── Cameras ──
    # Observer: standing south of building, looking north
    obs = ET.SubElement(root, "observerCamera")
    obs.set("attribute", "observerCamera")
    obs.set("lens", "PINHOLE")
    obs.set("x", str(cm(W / 2)))
    obs.set("y", str(cm(D + 100)))
    obs.set("z", str(cm(66)))
    obs.set("yaw", str(round(math.pi, 5)))
    obs.set("pitch", str(round(0.12, 5)))
    obs.set("fieldOfView", str(round(math.radians(63), 5)))
    obs.set("time", "0")

    # Top-down plan view
    top = ET.SubElement(root, "camera")
    top.set("attribute", "topCamera")
    top.set("lens", "PINHOLE")
    top.set("x", str(cm(W / 2)))
    top.set("y", str(cm(D / 2)))
    top.set("z", str(cm(480)))
    top.set("yaw", str(round(math.pi, 5)))
    top.set("pitch", str(round(math.pi / 2, 5)))
    top.set("fieldOfView", str(round(math.radians(63), 5)))
    top.set("time", "0")

    # ── Element collectors ──
    furniture_elements = []
    wall_elements = []
    room_elements = []
    dimension_elements = []
    label_elements = []

    wall_counter = [0]
    piece_counter = [0]
    room_counter = [0]
    dim_counter = [0]
    label_counter = [0]
    walls_by_id = {}

    # ═══════════════════════════════════════════
    #  HELPER FUNCTIONS
    # ═══════════════════════════════════════════

    def add_wall(x1, y1, x2, y2, t=EXT_T, h=CEIL_H,
                 left_color=None, right_color=None):
        wall_counter[0] += 1
        wid = f"wall-{wall_counter[0]}"
        w = ET.Element("wall")
        w.set("id", wid)
        w.set("xStart", str(cm(x1)))
        w.set("yStart", str(cm(y1)))
        w.set("xEnd", str(cm(x2)))
        w.set("yEnd", str(cm(y2)))
        w.set("height", str(cm(h)))
        w.set("thickness", str(cm(t)))
        if left_color is not None:
            w.set("leftSideColor", color_hex(left_color))
        if right_color is not None:
            w.set("rightSideColor", color_hex(right_color))
        wall_elements.append(w)
        walls_by_id[wid] = w
        return wid

    def add_room(name, points, floor_color=COL_LVP, ceil_color=COL_CEILING):
        room_counter[0] += 1
        r = ET.Element("room")
        r.set("id", f"room-{room_counter[0]}")
        r.set("name", name)
        r.set("nameVisible", "true")
        r.set("nameAngle", "0")
        r.set("nameXOffset", "0")
        r.set("nameYOffset", "-40")
        r.set("areaVisible", "true")
        r.set("areaAngle", "0")
        r.set("areaXOffset", "0")
        r.set("areaYOffset", "0")
        r.set("floorVisible", "true")
        r.set("floorColor", color_hex(floor_color))
        r.set("ceilingVisible", "true")
        r.set("ceilingColor", color_hex(ceil_color))
        for x, y in points:
            pt = ET.SubElement(r, "point")
            pt.set("x", str(cm(x)))
            pt.set("y", str(cm(y)))
        room_elements.append(r)

    def add_piece(name, x, y, w, d, h, angle=0, elevation=0,
                  color=0xCCCCCC, price=None, desc=None, model="Content/box.obj"):
        piece_counter[0] += 1
        f = ET.Element("pieceOfFurniture")
        f.set("id", f"piece-{piece_counter[0]}")
        f.set("name", name)
        f.set("model", model)
        f.set("x", str(cm(x)))
        f.set("y", str(cm(y)))
        f.set("elevation", str(cm(elevation)))
        f.set("angle", str(round(angle, 5)))
        f.set("width", str(cm(w)))
        f.set("depth", str(cm(d)))
        f.set("height", str(cm(h)))
        f.set("color", color_hex(color))
        f.set("movable", "true")
        f.set("visible", "true")
        f.set("nameVisible", "false")
        f.set("nameAngle", "0")
        f.set("nameXOffset", "0")
        f.set("nameYOffset", "0")
        if price is not None:
            f.set("price", str(round(price, 2)))
        if desc is not None:
            f.set("description", desc)
        furniture_elements.append(f)
        return f

    def add_opening(name, x, y, w, d, h, angle=0, elevation=0,
                    color=0xCCCCCC, is_door=False, model="Content/box.obj"):
        piece_counter[0] += 1
        f = ET.Element("doorOrWindow")
        f.set("id", f"piece-{piece_counter[0]}")
        f.set("name", name)
        f.set("model", model)
        f.set("x", str(cm(x)))
        f.set("y", str(cm(y)))
        f.set("elevation", str(cm(elevation)))
        f.set("angle", str(round(angle, 5)))
        f.set("width", str(cm(w)))
        f.set("depth", str(cm(d)))
        f.set("height", str(cm(h)))
        f.set("color", color_hex(color))
        f.set("movable", "false")
        f.set("visible", "true")
        f.set("nameVisible", "false")
        f.set("nameAngle", "0")
        f.set("nameXOffset", "0")
        f.set("nameYOffset", "0")
        f.set("wallThickness", "1.0")
        f.set("wallDistance", "0.0")
        f.set("cutOutShape", "M0,0 L1,0 L1,1 L0,1 Z")
        f.set("boundToWall", "true")
        if not is_door:
            f.set("wallCutOutOnBothSides", "false")
        furniture_elements.append(f)
        return f

    def add_dim(x1, y1, x2, y2, offset=20):
        dim_counter[0] += 1
        d = ET.Element("dimensionLine")
        d.set("id", f"dim-{dim_counter[0]}")
        d.set("xStart", str(cm(x1)))
        d.set("yStart", str(cm(y1)))
        d.set("xEnd", str(cm(x2)))
        d.set("yEnd", str(cm(y2)))
        d.set("offset", str(cm(offset)))
        dimension_elements.append(d)

    def add_label(text, x, y, angle=0, size=12, color=None):
        label_counter[0] += 1
        lbl = ET.Element("label")
        lbl.set("id", f"label-{label_counter[0]}")
        lbl.set("x", str(cm(x)))
        lbl.set("y", str(cm(y)))
        lbl.set("angle", str(round(angle, 5)))
        if color is not None:
            lbl.set("color", color_hex(color))
        txt = ET.SubElement(lbl, "text")
        txt.text = text
        st = ET.SubElement(lbl, "textStyle")
        st.set("fontSize", str(size))
        label_elements.append(lbl)

    # ═══════════════════════════════════════════
    #  EXTERIOR WALLS (4 walls, connected loop)
    # ═══════════════════════════════════════════
    ws = add_wall(0, D, W, D, EXT_T, CEIL_H, COL_EXT, COL_DRYWALL)    # South
    we = add_wall(W, D, W, 0, EXT_T, CEIL_H, COL_EXT, COL_DRYWALL)    # East
    wn = add_wall(W, 0, 0, 0, EXT_T, CEIL_H, COL_DRYWALL, COL_EXT)    # North
    ww = add_wall(0, 0, 0, D, EXT_T, CEIL_H, COL_EXT, COL_DRYWALL)    # West

    # Corner joints
    walls_by_id[ws].set("wallAtStart", ww)
    walls_by_id[ws].set("wallAtEnd", we)
    walls_by_id[we].set("wallAtStart", ws)
    walls_by_id[we].set("wallAtEnd", wn)
    walls_by_id[wn].set("wallAtStart", we)
    walls_by_id[wn].set("wallAtEnd", ww)
    walls_by_id[ww].set("wallAtStart", wn)
    walls_by_id[ww].set("wallAtEnd", ws)

    # ═══════════════════════════════════════════
    #  INTERIOR PARTITION WALLS (3 walls)
    # ═══════════════════════════════════════════
    iw = COL_DRYWALL  # both sides

    # 1) E-W divider — full width, separates top (beds+kitchen) from bottom (ensuites+utility)
    add_wall(INNER_W, DIV_Y, INNER_E, DIV_Y, INT_T, CEIL_H, iw, iw)

    # 2) N-S left: Bedroom A | Kitchen (top) AND Ensuite A | Utility (bottom)
    add_wall(P1_X, INNER_N, P1_X, INNER_S, INT_T, CEIL_H, iw, iw)

    # 3) N-S right: Kitchen | Bedroom B (top) AND Utility | Ensuite B (bottom)
    add_wall(P2_X, INNER_N, P2_X, INNER_S, INT_T, CEIL_H, iw, iw)

    # ═══════════════════════════════════════════
    #  ROOMS — 6 rooms (3×2 grid)
    # ═══════════════════════════════════════════

    # 1. Bedroom A (top-left)
    add_room("Bedroom A", [
        (INNER_W, INNER_N),
        (P1_L,    INNER_N),
        (P1_L,    TOP_S),
        (INNER_W, TOP_S),
    ], COL_BED_FLOOR)

    # 2. Shared Kitchen (top-center)
    add_room("Shared Kitchen", [
        (P1_R,  INNER_N),
        (P2_L,  INNER_N),
        (P2_L,  TOP_S),
        (P1_R,  TOP_S),
    ], COL_KITCHEN)

    # 3. Bedroom B (top-right)
    add_room("Bedroom B", [
        (P2_R,    INNER_N),
        (INNER_E, INNER_N),
        (INNER_E, TOP_S),
        (P2_R,    TOP_S),
    ], COL_BED_FLOOR)

    # 4. Ensuite A (bottom-left)
    add_room("Ensuite A", [
        (INNER_W, BOT_N),
        (P1_L,    BOT_N),
        (P1_L,    INNER_S),
        (INNER_W, INNER_S),
    ], COL_TILE)

    # 5. Shared Utility Room (bottom-center)
    add_room("Shared Utility Room", [
        (P1_R,  BOT_N),
        (P2_L,  BOT_N),
        (P2_L,  INNER_S),
        (P1_R,  INNER_S),
    ], COL_LNDY_TILE)

    # 6. Ensuite B (bottom-right)
    add_room("Ensuite B", [
        (P2_R,    BOT_N),
        (INNER_E, BOT_N),
        (INNER_E, INNER_S),
        (P2_R,    INNER_S),
    ], COL_TILE)

    # ═══════════════════════════════════════════
    #  DOORS & WINDOWS
    # ═══════════════════════════════════════════

    # ── Main Entrance: North wall center, into Kitchen ──
    add_opening("Dusco Moderna 34×80 Steel Door",
                DOOR_X, 0, DOOR_W, EXT_T, DOOR_H,
                angle=math.pi, color=COL_DOOR, is_door=True,
                model="Content/door.obj")

    # ── Exterior windows: Kent Atlantic 36×40 Casement (7 total) ──
    for wx in NORTH_WIN:
        add_opening("36×40 Casement",
                    wx, 0, WIN_W, EXT_T, WIN_H,
                    angle=math.pi, elevation=WIN_SILL, color=COL_WINDOW,
                    model="Content/window.obj")
    for wy in WEST_WIN:
        add_opening("36×40 Casement",
                    0, wy, WIN_W, EXT_T, WIN_H,
                    angle=-math.pi / 2, elevation=WIN_SILL, color=COL_WINDOW,
                    model="Content/window.obj")
    for wy in EAST_WIN:
        add_opening("36×40 Casement",
                    W, wy, WIN_W, EXT_T, WIN_H,
                    angle=math.pi / 2, elevation=WIN_SILL, color=COL_WINDOW,
                    model="Content/window.obj")
    for wx in SOUTH_WIN:
        add_opening("36×40 Casement",
                    wx, D, WIN_W, EXT_T, WIN_H,
                    angle=0, elevation=WIN_SILL, color=COL_WINDOW,
                    model="Content/window.obj")

    # ── Interior pocket doors (30×80) ──
    PD = POCKET_DOOR

    # Bedroom A → Kitchen (in P1_X partition, upper half)
    add_opening("Pocket Door 30×80",
                P1_X, 70, PD["w"], INT_T, PD["h"],
                angle=math.pi / 2, color=COL_POCKET, is_door=True,
                model="Content/door.obj")

    # Bedroom B → Kitchen (in P2_X partition, upper half)
    add_opening("Pocket Door 30×80",
                P2_X, 70, PD["w"], INT_T, PD["h"],
                angle=math.pi / 2, color=COL_POCKET, is_door=True,
                model="Content/door.obj")

    # Bedroom A → Ensuite A (in DIV_Y partition, left portion)
    add_opening("Pocket Door 30×80",
                44, DIV_Y, PD["w"], INT_T, PD["h"],
                angle=0, color=COL_POCKET, is_door=True,
                model="Content/door.obj")

    # Bedroom B → Ensuite B (in DIV_Y partition, right portion)
    add_opening("Pocket Door 30×80",
                211, DIV_Y, PD["w"], INT_T, PD["h"],
                angle=0, color=COL_POCKET, is_door=True,
                model="Content/door.obj")

    # Kitchen → Utility (in DIV_Y partition, center)
    add_opening("Pocket Door 30×80",
                W / 2, DIV_Y, PD["w"], INT_T, PD["h"],
                angle=0, color=COL_POCKET, is_door=True,
                model="Content/door.obj")

    # ═══════════════════════════════════════════
    #  BEDROOM A FIXTURES (top-left)
    # ═══════════════════════════════════════════
    bedA_x = INNER_W + BED["w"] / 2 + 2    # bed against west wall
    bedA_y = INNER_N + BED["d"] / 2 + 2    # head near north wall

    add_piece("Bed",
              bedA_x, bedA_y,
              BED["w"], BED["d"], BED["h"],
              color=COL_BED, model="Content/bed.obj")

    add_piece("Pillow",
              bedA_x, bedA_y - BED["d"] / 2 + 8,
              BED["w"] - 8, 14, 4,
              elevation=BED["h"], color=COL_PILLOW)

    add_piece("Nightstand",
              bedA_x + BED["w"] / 2 + NIGHTSTAND["w"] / 2 + 2, bedA_y - 15,
              NIGHTSTAND["w"], NIGHTSTAND["d"], NIGHTSTAND["h"],
              color=COL_NSTAND, model="Content/table.obj")

    add_piece("Baseboard",
              INNER_W + BASEBOARD["d"] / 2, (INNER_N + TOP_S) / 2,
              BASEBOARD["w"], BASEBOARD["d"], BASEBOARD["h"],
              angle=math.pi / 2, color=COL_BASEBOARD, price=BASEBOARD["price"])

    # ═══════════════════════════════════════════
    #  BEDROOM B FIXTURES (top-right)
    # ═══════════════════════════════════════════
    bedB_x = INNER_E - BED["w"] / 2 - 2    # bed against east wall
    bedB_y = INNER_N + BED["d"] / 2 + 2    # head near north wall

    add_piece("Bed",
              bedB_x, bedB_y,
              BED["w"], BED["d"], BED["h"],
              color=COL_BED, model="Content/bed.obj")

    add_piece("Pillow",
              bedB_x, bedB_y - BED["d"] / 2 + 8,
              BED["w"] - 8, 14, 4,
              elevation=BED["h"], color=COL_PILLOW)

    add_piece("Nightstand",
              bedB_x - BED["w"] / 2 - NIGHTSTAND["w"] / 2 - 2, bedB_y - 15,
              NIGHTSTAND["w"], NIGHTSTAND["d"], NIGHTSTAND["h"],
              color=COL_NSTAND, model="Content/table.obj")

    add_piece("Baseboard",
              INNER_E - BASEBOARD["d"] / 2, (INNER_N + TOP_S) / 2,
              BASEBOARD["w"], BASEBOARD["d"], BASEBOARD["h"],
              angle=math.pi / 2, color=COL_BASEBOARD, price=BASEBOARD["price"])

    # ═══════════════════════════════════════════
    #  SHARED KITCHEN FIXTURES (top-center)
    # ═══════════════════════════════════════════
    kit_cx = (P1_R + P2_L) / 2
    cab_w = 72  # 6 LF counter (fits kitchen width)
    cab_y = TOP_S - COUNTER["d"] / 2    # counter along divider wall

    add_piece("IKEA METOD+NICKEBO Lower",
              kit_cx, cab_y,
              cab_w, COUNTER["d"], COUNTER["h"],
              color=COL_CABINET, price=COUNTER["price"],
              model="Content/counter.obj")

    add_piece("White Laminate Counter",
              kit_cx, cab_y,
              cab_w + 2, COUNTER["d"] + 1, 1.5,
              elevation=COUNTER["h"], color=COL_COUNTER)

    add_piece("Sink",
              kit_cx + 12, cab_y,
              SINK["w"], SINK["d"], SINK["h"],
              elevation=COUNTER["h"] - SINK["h"],
              color=COL_SINK, price=SINK["price"],
              desc=SINK["name"])

    add_piece("Range",
              kit_cx - 20, cab_y,
              RANGE["w"], RANGE["d"], RANGE["h"],
              color=COL_RANGE, price=RANGE["price"],
              desc=RANGE["name"], model="Content/appliance.obj")

    add_piece("Hood",
              kit_cx - 20, cab_y,
              HOOD["w"], HOOD["d"], HOOD["h"],
              elevation=54, color=COL_HOOD, price=HOOD["price"],
              desc=HOOD["name"])

    add_piece("Fridge",
              P2_L - FRIDGE["d"] / 2, TOP_S - 40,
              FRIDGE["w"], FRIDGE["d"], FRIDGE["h"],
              angle=-math.pi / 2, color=COL_FRIDGE, price=FRIDGE["price"],
              desc=FRIDGE["name"], model="Content/appliance.obj")

    # Dining area (north portion near entrance)
    table_y = INNER_N + 55

    add_piece("Dining Table",
              kit_cx, table_y,
              DINING_TABLE["w"], DINING_TABLE["d"], DINING_TABLE["h"],
              color=COL_TABLE, model="Content/table.obj")

    add_piece("Chair",
              kit_cx - 14, table_y,
              DINING_CHAIR["w"], DINING_CHAIR["d"], DINING_CHAIR["h"],
              color=COL_CHAIR)
    add_piece("Chair",
              kit_cx + 14, table_y,
              DINING_CHAIR["w"], DINING_CHAIR["d"], DINING_CHAIR["h"],
              color=COL_CHAIR)

    # Mini-split head (high on north wall of kitchen)
    add_piece("Mini-Split Head",
              kit_cx, INNER_N + MINI_HEAD["d"] / 2,
              MINI_HEAD["w"], MINI_HEAD["d"], MINI_HEAD["h"],
              elevation=CEIL_H - MINI_HEAD["h"] - 4,
              color=COL_HEAD)

    # ═══════════════════════════════════════════
    #  ENSUITE A FIXTURES (bottom-left)
    # ═══════════════════════════════════════════
    ea_cx = (INNER_W + P1_L) / 2

    add_piece("Shower",
              ea_cx, INNER_S - SHOWER["d"] / 2,
              SHOWER["w"], SHOWER["d"], SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"],
              desc=SHOWER["name"], model="Content/shower.obj")

    add_piece("Toilet",
              INNER_W + TOILET["w"] / 2 + 5, BOT_N + TOILET["d"] / 2 + 5,
              TOILET["w"], TOILET["d"], TOILET["h"],
              color=COL_TOILET, price=TOILET["price"],
              desc=TOILET["name"], model="Content/toilet.obj")

    add_piece("Vanity",
              INNER_W + 40 + VANITY["w"] / 2, BOT_N + VANITY["d"] / 2 + 5,
              VANITY["w"], VANITY["d"], VANITY["h"],
              color=COL_VANITY, price=VANITY["price"],
              desc=VANITY["name"], model="Content/counter.obj")

    # ═══════════════════════════════════════════
    #  ENSUITE B FIXTURES (bottom-right)
    # ═══════════════════════════════════════════
    eb_cx = (P2_R + INNER_E) / 2

    add_piece("Shower",
              eb_cx, INNER_S - SHOWER["d"] / 2,
              SHOWER["w"], SHOWER["d"], SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"],
              desc=SHOWER["name"], model="Content/shower.obj")

    add_piece("Toilet",
              INNER_E - TOILET["w"] / 2 - 5, BOT_N + TOILET["d"] / 2 + 5,
              TOILET["w"], TOILET["d"], TOILET["h"],
              color=COL_TOILET, price=TOILET["price"],
              desc=TOILET["name"], model="Content/toilet.obj")

    add_piece("Vanity",
              INNER_E - 40 - VANITY["w"] / 2, BOT_N + VANITY["d"] / 2 + 5,
              VANITY["w"], VANITY["d"], VANITY["h"],
              color=COL_VANITY, price=VANITY["price"],
              desc=VANITY["name"], model="Content/counter.obj")

    # ═══════════════════════════════════════════
    #  SHARED UTILITY ROOM FIXTURES (bottom-center)
    # ═══════════════════════════════════════════
    util_cx = (P1_R + P2_L) / 2

    add_piece("Washer/Dryer",
              util_cx, INNER_S - WASHER["d"] / 2 - 2,
              WASHER["w"], WASHER["d"], WASHER["h"],
              color=COL_WASHER, price=WASHER["price"],
              desc=WASHER["name"], model="Content/appliance.obj")

    add_piece("Water Heater",
              P1_R + 12, INNER_S - WATER_HEATER["d"] / 2 - 2,
              WATER_HEATER["w"], WATER_HEATER["d"], WATER_HEATER["h"],
              color=COL_WH, price=WATER_HEATER["price"],
              desc=WATER_HEATER["name"])

    add_piece("HRV",
              util_cx, BOT_N + HRV["d"] / 2 + 5,
              HRV["w"], HRV["d"], HRV["h"],
              elevation=CEIL_H - HRV["h"] - 2,
              color=COL_HRV, price=HRV["price"],
              desc=HRV["name"])

    add_piece("Sub-Panel",
              P2_L - PANEL["d"] / 2 - 2, (BOT_N + INNER_S) / 2,
              PANEL["w"], PANEL["d"], PANEL["h"],
              elevation=48, color=COL_PANEL, price=PANEL["price"],
              desc=PANEL["name"])

    # ═══════════════════════════════════════════
    #  EXTERIOR MECHANICAL
    # ═══════════════════════════════════════════
    add_piece("Condenser",
              W + 20, D / 2,
              CONDENSER["w"], CONDENSER["d"], CONDENSER["h"],
              elevation=6, color=COL_COND, price=CONDENSER["price"],
              desc=CONDENSER["name"])

    # ═══════════════════════════════════════════
    #  DIMENSION LINES
    # ═══════════════════════════════════════════
    add_dim(0, D + 24, W, D + 24, offset=10)        # Total width
    add_dim(-24, 0, -24, D, offset=10)               # Total depth

    # ═══════════════════════════════════════════
    #  LABELS — purple room badges (matching reference style)
    # ═══════════════════════════════════════════
    purple = rgb_int(120, 90, 170)
    dark = rgb_int(40, 40, 40)

    def sqm(sqft_val):
        return sqft_val * 0.0929

    # Room name + area labels (centered in each room)
    rooms_labels = [
        ("Bedroom A",           (INNER_W + P1_L) / 2,  (INNER_N + TOP_S) / 2 + 20, BEDA_W, TOP_D),
        ("Shared Kitchen",      (P1_R + P2_L) / 2,     (INNER_N + TOP_S) / 2 + 20, KIT_W, TOP_D),
        ("Bedroom B",           (P2_R + INNER_E) / 2,  (INNER_N + TOP_S) / 2 + 20, BEDB_W, TOP_D),
        ("Ensuite A",           (INNER_W + P1_L) / 2,  (BOT_N + INNER_S) / 2 - 10, BEDA_W, BOT_D),
        ("Shared Utility Room", (P1_R + P2_L) / 2,     (BOT_N + INNER_S) / 2 - 10, KIT_W, BOT_D),
        ("Ensuite B",           (P2_R + INNER_E) / 2,  (BOT_N + INNER_S) / 2 - 10, BEDB_W, BOT_D),
    ]
    for rname, rx, ry, rw, rd in rooms_labels:
        sf = room_sqft(rw, rd)
        sm = sqm(sf)
        add_label(f"{rname}\n{sf:.2f} sq ft / {sm:.0f} sq m",
                  rx, ry, size=11, color=purple)

    # Main Entrance label with arrow
    add_label("Main Entrance",
              DOOR_X, -18, size=13, color=dark)

    # ═══════════════════════════════════════════
    #  ASSEMBLE XML IN CORRECT ORDER
    #  (per HomeXMLExporter: furniture → walls → rooms → dims → labels)
    # ═══════════════════════════════════════════
    for el in furniture_elements:
        root.append(el)
    for el in wall_elements:
        root.append(el)
    for el in room_elements:
        root.append(el)
    for el in dimension_elements:
        root.append(el)
    for el in label_elements:
        root.append(el)

    return root


# ═══════════════════════════════════════════════════════
#  .OBJ (unit box for 3D placeholders)
# ═══════════════════════════════════════════════════════
def generate_box_obj():
    """Basic unit box — SH3D scales to piece w/d/h."""
    return ("# Unit box\n"
            "v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n"
            "v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n"
            "f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")


def generate_toilet_obj():
    """Toilet — tank box + rounded bowl seat."""
    lines = ["# Toilet\n"]
    # Tank (back box): x[-0.5,0.5] y[0.0,0.7] z[-0.5,-0.1]
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 0.7 -0.5\nv -0.5 0.7 -0.5\n")
    lines.append("v -0.5 0.0 -0.1\nv 0.5 0.0 -0.1\nv 0.5 0.7 -0.1\nv -0.5 0.7 -0.1\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Bowl (front, lower): x[-0.4,0.4] y[0.0,0.4] z[-0.1,0.5]
    lines.append("v -0.4 0.0 -0.1\nv 0.4 0.0 -0.1\nv 0.4 0.4 -0.1\nv -0.4 0.4 -0.1\n")
    lines.append("v -0.4 0.0 0.5\nv 0.4 0.0 0.5\nv 0.4 0.4 0.5\nv -0.4 0.4 0.5\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    return "".join(lines)


def generate_shower_obj():
    """Shower enclosure — tall thin walls, open front."""
    lines = ["# Shower enclosure\n"]
    # Back wall
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n")
    lines.append("v -0.5 0.0 -0.45\nv 0.5 0.0 -0.45\nv 0.5 1.0 -0.45\nv -0.5 1.0 -0.45\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Left wall
    lines.append("v -0.5 0.0 -0.5\nv -0.5 0.0 0.5\nv -0.5 1.0 0.5\nv -0.5 1.0 -0.5\n")
    lines.append("v -0.45 0.0 -0.5\nv -0.45 0.0 0.5\nv -0.45 1.0 0.5\nv -0.45 1.0 -0.5\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    # Base tray
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 0.05 -0.5\nv -0.5 0.05 -0.5\n")
    lines.append("v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 0.05 0.5\nv -0.5 0.05 0.5\n")
    lines.append("f 17 18 19 20\nf 21 24 23 22\nf 17 21 22 18\nf 18 22 23 19\nf 19 23 24 20\nf 20 24 21 17\n")
    return "".join(lines)


def generate_counter_obj():
    """Kitchen counter — flat slab on cabinet box."""
    lines = ["# Counter + Cabinet\n"]
    # Cabinet base box
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 0.85 -0.5\nv -0.5 0.85 -0.5\n")
    lines.append("v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 0.85 0.5\nv -0.5 0.85 0.5\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Countertop slab (slightly wider)
    lines.append("v -0.52 0.85 -0.52\nv 0.52 0.85 -0.52\nv 0.52 1.0 -0.52\nv -0.52 1.0 -0.52\n")
    lines.append("v -0.52 0.85 0.52\nv 0.52 0.85 0.52\nv 0.52 1.0 0.52\nv -0.52 1.0 0.52\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    return "".join(lines)


def generate_table_obj():
    """Dining table — top slab on 4 legs."""
    lines = ["# Table\n"]
    # Tabletop
    lines.append("v -0.5 0.85 -0.5\nv 0.5 0.85 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n")
    lines.append("v -0.5 0.85 0.5\nv 0.5 0.85 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # 4 legs (thin posts)
    leg_positions = [(-0.4, -0.4), (0.4, -0.4), (0.4, 0.4), (-0.4, 0.4)]
    vn = 9
    for lx, lz in leg_positions:
        s = 0.04  # leg half-width
        lines.append(f"v {lx-s} 0.0 {lz-s}\nv {lx+s} 0.0 {lz-s}\n"
                     f"v {lx+s} 0.85 {lz-s}\nv {lx-s} 0.85 {lz-s}\n")
        lines.append(f"v {lx-s} 0.0 {lz+s}\nv {lx+s} 0.0 {lz+s}\n"
                     f"v {lx+s} 0.85 {lz+s}\nv {lx-s} 0.85 {lz+s}\n")
        a, b, c, d = vn, vn+1, vn+2, vn+3
        e, f_, g, h = vn+4, vn+5, vn+6, vn+7
        lines.append(f"f {a} {b} {c} {d}\nf {e} {h} {g} {f_}\n"
                     f"f {a} {e} {f_} {b}\nf {b} {f_} {g} {c}\n"
                     f"f {c} {g} {h} {d}\nf {d} {h} {e} {a}\n")
        vn += 8
    return "".join(lines)


def generate_door_obj():
    """Door — thin panel with frame."""
    lines = ["# Door\n"]
    # Door panel
    lines.append("v -0.5 0.0 -0.05\nv 0.5 0.0 -0.05\nv 0.5 1.0 -0.05\nv -0.5 1.0 -0.05\n")
    lines.append("v -0.5 0.0 0.05\nv 0.5 0.0 0.05\nv 0.5 1.0 0.05\nv -0.5 1.0 0.05\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    return "".join(lines)


def generate_window_obj():
    """Window — thin pane with frame border."""
    lines = ["# Window\n"]
    # Glass pane
    lines.append("v -0.5 0.0 -0.02\nv 0.5 0.0 -0.02\nv 0.5 1.0 -0.02\nv -0.5 1.0 -0.02\n")
    lines.append("v -0.5 0.0 0.02\nv 0.5 0.0 0.02\nv 0.5 1.0 0.02\nv -0.5 1.0 0.02\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Frame bars (cross)
    lines.append("v -0.02 0.0 -0.04\nv 0.02 0.0 -0.04\nv 0.02 1.0 -0.04\nv -0.02 1.0 -0.04\n")
    lines.append("v -0.02 0.0 0.04\nv 0.02 0.0 0.04\nv 0.02 1.0 0.04\nv -0.02 1.0 0.04\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    return "".join(lines)


def generate_appliance_obj():
    """Appliance (range/fridge) — box with front face detail."""
    lines = ["# Appliance\n"]
    # Main body
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n")
    lines.append("v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Handle (front protrusion)
    lines.append("v -0.05 0.45 0.5\nv 0.05 0.45 0.5\nv 0.05 0.65 0.5\nv -0.05 0.65 0.5\n")
    lines.append("v -0.05 0.45 0.55\nv 0.05 0.45 0.55\nv 0.05 0.65 0.55\nv -0.05 0.65 0.55\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    return "".join(lines)


def generate_bed_obj():
    """Bed — mattress rectangle + raised pillow section at head."""
    lines = ["# Bed\n"]
    # Mattress body: full box, y[0..0.7]
    lines.append("v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 0.7 -0.5\nv -0.5 0.7 -0.5\n")
    lines.append("v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 0.7 0.5\nv -0.5 0.7 0.5\n")
    lines.append("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")
    # Pillow bump at head (z negative = head end): slightly raised
    lines.append("v -0.4 0.7 -0.5\nv 0.4 0.7 -0.5\nv 0.4 0.85 -0.5\nv -0.4 0.85 -0.5\n")
    lines.append("v -0.4 0.7 -0.3\nv 0.4 0.7 -0.3\nv 0.4 0.85 -0.3\nv -0.4 0.85 -0.3\n")
    lines.append("f 9 10 11 12\nf 13 16 15 14\nf 9 13 14 10\nf 10 14 15 11\nf 11 15 16 12\nf 12 16 13 9\n")
    return "".join(lines)


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
def main():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "stjohns_suite.sh3d")

    print("=" * 60)
    print("  St. John's 430 sqft Backyard Suite — SH3D Generator")
    print("=" * 60)
    print(f"  Footprint:  {W}\" x {D}\" ({W/12:.1f}' x {D/12:.1f}') = 430 sqft")
    print(f"  Ceiling:    {CEIL_H}\" ({CEIL_H/12:.0f}'-0\")")
    print(f"  Ext. walls: {EXT_T}\" (2x6 @ 16\" o.c.)")
    print(f"  Int. walls: {INT_T}\" (2x4 + drywall)")

    root = build_home_xml()
    tree = ET.ElementTree(root)

    xml_buf = io.BytesIO()
    tree.write(xml_buf, encoding="UTF-8", xml_declaration=True)
    xml_bytes = xml_buf.getvalue()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Home.xml", xml_bytes)
        zf.writestr("Content/box.obj", generate_box_obj())
        zf.writestr("Content/toilet.obj", generate_toilet_obj())
        zf.writestr("Content/shower.obj", generate_shower_obj())
        zf.writestr("Content/counter.obj", generate_counter_obj())
        zf.writestr("Content/table.obj", generate_table_obj())
        zf.writestr("Content/door.obj", generate_door_obj())
        zf.writestr("Content/window.obj", generate_window_obj())
        zf.writestr("Content/appliance.obj", generate_appliance_obj())
        zf.writestr("Content/bed.obj", generate_bed_obj())

    walls = root.findall("wall")
    rooms = root.findall("room")
    furn = root.findall("pieceOfFurniture")
    dw = root.findall("doorOrWindow")
    dims = root.findall("dimensionLine")
    labels = root.findall("label")

    print(f"\n  Walls:       {len(walls)}")
    print(f"  Rooms:       {len(rooms)}")
    print(f"  Fixtures:    {len(furn)}")
    print(f"  Doors/Win:   {len(dw)}")
    print(f"  Dimensions:  {len(dims)}")
    print(f"  Labels:      {len(labels)}")
    print(f"  XML size:    {len(xml_bytes):,} bytes")
    print(f"  Output:      {output_path}")
    print(f"  File size:   {os.path.getsize(output_path):,} bytes")

    # Room summary
    print(f"\n{'─' * 50}")
    print("  ROOM LAYOUT")
    print(f"{'─' * 50}")
    rooms_data = [
        ("Bedroom A",      BEDA_W,  TOP_D),
        ("Shared Kitchen", KIT_W,   TOP_D),
        ("Bedroom B",      BEDB_W,  TOP_D),
        ("Ensuite A",      BEDA_W,  BOT_D),
        ("Utility Room",   KIT_W,   BOT_D),
        ("Ensuite B",      BEDB_W,  BOT_D),
    ]
    total_sqft = 0
    for name, w_in, d_in in rooms_data:
        sqft = room_sqft(w_in, d_in)
        total_sqft += sqft
        print(f"  {name:14s} {w_in/12:5.1f}' x {d_in/12:5.1f}' = {sqft:5.0f} sqft")
    print(f"  {'─' * 42}")
    print(f"  {'Total interior':14s}                   {total_sqft:5.0f} sqft")
    print(f"  {'Walls/structure':14s}                   {430 - total_sqft:5.0f} sqft")
    print(f"  {'Gross footprint':14s}                     430 sqft")

    # Fixture pricing
    print(f"\n{'─' * 50}")
    print("  FIXTURE PRICING")
    print(f"{'─' * 50}")
    total_price = 0.0
    for f in furn:
        name = f.get("name", "")
        price = float(f.get("price", "0"))
        if price > 0:
            print(f"  ${price:>8,.2f}  {name}")
            total_price += price
    print(f"  {'─' * 42}")
    print(f"  ${total_price:>8,.2f}  Total placed fixtures")

    print(f"\n  Open in Sweet Home 3D: File > Open > {os.path.basename(output_path)}")


if __name__ == "__main__":
    main()
