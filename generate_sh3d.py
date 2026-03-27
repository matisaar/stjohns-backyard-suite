#!/usr/bin/env python3
"""
generate_sh3d.py — Generate Sweet Home 3D (.sh3d) file programmatically.

St. John's 430 sqft Backyard Suite — 97 Mayor Ave
All dimensions from Kent.ca and Home Depot product listings.

Usage:
    python3 generate_sh3d.py
    → outputs stjohns_suite.sh3d
    → open in Sweet Home 3D (sweethome3d.com)

Workflow:
    1. Edit dimensions/positions below
    2. Re-run this script
    3. Re-open .sh3d in Sweet Home 3D
    4. Repeat until perfect

To add real 3D product models:
    - Download .obj from 3dwarehouse.sketchup.com or bimobject.com
    - In SH3D: Furniture > Import Furniture, replace any box placeholder
"""

import zipfile
import xml.etree.ElementTree as ET
import io
import math
import os

# ═══════════════════════════════════════════════════════
#  UNIT CONVERSION
# ═══════════════════════════════════════════════════════
# Sweet Home 3D stores everything in centimeters.
# We define in inches (construction standard) and convert.
CM = 2.54  # 1 inch = 2.54 cm

def cm(inches):
    """Convert inches to centimeters for SH3D."""
    return round(inches * CM, 2)

def rgb_int(r, g, b):
    """RGB (0-255) to SH3D integer color."""
    return (r << 16) | (g << 8) | b


# ═══════════════════════════════════════════════════════
#  BUILDING CONFIGURATION — EDIT THESE TO ITERATE
# ═══════════════════════════════════════════════════════

# Overall building (outer dimensions, inches)
W = 258              # 21'-6" width (east-west)
D = 240              # 20'-0" depth (north-south)
EXT_T = 5.5          # 2x6 exterior wall thickness
INT_T = 4.5          # 2x4 + drywall interior partition
CEIL_H = 96          # 8' ceiling height

# Plan view coordinate convention:
#   Origin (0,0) = NORTHWEST corner (back-left)
#   X increases EAST (right)
#   Y increases SOUTH (down = toward front door)
#
#     (0,0)─────────────────(W,0)
#       │  BACK (bedrooms)     │
#       │                      │
#  DIV_Y├──────────────────────┤
#       │  FRONT (kitchen/     │
#       │   living + bath)     │
#     (0,D)──[door]──────────(W,D)

# ── Partition positions (inches from origin) ──
DIV_Y = 108                    # E-W divider: back bedrooms / front living
BED1_X = 102                   # N-S: Bedroom 1 | Bathroom 2
BATH2_X = 156                  # N-S: Bathroom 2 | Bedroom 2
BATH1_X = 190                  # N-S: Living | Bathroom 1 (front zone)

# Interior edges (after wall thicknesses)
INNER_N = EXT_T                # 5.5" — inner face of north wall
INNER_S = D - EXT_T            # 234.5" — inner face of south wall
INNER_W = EXT_T                # 5.5"
INNER_E = W - EXT_T            # 252.5"

# ── Window positions (center X or Y along respective wall) ──
# Kent Atlantic 36"×40" Casement (SKU 1107802) — 6 total
WIN_W = 36     # window width
WIN_H = 40     # window height
WIN_SILL = 36  # sill height from floor

# South wall (front, y ≈ D) — 2 windows
SOUTH_WIN = [130, 210]

# North wall (back, y ≈ 0) — 2 windows (one per bedroom)
NORTH_WIN = [50, 210]

# West wall (x ≈ 0) — 1 window (Bedroom 1)
WEST_WIN = [54]

# East wall (x ≈ W) — 1 window (Bedroom 2)
EAST_WIN = [54]

# ── Front door position (center X on south wall) ──
# Dusco Moderna 34"×80" (Home Depot SKU 1001728121)
DOOR_X = 50
DOOR_W_IN = 34
DOOR_H_IN = 80

# ── Fixture dimensions (inches) — all from Kent.ca/HD product pages ──

# Toilet: Clarovista Tidal 1-piece (Kent SKU 1579329)
TOILET = {"w": 15, "d": 28, "h": 28, "price": 269.99}

# Vanity: 24" w/ Drawer matte black (Kent SKU 1697660)
VANITY = {"w": 24, "d": 18, "h": 34, "price": 549.00}

# Shower: Maax Finesse 4832 base (Kent SKU 1023986)
SHOWER = {"w": 32, "d": 48, "h": 78, "price": 397.99}

# Water Heater: GSW 182L (Kent SKU 1766016) — 18" dia, approx as square
WATER_HEATER = {"w": 18, "d": 18, "h": 48, "price": 595.00}

# Range: Whirlpool 24" Electric (Kent SKU 1461599)
RANGE = {"w": 24, "d": 25, "h": 36, "price": 1795.00}

# Fridge: Whirlpool 24" Bottom-Freezer (Kent SKU 1461451)
FRIDGE = {"w": 24, "d": 29, "h": 60, "price": 1445.00}

# Range Hood: Bosch 24" Under-Cabinet (Kent SKU 1462473)
HOOD = {"w": 24, "d": 20, "h": 10, "price": 1694.00}

# Kitchen Sink: 25" Undermount SS (Kent SKU 1391411)
SINK = {"w": 25, "d": 18, "h": 9, "price": 299.99}

# Kitchen Cabinets+Counter: IKEA METOD/NICKEBO 8LF + laminate top
COUNTER = {"w": 96, "d": 25, "h": 36, "price": 2800.00}

# Mini-split condenser: Perfect Aire 18kBTU (Kent SKU 1034429)
CONDENSER = {"w": 33, "d": 12, "h": 24, "price": 1553.00}

# Mini-split indoor head
MINISPLIT_HEAD = {"w": 32, "d": 8, "h": 12}

# HRV: Venmar HRV110 (Kent SKU 1400849)
HRV = {"w": 24, "d": 17, "h": 12, "price": 1279.00}

# Sub-panel: Schneider QO 100A (Kent SKU 1013553)
PANEL = {"w": 15, "d": 3.75, "h": 20, "price": 156.49}

# Washer/Dryer: GE 24" Combo (Kent SKU 1462204)
WASHER = {"w": 24, "d": 25, "h": 34, "price": 1395.00}

# Baseboard heater: 1500W 66" (Kent SKU 1652016)
BASEBOARD = {"w": 66, "d": 3, "h": 8, "price": 102.00}

# Pocket door: 30"×80" (Kent SKU 1389850)
POCKET_DOOR = {"w": 30, "d": 2, "h": 80, "price": 159.00}


# ── Floor colors ──
COL_LVP = rgb_int(61, 42, 22)       # Volcano Pewter dark walnut (Kent 1080257-PWT)
COL_TILE = rgb_int(240, 240, 245)    # White ceramic tile (Kent 1035109)
COL_CONCRETE = rgb_int(170, 170, 170)
COL_CEILING = rgb_int(255, 255, 255) # Pure White (Sico Evolution)

# ── Furniture colors ──
COL_TOILET = rgb_int(250, 250, 250)
COL_VANITY = rgb_int(30, 30, 30)      # Matte black
COL_SHOWER = rgb_int(242, 242, 245)
COL_WH = rgb_int(220, 220, 220)
COL_RANGE = rgb_int(80, 80, 80)       # Black stainless
COL_FRIDGE = rgb_int(80, 80, 80)
COL_HOOD = rgb_int(40, 40, 40)
COL_SINK = rgb_int(180, 185, 190)     # Stainless
COL_COUNTER = rgb_int(250, 250, 250)  # White laminate
COL_CABINET = rgb_int(38, 38, 42)     # IKEA NICKEBO anthracite
COL_COND = rgb_int(215, 215, 215)
COL_HEAD = rgb_int(245, 245, 245)
COL_HRV = rgb_int(180, 180, 180)
COL_PANEL_C = rgb_int(140, 140, 140)
COL_WASHER_C = rgb_int(245, 245, 245)
COL_BASEBOARD_C = rgb_int(245, 245, 245)
COL_DOOR = rgb_int(20, 20, 30)        # Dusco Moderna matte black
COL_WINDOW = rgb_int(200, 220, 235)
COL_POCKET = rgb_int(245, 245, 245)   # White interior door


# ═══════════════════════════════════════════════════════
#  XML GENERATION
# ═══════════════════════════════════════════════════════

def build_home_xml():
    """Build the complete Home.xml for Sweet Home 3D."""

    root = ET.Element("home")
    root.set("version", "5300")
    root.set("name", "St. John's 430sqft Backyard Suite")
    root.set("wallHeight", str(cm(CEIL_H)))
    root.set("basePlanLocked", "false")
    root.set("furnitureSortedProperty", "NAME")
    root.set("furnitureDescendingSorted", "false")

    # Visible columns in furniture table
    for prop in ["NAME", "WIDTH", "DEPTH", "HEIGHT", "VISIBLE", "PRICE"]:
        p = ET.SubElement(root, "furnitureVisibleProperty")
        p.set("name", prop)

    # ── State tracking ──
    wall_counter = [0]
    walls_by_id = {}

    # ── WALL HELPER ──
    def add_wall(x1, y1, x2, y2, t=EXT_T, h=CEIL_H,
                 left_color=None, right_color=None):
        wall_counter[0] += 1
        wid = f"wall-{wall_counter[0]}"

        w = ET.SubElement(root, "wall")
        w.set("id", wid)
        w.set("xStart", str(cm(x1)))
        w.set("yStart", str(cm(y1)))
        w.set("xEnd", str(cm(x2)))
        w.set("yEnd", str(cm(y2)))
        w.set("height", str(cm(h)))
        w.set("thickness", str(cm(t)))

        if left_color is not None:
            w.set("leftSideColor", str(left_color))
        if right_color is not None:
            w.set("rightSideColor", str(right_color))

        walls_by_id[wid] = w
        return wid

    # ── ROOM HELPER ──
    def add_room(name, points, floor_color=COL_LVP, ceil_color=COL_CEILING):
        room = ET.SubElement(root, "room")
        room.set("name", name)
        room.set("nameVisible", "true")
        room.set("nameAngle", "0")
        room.set("nameXOffset", "0")
        room.set("nameYOffset", "-10")
        room.set("areaVisible", "true")
        room.set("areaAngle", "0")
        room.set("areaXOffset", "0")
        room.set("areaYOffset", "10")
        room.set("floorVisible", "true")
        room.set("floorColor", str(floor_color))
        room.set("ceilingVisible", "true")
        room.set("ceilingColor", str(ceil_color))
        for x, y in points:
            pt = ET.SubElement(room, "point")
            pt.set("x", str(cm(x)))
            pt.set("y", str(cm(y)))

    # ── FURNITURE HELPER ──
    # Note: without a 'model' attribute, items appear in plan view as
    # labeled colored rectangles and in the furniture list. In 3D view
    # they'll be invisible — drag a model from SH3D's library or
    # 3dwarehouse.sketchup.com to replace them.
    def add_piece(name, x, y, w, d, h, angle=0, elevation=0,
                  color=0xCCCCCC, price=None, model_ref=None):
        """Place a furniture piece. x,y = center position in inches."""
        f = ET.SubElement(root, "pieceOfFurniture")
        f.set("name", name)
        f.set("nameVisible", "true")
        f.set("nameAngle", "0")
        f.set("nameXOffset", "0")
        f.set("nameYOffset", "0")
        f.set("x", str(cm(x)))
        f.set("y", str(cm(y)))
        f.set("elevation", str(cm(elevation)))
        f.set("angle", str(round(angle, 5)))
        f.set("width", str(cm(w)))
        f.set("depth", str(cm(d)))
        f.set("height", str(cm(h)))
        f.set("color", str(color))
        f.set("movable", "true")
        f.set("visible", "true")
        if price is not None:
            f.set("price", str(round(price, 2)))
        if model_ref:
            f.set("model", model_ref)
        return f

    # ── DOOR/WINDOW HELPER ──
    def add_opening(name, x, y, w, d, h, angle=0, elevation=0,
                    color=0xCCCCCC, is_door=False):
        """Place a door or window that cuts through a wall."""
        tag = "doorOrWindow"
        f = ET.SubElement(root, tag)
        f.set("name", name)
        f.set("nameVisible", "false")
        f.set("x", str(cm(x)))
        f.set("y", str(cm(y)))
        f.set("elevation", str(cm(elevation)))
        f.set("angle", str(round(angle, 5)))
        f.set("width", str(cm(w)))
        f.set("depth", str(cm(d)))
        f.set("height", str(cm(h)))
        f.set("color", str(color))
        f.set("movable", "false")
        f.set("visible", "true")
        f.set("doorOrWindow", "true")
        f.set("wallThickness", "1.0")
        f.set("wallDistance", "0.0")
        f.set("cutOutShape", "M0,0 L1,0 L1,1 L0,1 Z")
        if not is_door:
            f.set("wallCutOutOnBothSides", "false")
        return f

    # ── DIMENSION LINE HELPER ──
    def add_dimension(x1, y1, x2, y2, offset=20):
        dim = ET.SubElement(root, "dimensionLine")
        dim.set("xStart", str(cm(x1)))
        dim.set("yStart", str(cm(y1)))
        dim.set("xEnd", str(cm(x2)))
        dim.set("yEnd", str(cm(y2)))
        dim.set("offset", str(cm(offset)))

    # ── LABEL HELPER ──
    def add_label(text, x, y, angle=0, size=14):
        lbl = ET.SubElement(root, "label")
        lbl.set("x", str(cm(x)))
        lbl.set("y", str(cm(y)))
        lbl.set("angle", str(round(angle, 5)))
        lbl.set("text", text)
        lbl.set("style", f"font-size:{size}")

    # ══════════════════════════════════════════════
    #  EXTERIOR WALLS
    # ══════════════════════════════════════════════
    # Wall centerlines at edge of building footprint.
    # SH3D applies thickness symmetrically around centerline.

    ext_color = rgb_int(135, 155, 135)   # Mitten Oregon Pride siding
    int_color = rgb_int(240, 240, 240)   # White drywall interior

    # South wall (front, runs E-W at y=D)
    w_s = add_wall(0, D, W, D, EXT_T, CEIL_H, ext_color, int_color)
    # East wall (right, runs N-S at x=W)
    w_e = add_wall(W, D, W, 0, EXT_T, CEIL_H, ext_color, int_color)
    # North wall (back, runs E-W at y=0)
    w_n = add_wall(W, 0, 0, 0, EXT_T, CEIL_H, int_color, ext_color)
    # West wall (left, runs E-W at x=0)
    w_w = add_wall(0, 0, 0, D, EXT_T, CEIL_H, ext_color, int_color)

    # Connect corners
    walls_by_id[w_s].set("wallAtStart", w_w)
    walls_by_id[w_s].set("wallAtEnd", w_e)
    walls_by_id[w_e].set("wallAtStart", w_s)
    walls_by_id[w_e].set("wallAtEnd", w_n)
    walls_by_id[w_n].set("wallAtStart", w_e)
    walls_by_id[w_n].set("wallAtEnd", w_w)
    walls_by_id[w_w].set("wallAtStart", w_n)
    walls_by_id[w_w].set("wallAtEnd", w_s)

    # ══════════════════════════════════════════════
    #  INTERIOR PARTITION WALLS
    # ══════════════════════════════════════════════
    iw_color = rgb_int(240, 240, 240)

    # E-W divider: separates back bedrooms from front living (full width)
    add_wall(EXT_T, DIV_Y, W - EXT_T, DIV_Y, INT_T, CEIL_H, iw_color, iw_color)

    # N-S: Bedroom 1 | Bathroom 2 (in back zone)
    add_wall(BED1_X, EXT_T, BED1_X, DIV_Y, INT_T, CEIL_H, iw_color, iw_color)

    # N-S: Bathroom 2 | Bedroom 2 (in back zone)
    add_wall(BATH2_X, EXT_T, BATH2_X, DIV_Y, INT_T, CEIL_H, iw_color, iw_color)

    # N-S: Kitchen/Living | Bathroom 1 (in front zone, full height from DIV to south wall)
    add_wall(BATH1_X, DIV_Y, BATH1_X, D - EXT_T, INT_T, CEIL_H, iw_color, iw_color)

    # ══════════════════════════════════════════════
    #  ROOMS (floor polygons)
    # ══════════════════════════════════════════════
    # Each room = polygon of inner wall face coordinates

    # Bedroom 1 (back-left)
    add_room("Bedroom 1", [
        (INNER_W, INNER_N),
        (BED1_X - INT_T/2, INNER_N),
        (BED1_X - INT_T/2, DIV_Y - INT_T/2),
        (INNER_W, DIV_Y - INT_T/2),
    ], COL_LVP)

    # Bathroom 2 (back-center)
    add_room("Bathroom 2", [
        (BED1_X + INT_T/2, INNER_N),
        (BATH2_X - INT_T/2, INNER_N),
        (BATH2_X - INT_T/2, DIV_Y - INT_T/2),
        (BED1_X + INT_T/2, DIV_Y - INT_T/2),
    ], COL_TILE)

    # Bedroom 2 (back-right)
    add_room("Bedroom 2", [
        (BATH2_X + INT_T/2, INNER_N),
        (INNER_E, INNER_N),
        (INNER_E, DIV_Y - INT_T/2),
        (BATH2_X + INT_T/2, DIV_Y - INT_T/2),
    ], COL_LVP)

    # Kitchen / Living Room (front-left, large open plan)
    add_room("Kitchen / Living", [
        (INNER_W, DIV_Y + INT_T/2),
        (BATH1_X - INT_T/2, DIV_Y + INT_T/2),
        (BATH1_X - INT_T/2, INNER_S),
        (INNER_W, INNER_S),
    ], COL_LVP)

    # Bathroom 1 (front-right)
    add_room("Bathroom 1", [
        (BATH1_X + INT_T/2, DIV_Y + INT_T/2),
        (INNER_E, DIV_Y + INT_T/2),
        (INNER_E, INNER_S),
        (BATH1_X + INT_T/2, INNER_S),
    ], COL_TILE)

    # ══════════════════════════════════════════════
    #  DOORS & WINDOWS
    # ══════════════════════════════════════════════

    # ── Front Door: Dusco Moderna 34"×80" Full Lite Black Steel ──
    # Home Depot SKU 1001728121 — on south wall
    add_opening("Dusco Moderna 34×80 Door",
                x=DOOR_X, y=D, w=DOOR_W_IN, d=EXT_T, h=DOOR_H_IN,
                angle=0, elevation=0, color=COL_DOOR, is_door=True)

    # ── Windows: Kent Atlantic 36"×40" Casement (SKU 1107802) ──
    # South wall (front) — 2 windows
    for wx in SOUTH_WIN:
        add_opening(f"Casement 36×40 (SKU 1107802)",
                    x=wx, y=D, w=WIN_W, d=EXT_T, h=WIN_H,
                    angle=0, elevation=WIN_SILL, color=COL_WINDOW)

    # North wall (back) — 2 windows (1 per bedroom)
    for wx in NORTH_WIN:
        add_opening(f"Casement 36×40 (SKU 1107802)",
                    x=wx, y=0, w=WIN_W, d=EXT_T, h=WIN_H,
                    angle=math.pi, elevation=WIN_SILL, color=COL_WINDOW)

    # West wall — 1 window (Bedroom 1)
    for wy in WEST_WIN:
        add_opening(f"Casement 36×40 (SKU 1107802)",
                    x=0, y=wy, w=WIN_W, d=EXT_T, h=WIN_H,
                    angle=-math.pi/2, elevation=WIN_SILL, color=COL_WINDOW)

    # East wall — 1 window (Bedroom 2)
    for wy in EAST_WIN:
        add_opening(f"Casement 36×40 (SKU 1107802)",
                    x=W, y=wy, w=WIN_W, d=EXT_T, h=WIN_H,
                    angle=math.pi/2, elevation=WIN_SILL, color=COL_WINDOW)

    # ── Interior Pocket Doors (Kent SKU 1389850) ──
    # Bedroom 1 door (in E-W divider wall at y=DIV_Y)
    add_opening("Pocket Door 30×80", x=50, y=DIV_Y,
                w=POCKET_DOOR["w"], d=INT_T, h=POCKET_DOOR["h"],
                angle=0, elevation=0, color=COL_POCKET, is_door=True)

    # Bedroom 2 door
    add_opening("Pocket Door 30×80", x=200, y=DIV_Y,
                w=POCKET_DOOR["w"], d=INT_T, h=POCKET_DOOR["h"],
                angle=0, elevation=0, color=COL_POCKET, is_door=True)

    # Bathroom 2 door (in BED1_X partition)
    add_opening("Pocket Door 30×80", x=BED1_X, y=40,
                w=POCKET_DOOR["w"], d=INT_T, h=POCKET_DOOR["h"],
                angle=math.pi/2, elevation=0, color=COL_POCKET, is_door=True)

    # Bathroom 1 door (in BATH1_X partition)
    add_opening("Pocket Door 30×80", x=BATH1_X, y=170,
                w=POCKET_DOOR["w"], d=INT_T, h=POCKET_DOOR["h"],
                angle=math.pi/2, elevation=0, color=COL_POCKET, is_door=True)

    # ══════════════════════════════════════════════
    #  BATHROOM 1 FIXTURES (front-right zone)
    # ══════════════════════════════════════════════
    # Room interior: x = 192.25 to 252.5, y = 110.25 to 234.5
    b1_cx = (BATH1_X + INT_T/2 + INNER_E) / 2   # center X of bath1
    b1_left = BATH1_X + INT_T/2 + 2              # 2" clearance from wall

    # Toilet against east wall
    add_piece("Toilet (Kent 1579329)",
              x=INNER_E - TOILET["d"]/2, y=DIV_Y + INT_T/2 + 20 + TOILET["w"]/2,
              w=TOILET["w"], d=TOILET["d"], h=TOILET["h"],
              angle=math.pi/2, color=COL_TOILET, price=TOILET["price"])

    # Vanity against east wall, south of toilet
    add_piece("24\" Vanity (Kent 1697660)",
              x=INNER_E - VANITY["d"]/2, y=DIV_Y + INT_T/2 + 55 + VANITY["w"]/2,
              w=VANITY["w"], d=VANITY["d"], h=VANITY["h"],
              angle=math.pi/2, color=COL_VANITY, price=VANITY["price"])

    # Shower in south end of bath1
    add_piece("Shower 48×32 (Kent 1023986)",
              x=INNER_E - SHOWER["w"]/2, y=INNER_S - SHOWER["d"]/2,
              w=SHOWER["w"], d=SHOWER["d"], h=SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"])

    # ══════════════════════════════════════════════
    #  BATHROOM 2 FIXTURES (back-center zone)
    # ══════════════════════════════════════════════
    b2_left = BED1_X + INT_T/2
    b2_right = BATH2_X - INT_T/2

    # Toilet against north wall
    add_piece("Toilet (Kent 1579329)",
              x=b2_left + 10 + TOILET["w"]/2, y=INNER_N + TOILET["d"]/2,
              w=TOILET["w"], d=TOILET["d"], h=TOILET["h"],
              color=COL_TOILET, price=TOILET["price"])

    # Vanity against north wall
    add_piece("24\" Vanity (Kent 1697660)",
              x=b2_left + 10 + VANITY["w"]/2, y=INNER_N + 30 + VANITY["d"]/2,
              w=VANITY["w"], d=VANITY["d"], h=VANITY["h"],
              color=COL_VANITY, price=VANITY["price"])

    # Shower in south end of bath2
    add_piece("Shower 48×32 (Kent 1023986)",
              x=(b2_left + b2_right) / 2, y=DIV_Y - INT_T/2 - SHOWER["d"]/2,
              w=SHOWER["w"], d=SHOWER["d"], h=SHOWER["h"],
              color=COL_SHOWER, price=SHOWER["price"])

    # ══════════════════════════════════════════════
    #  KITCHEN / LIVING ROOM FIXTURES (front-left)
    # ══════════════════════════════════════════════
    # Room interior: x = 5.5 to 187.75, y = 110.25 to 234.5
    # Kitchen run along the E-W divider wall (north side of front zone)
    # Cabinets, counter, sink, range, fridge in a row

    kitchen_y = DIV_Y + INT_T/2 + COUNTER["d"]/2  # center Y of counter run

    # Kitchen cabinets + countertop (8 LF = 96" along divider wall)
    add_piece("IKEA METOD+NICKEBO Cabinets 8LF",
              x=70 + COUNTER["w"]/2, y=kitchen_y,
              w=COUNTER["w"], d=COUNTER["d"], h=COUNTER["h"],
              color=COL_CABINET, price=COUNTER["price"])

    # Counter on top of cabinets (white laminate — Kent 1015537)
    add_piece("White Laminate Counter 8'",
              x=70 + COUNTER["w"]/2, y=kitchen_y,
              w=COUNTER["w"], d=COUNTER["d"], h=1.5,
              elevation=COUNTER["h"], color=COL_COUNTER)

    # Sink in counter (Kent 1391411)
    add_piece("25\" SS Sink (Kent 1391411)",
              x=100, y=kitchen_y,
              w=SINK["w"], d=SINK["d"], h=SINK["h"],
              elevation=COUNTER["h"] - SINK["h"], color=COL_SINK, price=SINK["price"])

    # Range left of cabinets (Kent 1461599)
    add_piece("24\" Range (Kent 1461599)",
              x=60 + RANGE["w"]/2, y=kitchen_y,
              w=RANGE["w"], d=RANGE["d"], h=RANGE["h"],
              color=COL_RANGE, price=RANGE["price"])

    # Range hood above range (Kent 1462473)
    add_piece("24\" Range Hood (Kent 1462473)",
              x=60 + HOOD["w"]/2, y=kitchen_y,
              w=HOOD["w"], d=HOOD["d"], h=HOOD["h"],
              elevation=54, color=COL_HOOD, price=HOOD["price"])

    # Fridge at start of kitchen run (Kent 1461451)
    add_piece("24\" Fridge (Kent 1461451)",
              x=30 + FRIDGE["w"]/2, y=kitchen_y,
              w=FRIDGE["w"], d=FRIDGE["d"], h=FRIDGE["h"],
              color=COL_FRIDGE, price=FRIDGE["price"])

    # ── Living room area ──
    # Mini-split head on divider wall, high up
    add_piece("Mini-Split Indoor Head",
              x=BATH1_X / 2, y=DIV_Y + INT_T/2 + MINISPLIT_HEAD["d"]/2,
              w=MINISPLIT_HEAD["w"], d=MINISPLIT_HEAD["d"], h=MINISPLIT_HEAD["h"],
              elevation=CEIL_H - MINISPLIT_HEAD["h"] - 6, color=COL_HEAD)

    # ══════════════════════════════════════════════
    #  BEDROOM 1 FIXTURES (back-left)
    # ══════════════════════════════════════════════
    # Baseboard heater on west wall (Kent 1652016)
    add_piece("Baseboard 1500W (Kent 1652016)",
              x=INNER_W + BASEBOARD["d"]/2, y=(INNER_N + DIV_Y - INT_T/2) / 2,
              w=BASEBOARD["w"], d=BASEBOARD["d"], h=BASEBOARD["h"],
              angle=math.pi/2, color=COL_BASEBOARD_C, price=BASEBOARD["price"])

    # ══════════════════════════════════════════════
    #  BEDROOM 2 FIXTURES (back-right)
    # ══════════════════════════════════════════════
    # Baseboard heater on east wall
    add_piece("Baseboard 1500W (Kent 1652016)",
              x=INNER_E - BASEBOARD["d"]/2, y=(INNER_N + DIV_Y - INT_T/2) / 2,
              w=BASEBOARD["w"], d=BASEBOARD["d"], h=BASEBOARD["h"],
              angle=math.pi/2, color=COL_BASEBOARD_C, price=BASEBOARD["price"])

    # ══════════════════════════════════════════════
    #  MECHANICAL / UTILITY (placed in bath1 area or along walls)
    # ══════════════════════════════════════════════

    # Water heater — in bath1 near north wall
    add_piece("Water Heater 182L (Kent 1766016)",
              x=BATH1_X + INT_T/2 + 12, y=DIV_Y + INT_T/2 + 12,
              w=WATER_HEATER["w"], d=WATER_HEATER["d"], h=WATER_HEATER["h"],
              color=COL_WH, price=WATER_HEATER["price"])

    # Sub-panel on west wall in living room (Kent 1013553)
    add_piece("100A Sub-Panel (Kent 1013553)",
              x=INNER_W + PANEL["d"]/2, y=DIV_Y + INT_T/2 + 60,
              w=PANEL["w"], d=PANEL["d"], h=PANEL["h"],
              elevation=48, angle=math.pi/2,
              color=COL_PANEL_C, price=PANEL["price"])

    # HRV — ceiling-mounted in bath1 area (Kent 1400849)
    add_piece("HRV Venmar HRV110 (Kent 1400849)",
              x=BATH1_X + INT_T/2 + 20, y=150,
              w=HRV["w"], d=HRV["d"], h=HRV["h"],
              elevation=CEIL_H - HRV["h"] - 2,
              color=COL_HRV, price=HRV["price"])

    # Washer/Dryer — in bath1 utility corner (Kent 1462204)
    add_piece("GE 24\" Washer/Dryer (Kent 1462204)",
              x=INNER_E - WASHER["d"]/2, y=DIV_Y + INT_T/2 + 12 + WASHER["w"]/2,
              w=WASHER["w"], d=WASHER["d"], h=WASHER["h"],
              angle=math.pi/2, color=COL_WASHER_C, price=WASHER["price"])

    # Condenser — OUTSIDE east wall (Kent 1034429)
    add_piece("Mini-Split Condenser (Kent 1034429)",
              x=W + 18, y=D / 2,
              w=CONDENSER["w"], d=CONDENSER["d"], h=CONDENSER["h"],
              elevation=6, color=COL_COND, price=CONDENSER["price"])

    # ══════════════════════════════════════════════
    #  DIMENSION LINES
    # ══════════════════════════════════════════════
    # Building width
    add_dimension(0, D + 30, W, D + 30, offset=15)
    # Building depth
    add_dimension(-30, 0, -30, D, offset=15)
    # Room widths in back zone
    add_dimension(INNER_W, -15, BED1_X, -15, offset=10)
    add_dimension(BED1_X, -15, BATH2_X, -15, offset=10)
    add_dimension(BATH2_X, -15, INNER_E, -15, offset=10)

    # ══════════════════════════════════════════════
    #  LABELS
    # ══════════════════════════════════════════════
    add_label("21'-6\" × 20'-0\" = 430 sqft", W/2, D + 50, size=16)
    add_label("Mono-slope roof: 9'-6\" (left) → 7'-0\" (right)", W/2, D + 65, size=12)

    # ══════════════════════════════════════════════
    #  CAMERAS
    # ══════════════════════════════════════════════
    # Top-down camera
    top_cam = ET.SubElement(root, "observerCamera")
    top_cam.set("attribute", "topCamera")
    top_cam.set("x", str(cm(W/2)))
    top_cam.set("y", str(cm(D/2)))
    top_cam.set("z", str(cm(200)))  # high above
    top_cam.set("yaw", str(round(math.pi, 5)))
    top_cam.set("pitch", str(round(math.pi/2, 5)))
    top_cam.set("fieldOfView", "1.09")
    top_cam.set("time", "0")
    top_cam.set("lens", "PINHOLE")

    # Observer camera (eye-level perspective from front)
    obs_cam = ET.SubElement(root, "observerCamera")
    obs_cam.set("attribute", "observerCamera")
    obs_cam.set("x", str(cm(W/2)))
    obs_cam.set("y", str(cm(D + 120)))  # standing south of building
    obs_cam.set("z", str(cm(66)))        # eye height 5'-6"
    obs_cam.set("yaw", str(round(math.pi, 5)))  # looking north
    obs_cam.set("pitch", str(round(0.15, 5)))
    obs_cam.set("fieldOfView", "1.09")
    obs_cam.set("time", "0")
    obs_cam.set("lens", "PINHOLE")

    return root


# ═══════════════════════════════════════════════════════
#  .OBJ MODEL GENERATOR (simple box for 3D rendering)
# ═══════════════════════════════════════════════════════

def generate_box_obj():
    """Generate a unit box .obj model for SH3D 3D view rendering.
    Centered horizontally at origin, base at Y=0, Y-up coordinate system."""
    return """# Unit box model for Sweet Home 3D
# SH3D scales this to match width/depth/height of each piece
v -0.5 0.0 -0.5
v  0.5 0.0 -0.5
v  0.5 1.0 -0.5
v -0.5 1.0 -0.5
v -0.5 0.0  0.5
v  0.5 0.0  0.5
v  0.5 1.0  0.5
v -0.5 1.0  0.5
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""


# ═══════════════════════════════════════════════════════
#  MAIN — Generate the .sh3d file
# ═══════════════════════════════════════════════════════

def main():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "stjohns_suite.sh3d")

    print("Generating Sweet Home 3D file...")
    print(f"  Building: {W}\" × {D}\" ({W/12:.1f}' × {D/12:.1f}') = 430 sqft")
    print(f"  Ceiling:  {CEIL_H}\" ({CEIL_H/12:.1f}')")
    print(f"  Walls:    {EXT_T}\" exterior (2×6), {INT_T}\" interior (2×4)")

    # Build XML
    root = build_home_xml()
    tree = ET.ElementTree(root)

    # Serialize XML
    xml_buffer = io.BytesIO()
    tree.write(xml_buffer, encoding="UTF-8", xml_declaration=True)
    xml_bytes = xml_buffer.getvalue()

    # Count elements
    walls = root.findall("wall")
    rooms = root.findall("room")
    furniture = root.findall("pieceOfFurniture")
    doors_wins = root.findall("doorOrWindow")
    dims = root.findall("dimensionLine")

    print(f"\n  Walls:      {len(walls)}")
    print(f"  Rooms:      {len(rooms)}")
    print(f"  Fixtures:   {len(furniture)}")
    print(f"  Doors/Win:  {len(doors_wins)}")
    print(f"  Dimensions: {len(dims)}")

    # Package as .sh3d (ZIP containing Home.xml)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Home.xml", xml_bytes)
        # Include box model for 3D rendering (optional)
        zf.writestr("Content/box.obj", generate_box_obj())

    file_size = os.path.getsize(output_path)
    print(f"\n  Output: {output_path}")
    print(f"  Size:   {file_size:,} bytes")
    print(f"\nOpen in Sweet Home 3D (sweethome3d.com) to view.")
    print("Edit dimensions in this script and re-run to iterate.")

    # Print room summary
    print("\n── Room Layout ──")
    bed1_w = (BED1_X - INT_T/2 - INNER_W) / 12
    bed1_d = (DIV_Y - INT_T/2 - INNER_N) / 12
    print(f"  Bedroom 1:       {bed1_w:.1f}' × {bed1_d:.1f}' = {bed1_w*bed1_d:.0f} sqft")

    b2_w = (BATH2_X - INT_T/2 - BED1_X - INT_T/2) / 12
    b2_d = bed1_d
    print(f"  Bathroom 2:      {b2_w:.1f}' × {b2_d:.1f}' = {b2_w*b2_d:.0f} sqft")

    bed2_w = (INNER_E - BATH2_X - INT_T/2) / 12
    bed2_d = bed1_d
    print(f"  Bedroom 2:       {bed2_w:.1f}' × {bed2_d:.1f}' = {bed2_w*bed2_d:.0f} sqft")

    lk_w = (BATH1_X - INT_T/2 - INNER_W) / 12
    lk_d = (INNER_S - DIV_Y - INT_T/2) / 12
    print(f"  Kitchen/Living:  {lk_w:.1f}' × {lk_d:.1f}' = {lk_w*lk_d:.0f} sqft")

    b1_w = (INNER_E - BATH1_X - INT_T/2) / 12
    b1_d = lk_d
    print(f"  Bathroom 1:      {b1_w:.1f}' × {b1_d:.1f}' = {b1_w*b1_d:.0f} sqft")

    total = bed1_w*bed1_d + b2_w*b2_d + bed2_w*bed2_d + lk_w*lk_d + b1_w*b1_d
    print(f"  Total interior:  {total:.0f} sqft")

    # Print fixture price summary
    print("\n── Fixtures Placed ──")
    total_price = 0
    for f in furniture:
        name = f.get("name", "")
        price = float(f.get("price", "0"))
        if price > 0:
            print(f"  ${price:>8,.2f}  {name}")
            total_price += price
    print(f"  {'─'*30}")
    print(f"  ${total_price:>8,.2f}  Total placed fixtures")


if __name__ == "__main__":
    main()
