#!/usr/bin/env python3
"""
generate_sh3d.py — Generate Sweet Home 3D (.sh3d) file programmatically.

St. John's 430 sqft Backyard Suite — 97 Mayor Ave
2 Bedrooms · 2 Bathrooms · Kitchen · Laundry Room
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
#     x=0  BED1_X  MID_X    x=W
#      ┌──────┬──────┬──────┐  y=0  (North)
#      │      │      │      │
#      │ BED1 │ BATH2│ BED2 │  Back zone
#      │      │      │      │
#      ├──────┴──────┴──┬───┤  y=DIV_Y  (E-W divider)
#      │                │B1 │
#      │    KITCHEN     ├───┤  y=LNDY_Y  (Bath1/Laundry split)
#      │                │LR │
#      │                │   │
#      └──[DOOR]────────┴───┘  y=D  (South, entry)
#
#  6 rooms: Bedroom 1, Bedroom 2, Bathroom 2 (back)
#           Kitchen, Bathroom 1, Laundry (front)

# ── Partition positions (centerline, inches from origin) ──
DIV_Y   = 120       # E-W divider: back bedrooms / front service zone
BED1_X  = 102       # N-S: Bedroom 1 | Bathroom 2  (back zone)
MID_X   = 158       # N-S: Bathroom 2 | Bedroom 2  (back zone)
                     #  AND Kitchen | Bath1+Laundry  (front zone) — CONTINUOUS
LNDY_Y  = 180       # E-W: Bathroom 1 | Laundry  (front-right zone)

# Derived interior edges of each room
# Back zone (y: INNER_N to DIV_Y - INT_T/2)
BACK_S = DIV_Y - INT_T / 2          # 117.75"   south edge of back zone
# Front zone (y: DIV_Y + INT_T/2 to INNER_S)
FRONT_N = DIV_Y + INT_T / 2         # 122.25"   north edge of front zone
# Front-right sub-zones
RIGHT_W = MID_X + INT_T / 2         # 160.25"   west edge of bath1/laundry
BATH1_S = LNDY_Y - INT_T / 2        # 177.75"   south edge of bath 1
LNDY_N  = LNDY_Y + INT_T / 2        # 182.25"   north edge of laundry

# ── Room areas (for labels) ──
def room_sqft(w_in, d_in):
    return (w_in * d_in) / 144

BED1_W_IN = BED1_X - INT_T/2 - INNER_W         # 94.25"
BACK_D_IN = BACK_S - INNER_N                    # 112.25"
BATH2_W_IN = (MID_X - INT_T/2) - (BED1_X + INT_T/2)  # 51.5"
BED2_W_IN = INNER_E - (MID_X + INT_T/2)         # 92.25"

KITCHEN_W_IN = (MID_X - INT_T/2) - INNER_W      # 150.25"
FRONT_D_IN = INNER_S - FRONT_N                  # 112.25"
B1LR_W_IN = INNER_E - RIGHT_W                   # 92.25"
BATH1_D_IN = BATH1_S - FRONT_N                  # 55.5"
LNDY_D_IN = INNER_S - LNDY_N                    # 52.25"

# ── Window positions ──
# Kent Atlantic 36"×40" Casement (SKU 1107802) — 7 total
WIN_W    = 36     # window width
WIN_H    = 40     # window height
WIN_SILL = 36     # sill height from floor

# North wall: 1 per bedroom
NORTH_WIN = [50, 210]
# South wall: 2 in kitchen area
SOUTH_WIN = [60, 120]
# West wall: 1 in bedroom 1
WEST_WIN = [60]
# East wall: 1 in bedroom 2, 1 in bath 1
EAST_WIN = [60, 150]

# ── Front door ──
# Dusco Moderna 34"×80" Full Lite Black Steel (HD SKU 1001728121)
DOOR_X   = 75        # center X on south wall
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

# ── Material colors ──
# Floors
COL_LVP       = rgb_int(61, 42, 22)       # Volcano Pewter dark walnut
COL_TILE      = rgb_int(225, 225, 230)     # White ceramic tile
COL_LNDY_TILE = rgb_int(200, 200, 210)    # Light gray tile (laundry)
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
                  color=0xCCCCCC, price=None, desc=None):
        piece_counter[0] += 1
        f = ET.Element("pieceOfFurniture")
        f.set("id", f"piece-{piece_counter[0]}")
        f.set("name", name)
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
        f.set("nameVisible", "true")
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
                    color=0xCCCCCC, is_door=False):
        piece_counter[0] += 1
        f = ET.Element("doorOrWindow")
        f.set("id", f"piece-{piece_counter[0]}")
        f.set("name", name)
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
    #  INTERIOR PARTITION WALLS
    # ═══════════════════════════════════════════
    iw = COL_DRYWALL  # both sides

    # 1) E-W divider — full width, separates back bedrooms from front zone
    add_wall(INNER_W, DIV_Y, INNER_E, DIV_Y, INT_T, CEIL_H, iw, COL_ACCENT)

    # 2) N-S: Bedroom 1 | Bathroom 2  (back zone only)
    add_wall(BED1_X, INNER_N, BED1_X, DIV_Y, INT_T, CEIL_H, iw, iw)

    # 3) N-S: Bathroom 2 | Bedroom 2  AND  Kitchen | Bath1+Laundry
    #    CONTINUOUS wall from north interior to south interior
    add_wall(MID_X, INNER_N, MID_X, INNER_S, INT_T, CEIL_H, iw, iw)

    # 4) E-W: Bathroom 1 | Laundry  (front-right sub-zone only)
    add_wall(RIGHT_W, LNDY_Y, INNER_E, LNDY_Y, INT_T, CEIL_H, iw, iw)

    # ═══════════════════════════════════════════
    #  ROOMS — 6 rooms
    # ═══════════════════════════════════════════

    # 1. Bedroom 1 (back-west)
    add_room("Bedroom 1", [
        (INNER_W,              INNER_N),
        (BED1_X - INT_T / 2,  INNER_N),
        (BED1_X - INT_T / 2,  BACK_S),
        (INNER_W,              BACK_S),
    ], COL_LVP)

    # 2. Bathroom 2 (back-center, Jack & Jill)
    add_room("Bathroom 2", [
        (BED1_X + INT_T / 2,  INNER_N),
        (MID_X - INT_T / 2,   INNER_N),
        (MID_X - INT_T / 2,   BACK_S),
        (BED1_X + INT_T / 2,  BACK_S),
    ], COL_TILE)

    # 3. Bedroom 2 (back-east)
    add_room("Bedroom 2", [
        (MID_X + INT_T / 2,   INNER_N),
        (INNER_E,              INNER_N),
        (INNER_E,              BACK_S),
        (MID_X + INT_T / 2,   BACK_S),
    ], COL_LVP)

    # 4. Kitchen (front-west, eat-in — the communal space)
    add_room("Kitchen", [
        (INNER_W,              FRONT_N),
        (MID_X - INT_T / 2,   FRONT_N),
        (MID_X - INT_T / 2,   INNER_S),
        (INNER_W,              INNER_S),
    ], COL_LVP)

    # 5. Bathroom 1 (front-right upper)
    add_room("Bathroom 1", [
        (RIGHT_W,   FRONT_N),
        (INNER_E,   FRONT_N),
        (INNER_E,   BATH1_S),
        (RIGHT_W,   BATH1_S),
    ], COL_TILE)

    # 6. Laundry Room (front-right lower)
    add_room("Laundry", [
        (RIGHT_W,   LNDY_N),
        (INNER_E,   LNDY_N),
        (INNER_E,   INNER_S),
        (RIGHT_W,   INNER_S),
    ], COL_LNDY_TILE)

    # ═══════════════════════════════════════════
    #  DOORS & WINDOWS
    # ═══════════════════════════════════════════

    # ── Exterior: Front door (south wall) ──
    add_opening("Dusco Moderna 34×80 Steel Door",
                DOOR_X, D, DOOR_W, EXT_T, DOOR_H,
                angle=0, color=COL_DOOR, is_door=True)

    # ── Exterior windows: Kent Atlantic 36×40 Casement ──
    for wx in SOUTH_WIN:
        add_opening("36×40 Casement (Kent 1107802)",
                    wx, D, WIN_W, EXT_T, WIN_H,
                    angle=0, elevation=WIN_SILL, color=COL_WINDOW)
    for wx in NORTH_WIN:
        add_opening("36×40 Casement (Kent 1107802)",
                    wx, 0, WIN_W, EXT_T, WIN_H,
                    angle=math.pi, elevation=WIN_SILL, color=COL_WINDOW)
    for wy in WEST_WIN:
        add_opening("36×40 Casement (Kent 1107802)",
                    0, wy, WIN_W, EXT_T, WIN_H,
                    angle=-math.pi / 2, elevation=WIN_SILL, color=COL_WINDOW)
    for wy in EAST_WIN:
        add_opening("36×40 Casement (Kent 1107802)",
                    W, wy, WIN_W, EXT_T, WIN_H,
                    angle=math.pi / 2, elevation=WIN_SILL, color=COL_WINDOW)

    # ── Interior pocket doors (Kent 1389850, 30×80) ──
    PD = POCKET_DOOR

    # Bedroom 1 → Kitchen (in E-W divider)
    add_opening("Pocket Door 30×80",
                50, DIV_Y, PD["w"], INT_T, PD["h"],
                angle=0, color=COL_POCKET, is_door=True)

    # Bedroom 2 → Kitchen (in E-W divider)
    add_opening("Pocket Door 30×80",
                210, DIV_Y, PD["w"], INT_T, PD["h"],
                angle=0, color=COL_POCKET, is_door=True)

    # Bathroom 2 door (in BED1_X partition, from Bedroom 1 side)
    add_opening("Pocket Door 30×80",
                BED1_X, 65, PD["w"], INT_T, PD["h"],
                angle=math.pi / 2, color=COL_POCKET, is_door=True)

    # Bathroom 1 → Kitchen (in MID_X partition)
    add_opening("Pocket Door 30×80",
                MID_X, 145, PD["w"], INT_T, PD["h"],
                angle=math.pi / 2, color=COL_POCKET, is_door=True)

    # Laundry → Kitchen (in MID_X partition)
    add_opening("Pocket Door 30×80",
                MID_X, 210, PD["w"], INT_T, PD["h"],
                angle=math.pi / 2, color=COL_POCKET, is_door=True)

    # ═══════════════════════════════════════════
    #  BATHROOM 1 FIXTURES (front-right upper)
    #  Interior: x 160.25→252.5, y 122.25→177.75
    # ═══════════════════════════════════════════

    # Shower against east wall
    add_piece(f"Shower ({SHOWER['sku']})",
              INNER_E - SHOWER["w"] / 2, FRONT_N + SHOWER["d"] / 2,
              SHOWER["w"], SHOWER["d"], SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"],
              desc=SHOWER["name"])

    # Toilet
    add_piece(f"Toilet ({TOILET['sku']})",
              RIGHT_W + 20, BATH1_S - TOILET["d"] / 2 - 2,
              TOILET["w"], TOILET["d"], TOILET["h"],
              color=COL_TOILET, price=TOILET["price"],
              desc=TOILET["name"])

    # Vanity
    add_piece(f"Vanity ({VANITY['sku']})",
              RIGHT_W + 55, BATH1_S - VANITY["d"] / 2 - 2,
              VANITY["w"], VANITY["d"], VANITY["h"],
              color=COL_VANITY, price=VANITY["price"],
              desc=VANITY["name"])

    # ═══════════════════════════════════════════
    #  BATHROOM 2 FIXTURES (back-center)
    #  Interior: x 104.25→155.75, y 5.5→117.75
    # ═══════════════════════════════════════════
    b2_left = BED1_X + INT_T / 2
    b2_right = MID_X - INT_T / 2

    # Toilet against north wall
    add_piece(f"Toilet ({TOILET['sku']})",
              b2_left + 12 + TOILET["w"] / 2, INNER_N + TOILET["d"] / 2,
              TOILET["w"], TOILET["d"], TOILET["h"],
              color=COL_TOILET, price=TOILET["price"],
              desc=TOILET["name"])

    # Vanity next to toilet
    add_piece(f"Vanity ({VANITY['sku']})",
              b2_left + 12 + VANITY["w"] / 2, INNER_N + 34 + VANITY["d"] / 2,
              VANITY["w"], VANITY["d"], VANITY["h"],
              color=COL_VANITY, price=VANITY["price"],
              desc=VANITY["name"])

    # Shower in south end of bath2
    add_piece(f"Shower ({SHOWER['sku']})",
              (b2_left + b2_right) / 2, BACK_S - SHOWER["d"] / 2,
              SHOWER["w"], SHOWER["d"], SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"],
              desc=SHOWER["name"])

    # ═══════════════════════════════════════════
    #  KITCHEN FIXTURES (front-west)
    #  Interior: x 5.5→155.75, y 122.25→234.5
    # ═══════════════════════════════════════════

    # Kitchen counter + cabinets along north wall (divider), L-shape
    cab_y = FRONT_N + COUNTER["d"] / 2     # center of cabinets against divider
    cab_start_x = INNER_W + 8              # 8" from west wall

    # Lower cabinets (8 LF = 96" run)
    add_piece("IKEA METOD+NICKEBO 8LF Lower",
              cab_start_x + COUNTER["w"] / 2, cab_y,
              COUNTER["w"], COUNTER["d"], COUNTER["h"],
              color=COL_CABINET, price=COUNTER["price"],
              desc="IKEA METOD frame + NICKEBO anthracite fronts")

    # Countertop on cabinets
    add_piece("White Laminate Counter 8'",
              cab_start_x + COUNTER["w"] / 2, cab_y,
              COUNTER["w"] + 2, COUNTER["d"] + 1, 1.5,
              elevation=COUNTER["h"], color=COL_COUNTER)

    # Sink in counter
    add_piece(f"Sink ({SINK['sku']})",
              cab_start_x + 50, cab_y,
              SINK["w"], SINK["d"], SINK["h"],
              elevation=COUNTER["h"] - SINK["h"],
              color=COL_SINK, price=SINK["price"],
              desc=SINK["name"])

    # Range
    add_piece(f"Range ({RANGE['sku']})",
              cab_start_x + 24 + RANGE["w"] / 2, cab_y,
              RANGE["w"], RANGE["d"], RANGE["h"],
              color=COL_RANGE, price=RANGE["price"],
              desc=RANGE["name"])

    # Hood above range
    add_piece(f"Hood ({HOOD['sku']})",
              cab_start_x + 24 + HOOD["w"] / 2, cab_y,
              HOOD["w"], HOOD["d"], HOOD["h"],
              elevation=54, color=COL_HOOD, price=HOOD["price"],
              desc=HOOD["name"])

    # Fridge against west wall
    add_piece(f"Fridge ({FRIDGE['sku']})",
              INNER_W + FRIDGE["d"] / 2, FRONT_N + 35 + FRIDGE["w"] / 2,
              FRIDGE["w"], FRIDGE["d"], FRIDGE["h"],
              angle=math.pi / 2, color=COL_FRIDGE, price=FRIDGE["price"],
              desc=FRIDGE["name"])

    # ── Dining area (south portion of kitchen) ──
    table_x = (INNER_W + MID_X - INT_T / 2) / 2   # center of kitchen
    table_y = INNER_S - 40                          # near south wall

    add_piece("Dining Table 36x30",
              table_x, table_y,
              DINING_TABLE["w"], DINING_TABLE["d"], DINING_TABLE["h"],
              color=COL_TABLE, desc="Dining table (seats 2-4)")

    add_piece("Chair",
              table_x - 14, table_y,
              DINING_CHAIR["w"], DINING_CHAIR["d"], DINING_CHAIR["h"],
              color=COL_CHAIR)
    add_piece("Chair",
              table_x + 14, table_y,
              DINING_CHAIR["w"], DINING_CHAIR["d"], DINING_CHAIR["h"],
              color=COL_CHAIR)

    # Mini-split indoor head (high on divider wall)
    add_piece("Mini-Split Head (18kBTU)",
              table_x, FRONT_N + MINI_HEAD["d"] / 2,
              MINI_HEAD["w"], MINI_HEAD["d"], MINI_HEAD["h"],
              elevation=CEIL_H - MINI_HEAD["h"] - 4,
              color=COL_HEAD, desc="Perfect Aire wall-mount head")

    # ═══════════════════════════════════════════
    #  BEDROOM 1 FIXTURES (back-west)
    # ═══════════════════════════════════════════
    bed1_cx = (INNER_W + BED1_X - INT_T / 2) / 2
    bed1_cy = (INNER_N + BACK_S) / 2

    add_piece(f"Baseboard ({BASEBOARD['sku']})",
              INNER_W + BASEBOARD["d"] / 2, bed1_cy,
              BASEBOARD["w"], BASEBOARD["d"], BASEBOARD["h"],
              angle=math.pi / 2, color=COL_BASEBOARD, price=BASEBOARD["price"],
              desc=BASEBOARD["name"])

    # ═══════════════════════════════════════════
    #  BEDROOM 2 FIXTURES (back-east)
    # ═══════════════════════════════════════════

    add_piece(f"Baseboard ({BASEBOARD['sku']})",
              INNER_E - BASEBOARD["d"] / 2, bed1_cy,
              BASEBOARD["w"], BASEBOARD["d"], BASEBOARD["h"],
              angle=math.pi / 2, color=COL_BASEBOARD, price=BASEBOARD["price"],
              desc=BASEBOARD["name"])

    # ═══════════════════════════════════════════
    #  LAUNDRY ROOM FIXTURES (front-right lower)
    #  Interior: x 160.25→252.5, y 182.25→234.5
    # ═══════════════════════════════════════════
    lr_cx = (RIGHT_W + INNER_E) / 2
    lr_cy = (LNDY_N + INNER_S) / 2

    # Washer/Dryer combo against east wall
    add_piece(f"Washer/Dryer ({WASHER['sku']})",
              INNER_E - WASHER["d"] / 2, lr_cy - 5,
              WASHER["w"], WASHER["d"], WASHER["h"],
              angle=math.pi / 2, color=COL_WASHER, price=WASHER["price"],
              desc=WASHER["name"])

    # Water heater
    add_piece(f"Water Heater ({WATER_HEATER['sku']})",
              RIGHT_W + 15, INNER_S - WATER_HEATER["d"] / 2 - 3,
              WATER_HEATER["w"], WATER_HEATER["d"], WATER_HEATER["h"],
              color=COL_WH, price=WATER_HEATER["price"],
              desc=WATER_HEATER["name"])

    # HRV (ceiling-mounted)
    add_piece(f"HRV ({HRV['sku']})",
              lr_cx, LNDY_N + 15,
              HRV["w"], HRV["d"], HRV["h"],
              elevation=CEIL_H - HRV["h"] - 2,
              color=COL_HRV, price=HRV["price"],
              desc=HRV["name"])

    # Sub-panel on west wall of laundry
    add_piece(f"Sub-Panel ({PANEL['sku']})",
              RIGHT_W + PANEL["d"] / 2 + 2, lr_cy + 10,
              PANEL["w"], PANEL["d"], PANEL["h"],
              elevation=48, color=COL_PANEL, price=PANEL["price"],
              desc=PANEL["name"])

    # ═══════════════════════════════════════════
    #  EXTERIOR MECHANICAL
    # ═══════════════════════════════════════════
    add_piece(f"Condenser ({CONDENSER['sku']})",
              W + 20, D / 2,
              CONDENSER["w"], CONDENSER["d"], CONDENSER["h"],
              elevation=6, color=COL_COND, price=CONDENSER["price"],
              desc=CONDENSER["name"])

    # ═══════════════════════════════════════════
    #  DIMENSION LINES — comprehensive callouts
    # ═══════════════════════════════════════════

    # ── Overall building dimensions ──
    add_dim(0, D + 36, W, D + 36, offset=12)        # Total width
    add_dim(-36, 0, -36, D, offset=12)               # Total depth

    # ── Back zone room widths (along north edge) ──
    add_dim(INNER_W, -18, BED1_X - INT_T/2, -18, offset=8)     # Bed 1 width
    add_dim(BED1_X + INT_T/2, -18, MID_X - INT_T/2, -18, 8)    # Bath 2 width
    add_dim(MID_X + INT_T/2, -18, INNER_E, -18, offset=8)      # Bed 2 width

    # ── Back zone depth (along west edge) ──
    add_dim(-18, INNER_N, -18, BACK_S, offset=8)

    # ── Front zone room widths (along south edge) ──
    add_dim(INNER_W, D + 18, MID_X - INT_T/2, D + 18, 8)       # Kitchen width
    add_dim(RIGHT_W, D + 18, INNER_E, D + 18, offset=8)         # Bath1/Laundry width

    # ── Front zone depths (along east edge) ──
    add_dim(W + 18, FRONT_N, W + 18, BATH1_S, offset=8)         # Bath 1 depth
    add_dim(W + 18, LNDY_N, W + 18, INNER_S, offset=8)          # Laundry depth

    # ── Kitchen depth ──
    add_dim(INNER_W - 12, FRONT_N, INNER_W - 12, INNER_S, 8)

    # ── Partition positions (E-W divider) ──
    add_dim(-18, INNER_N, -18, DIV_Y, offset=14)                # Back zone height
    add_dim(-18, DIV_Y, -18, INNER_S, offset=14)                # Front zone height

    # ── Window callouts ──
    for wx in NORTH_WIN:
        add_dim(wx - WIN_W/2, -6, wx + WIN_W/2, -6, offset=4)
    for wx in SOUTH_WIN:
        add_dim(wx - WIN_W/2, D + 6, wx + WIN_W/2, D + 6, 4)

    # ═══════════════════════════════════════════
    #  LABELS — engineering annotations
    # ═══════════════════════════════════════════
    dark = rgb_int(60, 60, 60)
    note_color = rgb_int(120, 120, 120)

    # ── Title block (below the plan) ──
    add_label("ST. JOHN'S 430 sqft BACKYARD SUITE",
              W / 2, D + 55, size=18, color=dark)
    add_label("97 Mayor Ave  -  St. John's, NL  -  2 Bed / 2 Bath / Kitchen / Laundry",
              W / 2, D + 70, size=11, color=note_color)
    add_label("21'-6\" x 20'-0\" footprint  -  8'-0\" ceiling  -  Mono-slope roof 9'-6\" to 7'-0\"",
              W / 2, D + 82, size=10, color=note_color)

    # ── Construction notes ──
    notes_x = W + 50
    notes_y = 10
    add_label("CONSTRUCTION NOTES", notes_x, notes_y, size=14, color=dark)
    notes = [
        "Exterior: 2x6 @ 16\" o.c., R-24 mineral wool",
        "Interior: 2x4 @ 16\" o.c., R-12 batt",
        "Ceiling: R-60 blown cellulose",
        "Foundation: 4\" slab-on-grade, R-10 XPS perimeter",
        "Roof: Mono-slope 3:12, standing seam metal",
        "Windows: Kent Atlantic 36x40 casement (x7)",
        "Entry: Dusco Moderna 34x80 full-lite steel",
        "Interior: 30x80 pocket doors (x5)",
        "Siding: Mitten Oregon Pride vinyl",
        "Floor: Volcano Pewter LVP (bed/kit), ceramic tile (bath/lndy)",
        "HVAC: 18kBTU mini-split + HRV + baseboard backup",
        "Plumbing: PEX manifold, 182L electric HWT",
        "Electrical: 100A sub-panel, 200A service at main house",
        "NL Building Code 2019 + Energy Code compliance",
    ]
    for i, note in enumerate(notes):
        add_label(f"  {note}",
                  notes_x, notes_y + 16 + i * 13, size=9, color=note_color)

    # ── Room labels with specs ──
    # Bedroom 1
    b1_area = room_sqft(BED1_W_IN, BACK_D_IN)
    add_label(f"BEDROOM 1  ({b1_area:.0f} sqft)",
              (INNER_W + BED1_X - INT_T/2) / 2,
              (INNER_N + BACK_S) / 2 - 12, size=11, color=dark)
    add_label("LVP floor  |  1500W baseboard",
              (INNER_W + BED1_X - INT_T/2) / 2,
              (INNER_N + BACK_S) / 2 + 2, size=8, color=note_color)

    # Bathroom 2
    b2_area = room_sqft(BATH2_W_IN, BACK_D_IN)
    add_label(f"BATH 2  ({b2_area:.0f} sqft)",
              (BED1_X + INT_T/2 + MID_X - INT_T/2) / 2,
              (INNER_N + BACK_S) / 2 - 6, size=10, color=dark)
    add_label("Ceramic tile  |  48x32 shower",
              (BED1_X + INT_T/2 + MID_X - INT_T/2) / 2,
              (INNER_N + BACK_S) / 2 + 6, size=7, color=note_color)

    # Bedroom 2
    b2b_area = room_sqft(BED2_W_IN, BACK_D_IN)
    add_label(f"BEDROOM 2  ({b2b_area:.0f} sqft)",
              (MID_X + INT_T/2 + INNER_E) / 2,
              (INNER_N + BACK_S) / 2 - 12, size=11, color=dark)
    add_label("LVP floor  |  1500W baseboard",
              (MID_X + INT_T/2 + INNER_E) / 2,
              (INNER_N + BACK_S) / 2 + 2, size=8, color=note_color)

    # Kitchen
    k_area = room_sqft(KITCHEN_W_IN, FRONT_D_IN)
    add_label(f"KITCHEN  ({k_area:.0f} sqft)",
              (INNER_W + MID_X - INT_T/2) / 2,
              (FRONT_N + INNER_S) / 2 - 20, size=13, color=dark)
    add_label("Eat-in  |  IKEA METOD + NICKEBO anthracite",
              (INNER_W + MID_X - INT_T/2) / 2,
              (FRONT_N + INNER_S) / 2 - 6, size=9, color=note_color)
    add_label("8 LF counter | 24\" range | 24\" fridge | SS sink",
              (INNER_W + MID_X - INT_T/2) / 2,
              (FRONT_N + INNER_S) / 2 + 6, size=8, color=note_color)
    add_label("LVP floor  |  Mini-split head (18kBTU)",
              (INNER_W + MID_X - INT_T/2) / 2,
              (FRONT_N + INNER_S) / 2 + 17, size=8, color=note_color)

    # Bathroom 1
    b1a_area = room_sqft(B1LR_W_IN, BATH1_D_IN)
    add_label(f"BATH 1  ({b1a_area:.0f} sqft)",
              (RIGHT_W + INNER_E) / 2,
              (FRONT_N + BATH1_S) / 2 - 4, size=10, color=dark)
    add_label("Ceramic tile  |  48x32 shower",
              (RIGHT_W + INNER_E) / 2,
              (FRONT_N + BATH1_S) / 2 + 7, size=7, color=note_color)

    # Laundry
    lr_area = room_sqft(B1LR_W_IN, LNDY_D_IN)
    add_label(f"LAUNDRY  ({lr_area:.0f} sqft)",
              (RIGHT_W + INNER_E) / 2,
              (LNDY_N + INNER_S) / 2 - 8, size=10, color=dark)
    add_label("24\" combo W/D | HWT | HRV | panel",
              (RIGHT_W + INNER_E) / 2,
              (LNDY_N + INNER_S) / 2 + 4, size=7, color=note_color)

    # ── Fixture legend (bottom-right) ──
    leg_x = W + 50
    leg_y = D - 60
    add_label("FIXTURE SCHEDULE", leg_x, leg_y, size=13, color=dark)
    fixtures_list = [
        f"Toilets (x2): {TOILET['name']} -- ${TOILET['price']:.2f} ea",
        f"Vanities (x2): {VANITY['name']} -- ${VANITY['price']:.2f} ea",
        f"Showers (x2): {SHOWER['name']} -- ${SHOWER['price']:.2f} ea",
        f"Range: {RANGE['name']} -- ${RANGE['price']:.2f}",
        f"Fridge: {FRIDGE['name']} -- ${FRIDGE['price']:.2f}",
        f"Hood: {HOOD['name']} -- ${HOOD['price']:.2f}",
        f"Sink: {SINK['name']} -- ${SINK['price']:.2f}",
        f"W/D: {WASHER['name']} -- ${WASHER['price']:.2f}",
        f"HWT: {WATER_HEATER['name']} -- ${WATER_HEATER['price']:.2f}",
        f"HRV: {HRV['name']} -- ${HRV['price']:.2f}",
        f"Panel: {PANEL['name']} -- ${PANEL['price']:.2f}",
        f"Mini-split: {CONDENSER['name']} -- ${CONDENSER['price']:.2f}",
        f"Cabinets: IKEA METOD+NICKEBO 8LF -- ${COUNTER['price']:.2f}",
    ]
    for i, line in enumerate(fixtures_list):
        add_label(line, leg_x, leg_y + 15 + i * 12, size=8, color=note_color)

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
    return ("# Unit box — SH3D scales to piece w/d/h\n"
            "v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n"
            "v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n"
            "f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n")


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
        ("Bedroom 1",  BED1_W_IN,    BACK_D_IN),
        ("Bathroom 2", BATH2_W_IN,   BACK_D_IN),
        ("Bedroom 2",  BED2_W_IN,    BACK_D_IN),
        ("Kitchen",    KITCHEN_W_IN, FRONT_D_IN),
        ("Bathroom 1", B1LR_W_IN,    BATH1_D_IN),
        ("Laundry",    B1LR_W_IN,    LNDY_D_IN),
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
