#!/usr/bin/env python3
"""Analyze furniture placement in the generated .sh3d file."""
import zipfile, xml.etree.ElementTree as ET, math

CM = 2.54
W, D = 258, 240
EXT_T, INT_T = 5.5, 4.5
CEIL_H = 96
DIV_Y = 140
P1_X, P2_X = 86, 168

# Interior edges (inches)
INNER_N, INNER_S = EXT_T, D - EXT_T
INNER_W, INNER_E = EXT_T, W - EXT_T
TOP_S = DIV_Y - INT_T / 2
BOT_N = DIV_Y + INT_T / 2
P1_L = P1_X - INT_T / 2
P1_R = P1_X + INT_T / 2
P2_L = P2_X - INT_T / 2
P2_R = P2_X + INT_T / 2

# Room bounding boxes (inches): (x_min, y_min, x_max, y_max)
ROOMS = {
    "Bedroom A":      (INNER_W, INNER_N, P1_L, TOP_S),
    "Shared Kitchen":  (P1_R, INNER_N, P2_L, TOP_S),
    "Bedroom B":      (P2_R, INNER_N, INNER_E, TOP_S),
    "Ensuite A":      (INNER_W, BOT_N, P1_L, INNER_S),
    "Utility":        (P1_R, BOT_N, P2_L, INNER_S),
    "Ensuite B":      (P2_R, BOT_N, INNER_E, INNER_S),
}

# Items that are legitimately elevated
ELEVATED_OK = {
    "Hood", "HRV", "Mini-Split Head", "Sub-Panel", "Condenser",
    "Pendant Lamp", "Lamp", "White Laminate Counter", "Pillow",
    "Sink",  # sink recessed into counter
}

xml_data = zipfile.ZipFile("stjohns_suite.sh3d").read("Home.xml")
root = ET.fromstring(xml_data)

def to_in(cm_val):
    return cm_val / CM

print("=" * 80)
print("FURNITURE PLACEMENT ANALYSIS")
print("=" * 80)

issues = []

for tag in ("pieceOfFurniture", "doorOrWindow"):
    for p in root.findall(tag):
        name = p.get("name")
        x_cm = float(p.get("x", 0))
        y_cm = float(p.get("y", 0))
        w_cm = float(p.get("width", 0))
        d_cm = float(p.get("depth", 0))
        h_cm = float(p.get("height", 0))
        elev_cm = float(p.get("elevation", 0))
        angle = float(p.get("angle", 0))

        # Convert to inches
        x, y = to_in(x_cm), to_in(y_cm)
        w, d, h = to_in(w_cm), to_in(d_cm), to_in(h_cm)
        elev = to_in(elev_cm)

        # Account for rotation: if angle ~90 or ~270, swap w/d
        a_norm = abs(angle) % math.pi
        if abs(a_norm - math.pi/2) < 0.1:
            ew, ed = d, w  # effective width/depth swapped
        else:
            ew, ed = w, d

        # Bounding box of piece (inches)
        x_min = x - ew / 2
        x_max = x + ew / 2
        y_min = y - ed / 2
        y_max = y + ed / 2

        flags = []

        # 1. Out of building bounds (allow exterior items like condenser)
        if name != "Condenser":
            if x_min < -2:
                flags.append(f"LEFT-OOB({x_min:.1f})")
            if x_max > W + 2:
                flags.append(f"RIGHT-OOB({x_max:.1f})")
            if y_min < -2:
                flags.append(f"NORTH-OOB({y_min:.1f})")
            if y_max > D + 2:
                flags.append(f"SOUTH-OOB({y_max:.1f})")

        # 2. Floating check
        if elev > 0 and name not in ELEVATED_OK:
            flags.append(f"FLOATING(elev={elev:.1f}in)")

        # 3. Size sanity
        if tag == "doorOrWindow":
            if h < 30:
                flags.append(f"TINY-DOOR(h={h:.0f}in)")
            if w < 10 and d < 10:
                flags.append(f"TINY-OPENING(w={w:.0f},d={d:.0f})")
        else:
            if h + elev > CEIL_H + 2:
                flags.append(f"ABOVE-CEILING(top={h+elev:.0f}in)")

        # 4. Find which room it's in
        in_room = None
        for rname, (rx1, ry1, rx2, ry2) in ROOMS.items():
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                in_room = rname
                break

        # Print
        room_str = f"[{in_room}]" if in_room else "[NO ROOM / WALL / OUTSIDE]"
        flag_str = " *** " + ", ".join(flags) if flags else ""
        print(f"  {tag[:5]:5s} {name:30s} pos=({x:6.1f},{y:6.1f}) "
              f"sz=({w:5.1f}x{d:5.1f}x{h:5.1f}) elev={elev:5.1f} "
              f"{room_str}{flag_str}")

        if flags:
            issues.append((name, flags))

print()
if issues:
    print(f"ISSUES FOUND: {len(issues)}")
    for name, flags in issues:
        print(f"  {name}: {', '.join(flags)}")
else:
    print("NO ISSUES FOUND")
