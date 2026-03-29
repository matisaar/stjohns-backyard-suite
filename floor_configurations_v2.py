#!/usr/bin/env python3
"""
Floor Plan Model v2 — Adjacency-Aware with Hallway & Doors
============================================================
Constraints:
  - Max exterior footprint: 430 sq ft
  - 2 bedroom "suites" (each bedroom has a private en-suite bathroom)
  - 1 kitchen (shared/common area)
  - 1 entrance foyer
  - Hallway/corridor connecting entrance → kitchen → both suites
  - Doors placed on shared walls between adjacent rooms
  - Every room reachable from the entrance (BFS validated)

Room sizes (compact — derived from furniture estimates):
  Bedroom:  8 × 9  = 72 sf   (double bed, nightstand, dresser, desk)
  Bathroom: 5 × 5  = 25 sf   (compact 3-piece: 30″ shower, toilet, vanity)
  Kitchen:  7 × 7  = 49 sf   (galley counter, fridge, stove, small table)
  Entry:    4 × 4  = 16 sf   (landing, coat hooks, bench)
  Hallway:  3 ft wide         (comfortable single-person corridor)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
WALL = 0.33          # ~4″ interior wall (half-thickness per side)
DOOR_W = 2.67        # 32″ door opening

COLORS = {
    "Bedroom 1":  "#7FB3D8",
    "Bedroom 2":  "#6CA0C8",
    "Bath 1":     "#A8D8A8",
    "Bath 2":     "#8FC98F",
    "Kitchen":    "#F4C478",
    "Entry":      "#D4A0D4",
    "Hallway":    "#E8DDD0",
    "Hallway N":  "#E8DDD0",
    "Hallway S":  "#E8DDD0",
}

# ──────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────

@dataclass
class Room:
    name: str
    x: float
    y: float
    w: float
    h: float

    @property
    def area(self): return self.w * self.h
    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2
    @property
    def x2(self): return self.x + self.w
    @property
    def y2(self): return self.y + self.h


@dataclass
class Door:
    room_a: str
    room_b: str
    x: float
    y: float
    is_vertical: bool   # True = door in a vertical wall (opens E-W)


@dataclass
class FloorPlan:
    name: str
    desc: str
    rooms: List[Room]
    doors: List[Door]
    bw: float   # bounding width
    bh: float   # bounding height

    @property
    def total_area(self): return self.bw * self.bh
    @property
    def room_area(self): return sum(r.area for r in self.rooms)
    @property
    def efficiency(self): return self.room_area / self.total_area * 100
    @property
    def aspect(self): return max(self.bw, self.bh) / min(self.bw, self.bh)


def make_door(r1: Room, r2: Room, tol=0.5) -> Optional[Door]:
    """Place a door at the midpoint of the shared wall between two rooms."""
    # Vertical wall: r1 right = r2 left
    if abs(r1.x2 - r2.x) < tol:
        lo = max(r1.y, r2.y)
        hi = min(r1.y2, r2.y2)
        if hi - lo >= DOOR_W:
            return Door(r1.name, r2.name, r1.x2, (lo + hi) / 2, True)
    # Vertical wall: r2 right = r1 left
    if abs(r2.x2 - r1.x) < tol:
        lo = max(r1.y, r2.y)
        hi = min(r1.y2, r2.y2)
        if hi - lo >= DOOR_W:
            return Door(r1.name, r2.name, r1.x, (lo + hi) / 2, True)
    # Horizontal wall: r1 top = r2 bottom
    if abs(r1.y2 - r2.y) < tol:
        lo = max(r1.x, r2.x)
        hi = min(r1.x2, r2.x2)
        if hi - lo >= DOOR_W:
            return Door(r1.name, r2.name, (lo + hi) / 2, r1.y2, False)
    # Horizontal wall: r2 top = r1 bottom
    if abs(r2.y2 - r1.y) < tol:
        lo = max(r1.x, r2.x)
        hi = min(r1.x2, r2.x2)
        if hi - lo >= DOOR_W:
            return Door(r1.name, r2.name, (lo + hi) / 2, r1.y, False)
    return None


def auto_doors(pairs: List[Tuple[Room, Room]]) -> List[Door]:
    """Generate doors for (room, room) adjacency pairs."""
    doors = []
    seen = set()
    for a, b in pairs:
        key = tuple(sorted([a.name, b.name]))
        if key in seen:
            continue
        d = make_door(a, b)
        if d:
            doors.append(d)
            seen.add(key)
    return doors


def bfs_reachable(plan: FloorPlan) -> Tuple[bool, List[str]]:
    """BFS from Entry; return (all_reachable, unreachable_names)."""
    adj: Dict[str, set] = {r.name: set() for r in plan.rooms}
    for d in plan.doors:
        adj.setdefault(d.room_a, set()).add(d.room_b)
        adj.setdefault(d.room_b, set()).add(d.room_a)
    visited = set()
    queue = ["Entry"]
    visited.add("Entry")
    while queue:
        cur = queue.pop(0)
        for nb in adj.get(cur, []):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    all_names = {r.name for r in plan.rooms}
    unreachable = sorted(all_names - visited)
    return len(unreachable) == 0, unreachable


# ──────────────────────────────────────────────────────────────
# Layout builders
# ──────────────────────────────────────────────────────────────

def layout_A(bW=8, bH=9, baW=5, baH=5, kW=7, kH=7, eW=4, eH=4, hW=3):
    """
    LINEAR SPINE — suites top/bottom, kitchen+entry in middle

    ┌─────────┬─────┐
    │Bedroom 1│Bath1│
    ├─────────┴─────┤
    │   Hallway N   │
    ├───────┬───────┤
    │Kitchen│ Entry │
    ├───────┴───────┤
    │   Hallway S   │
    ├─────────┬─────┤
    │Bedroom 2│Bath2│
    └─────────┴─────┘
    """
    g = WALL
    suite_w = bW + g + baW

    y = g
    bed2 = Room("Bedroom 2", g, y, bW, bH)
    bath2 = Room("Bath 2", g + bW + g, y, baW, baH)
    y += bH + g

    hall_s = Room("Hallway S", g, y, suite_w, hW)
    y += hW + g

    ent_w = suite_w - kW - g
    if ent_w < 3:
        ent_w = 3
        kW = suite_w - ent_w - g
    kitchen = Room("Kitchen", g, y, kW, kH)
    entry = Room("Entry", g + kW + g, y, ent_w, eH)
    mid_h = max(kH, eH)
    y += mid_h + g

    hall_n = Room("Hallway N", g, y, suite_w, hW)
    y += hW + g

    bed1 = Room("Bedroom 1", g, y, bW, bH)
    bath1 = Room("Bath 1", g + bW + g, y, baW, baH)
    y += bH + g

    bw = suite_w + 2 * g
    bh = y
    rooms = [bed1, bath1, bed2, bath2, kitchen, entry, hall_n, hall_s]

    pairs = [
        (bed1, bath1), (bed2, bath2),
        (bed1, hall_n),
        (bed2, hall_s),
        (kitchen, hall_s), (kitchen, hall_n),
        (entry, hall_s), (entry, hall_n),
        (kitchen, entry),
    ]
    doors = auto_doors(pairs)
    return FloorPlan("A · Linear Spine",
        "Suites top & bottom · kitchen+entry in middle · central hallway",
        rooms, doors, bw, bh)


def layout_B(bW=8, bH=9, baW=5, baH=5, kW=7, kH=7, eW=4, eH=4, hW=3):
    """
    STACKED SUITES + SIDE KITCHEN

    ┌─────────┬─────┬───────┐
    │Bedroom 1│Bath1│       │
    │         │     │Kitchen│
    ├─────────┼─────┤       │
    │Bedroom 2│Bath2├───────┤
    │         │     │ Entry │
    └─────────┴─────┴───────┘
    """
    g = WALL
    suite_w = baW + g + bW  # bath outside, bedroom inside
    total_h = bH + g + bH  # two bedrooms stacked

    right_x = g + suite_w + g
    kit_h = total_h - eH - g

    y = g
    bath2 = Room("Bath 2", g, y, baW, baH)
    bed2 = Room("Bedroom 2", g + baW + g, y, bW, bH)
    entry = Room("Entry", right_x, y, kW, eH)

    y2 = g + bH + g
    bath1 = Room("Bath 1", g, y2, baW, baH)
    bed1 = Room("Bedroom 1", g + baW + g, y2, bW, bH)
    kitchen = Room("Kitchen", right_x, y + eH + g, kW, kit_h)

    y_top = g + total_h + g
    bw = right_x + kW + g
    bh = y_top

    rooms = [bed1, bath1, bed2, bath2, kitchen, entry]
    pairs = [
        (bed1, bath1), (bed2, bath2),
        (bed1, kitchen), (bed2, entry),
        (entry, kitchen),
    ]
    doors = auto_doors(pairs)
    return FloorPlan("B · Stacked Suites",
        "Suites stacked · baths outside · bedrooms adjoin kitchen+entry",
        rooms, doors, bw, bh)


def layout_C(bW=8, bH=9, baW=5, baH=5, kW=7, kH=7, eW=4, eH=4, hW=3):
    """
    L-SHAPE — suite above suite; kitchen+entry extend right

    ┌─────────┬─────┐
    │Bedroom 1│Bath1│
    ├─────────┴─────┤
    │    Hallway    │
    ├─────────┬─────┬───────┬─────┐
    │Bedroom 2│Bath2│Kitchen│Entry│
    └─────────┴─────┴───────┴─────┘
    """
    g = WALL
    suite_w = bW + g + baW

    y = g
    bed2 = Room("Bedroom 2", g, y, bW, bH)
    bath2 = Room("Bath 2", g + bW + g, y, baW, baH)
    kit_x = g + suite_w + g
    kitchen = Room("Kitchen", kit_x, y, kW, kH)
    ent_x = kit_x + kW + g
    entry = Room("Entry", ent_x, y, eW, eH)
    row1_h = max(bH, kH, eH)
    y += row1_h + g

    full_w = ent_x + eW - g
    hallway = Room("Hallway", g, y, full_w, hW)
    y += hW + g

    bed1 = Room("Bedroom 1", g, y, bW, bH)
    bath1 = Room("Bath 1", g + bW + g, y, baW, baH)
    y += bH + g

    bw = ent_x + eW + g
    bh = y
    rooms = [bed1, bath1, bed2, bath2, kitchen, entry, hallway]
    pairs = [
        (bed1, bath1), (bed2, bath2),
        (bed1, hallway),
        (bed2, hallway),
        (kitchen, hallway), (entry, hallway),
        (kitchen, entry),
    ]
    doors = auto_doors(pairs)
    return FloorPlan("C · L-Shape",
        "Suite 1 on top · suite 2 + kitchen + entry on bottom · L-shaped footprint",
        rooms, doors, bw, bh)


def layout_D(bW=8, bH=9, baW=5, baH=5, kW=7, kH=7, eW=4, eH=4, hW=3):
    """
    COMPACT CORE — bedrooms on top, baths flank kitchen+entry below

    ┌──────────┬──────────┐
    │Bedroom 1 │Bedroom 2 │
    │          │          │
    ├────┬─────┴─────┬────┤
    │Ba1 │ Kit │Entry│Ba2 │
    └────┴─────┴─────┴────┘
    """
    g = WALL
    bottom_w = baW + g + kW + g + eW + g + baW
    top_w = bottom_w  # match
    bed_actual_w = (top_w - g) / 2

    y = g
    bottom_h = max(baH, kH, eH)
    # Extend baths to full bottom row height so they touch bedrooms above
    bath1 = Room("Bath 1", g, y, baW, bottom_h)
    kitchen = Room("Kitchen", g + baW + g, y, kW, bottom_h)
    entry = Room("Entry", g + baW + g + kW + g, y, eW, bottom_h)
    bath2 = Room("Bath 2", g + baW + g + kW + g + eW + g, y, baW, bottom_h)
    y += bottom_h + g

    bed1 = Room("Bedroom 1", g, y, bed_actual_w, bH)
    bed2 = Room("Bedroom 2", g + bed_actual_w + g, y, bed_actual_w, bH)
    y += bH + g

    bw = top_w + 2 * g
    bh = y
    rooms = [bed1, bath1, bed2, bath2, kitchen, entry]
    pairs = [
        (bed1, bath1), (bed2, bath2),   # en-suite: bed above its bath
        (bed1, kitchen), (bed2, entry), # beds above center rooms
        (kitchen, entry),               # center rooms adjacent
    ]
    doors = auto_doors(pairs)
    return FloorPlan("D · Compact Core",
        "Bedrooms on top · baths flank kitchen+entry core below · no hallway needed",
        rooms, doors, bw, bh)


def layout_E(bW=8, bH=9, baW=5, baH=5, kW=7, kH=7, eW=4, eH=4, hW=3):
    """
    MIRRORED SUITES — bedrooms face central corridor; baths on outside

    ┌─────┬────────┬────┬────────┬─────┐
    │Bath1│Bedroom1│    │Bedroom2│Bath2│
    │     │        │Hall│        │     │
    │     │        │way │        │     │
    ├─────┴────────┤    ├────────┴─────┤
    │              ├────┤              │
    │              │Entr│              │
    │              │    │              │
    │              │Kit │              │
    └──────────────┴────┴──────────────┘
    """
    g = WALL
    suite_w = baW + g + bW  # bath outside, bed inside

    hall_x = g + suite_w + g
    right_suite_x = hall_x + hW + g

    y = g
    entry = Room("Entry", hall_x, y, hW, eH)
    kitchen = Room("Kitchen", hall_x, y + eH + g, hW, kH)
    common_h = eH + g + kH

    suite_h = max(bH, common_h)

    bath1 = Room("Bath 1", g, g, baW, baH)
    bed1 = Room("Bedroom 1", g + baW + g, g, bW, suite_h)
    bed2 = Room("Bedroom 2", right_suite_x, g, bW, suite_h)
    bath2 = Room("Bath 2", right_suite_x + bW + g, g, baW, baH)

    y_top = g + suite_h + g
    bw = right_suite_x + bW + g + baW + g
    bh = y_top

    rooms = [bed1, bath1, bed2, bath2, kitchen, entry]
    pairs = [
        (bed1, bath1), (bed2, bath2),
        (bed1, entry), (bed1, kitchen),
        (bed2, entry), (bed2, kitchen),
        (entry, kitchen),
    ]
    doors = auto_doors(pairs)
    return FloorPlan("E · Mirrored Suites",
        "Suites face central corridor · baths on outside · entry+kitchen at corridor end",
        rooms, doors, bw, bh)


# ──────────────────────────────────────────────────────────────
# Generate plans with size variations
# ──────────────────────────────────────────────────────────────

SIZE_PRESETS = [
    #  label        bW  bH  baW baH  kW  kH  eW  eH  hW
    ("minimal",      7,  8,  4,  5,   6,  6,  3,  3,  3),
    ("compact",      8,  9,  5,  5,   7,  7,  4,  4,  3),
    ("standard",     9,  9,  5,  6,   7,  7,  4,  4,  3),
    ("comfortable",  9, 10,  5,  6,   8,  7,  4,  4,  3),
]

LAYOUTS = [layout_A, layout_B, layout_C, layout_D, layout_E]


def generate_plans(max_area=430.0) -> List[FloorPlan]:
    plans = []
    for label, bW, bH, baW, baH, kW, kH, eW, eH, hW in SIZE_PRESETS:
        for fn in LAYOUTS:
            try:
                p = fn(bW=bW, bH=bH, baW=baW, baH=baH,
                       kW=kW, kH=kH, eW=eW, eH=eH, hW=hW)
                p.name = f"{p.name} [{label}]"
                if p.total_area <= max_area:
                    plans.append(p)
            except Exception:
                pass
    plans.sort(key=lambda p: (-p.efficiency, p.total_area))
    return plans


# ──────────────────────────────────────────────────────────────
# Drawing
# ──────────────────────────────────────────────────────────────

FURN_SPECS = {
    # Each item: (name, real_w, real_h, color, wall_affinity)
    # wall_affinity: None=free, "any"=against any wall, "back"=back wall (top)
    "Bedroom": [
        ("Bed",     5.0, 6.5, "#4A7A9B", "back"),       # queen: 60″×80″
        ("N.stand", 1.5, 1.5, "#8B6F4E", None),          # beside bed
        ("Dresser", 3.0, 1.5, "#8B6F4E", "any"),         # against wall
        ("Desk",    3.0, 2.0, "#8B6F4E", "any"),
    ],
    "Bath": [
        ("Shower",  2.5, 2.5, "#B0D4F1", "any"),
        ("Toilet",  1.5, 2.2, "#E8E8E8", "any"),
        ("Sink",    1.8, 1.5, "#B0D4F1", "any"),
    ],
    "Entry": [
        ("Ext.Door", 3.0, 0.4, "#6B4226", "any"),   # exterior door on outside wall
        ("Bench",    2.5, 1.2, "#8B6F4E", "any"),
    ],
}


def _get_door_zones(room, plan_doors, clearance=3.0):
    """Return door clearance zones as [(local_x, local_y, radius), ...]."""
    zones = []
    for d in plan_doors:
        if d.room_a == room.name or d.room_b == room.name:
            zones.append((d.x - room.x, d.y - room.y, clearance))
    return zones


def _overlaps_zone(fx, fy, fw, fh, zones):
    """Check if rectangle overlaps any circular clearance zone."""
    for zx, zy, zr in zones:
        cx = max(fx, min(zx, fx + fw))
        cy = max(fy, min(zy, fy + fh))
        if (cx - zx) ** 2 + (cy - zy) ** 2 < zr ** 2:
            return True
    return False


def _overlaps_item(fx, fy, fw, fh, placed):
    """Check if rectangle overlaps any already-placed item."""
    for _, px, py, pw, ph, _ in placed:
        if fx < px + pw and fx + fw > px and fy < py + ph and fy + fh > py:
            return True
    return False


def _wall_candidates(W, H, iw, ih, pad=0.3):
    """Yield (x, y) positions against each wall for an item of size (iw, ih)."""
    # Bottom wall, sweep left to right
    for x in [pad, W / 2 - iw / 2, W - iw - pad]:
        yield (x, pad)
    # Top wall
    for x in [pad, W / 2 - iw / 2, W - iw - pad]:
        yield (x, H - ih - pad)
    # Left wall
    for y in [pad, H / 2 - ih / 2, H - ih - pad]:
        yield (pad, y)
    # Right wall
    for y in [pad, H / 2 - ih / 2, H - ih - pad]:
        yield (W - iw - pad, y)


def _free_candidates(W, H, iw, ih, pad=0.3, step=0.5):
    """Yield (x, y) grid positions within room."""
    y = pad
    while y + ih <= H - pad:
        x = pad
        while x + iw <= W - pad:
            yield (x, y)
            x += step
        y += step


def place_room_furniture(room_type, W, H, door_zones):
    """
    Constraint-based furniture placement for any room type.
    Returns [(name, x, y, w, h, color), ...] in room-local coords.
    
    Algorithm:
      1. For each furniture item in priority order:
         a. Generate candidate positions (wall-hugging or free)
         b. Filter out positions that overlap door clearance zones
         c. Filter out positions that overlap already-placed items
         d. Pick the first valid position
      2. Nightstand is special-cased: placed beside the bed
    """
    specs = FURN_SPECS.get(room_type, [])
    placed = []
    bed_rect = None  # track bed for nightstand placement

    for name, iw, ih, color, affinity in specs:
        if name == "N.stand" and bed_rect is not None:
            # Place beside the bed
            bx, by, bw, bh = bed_rect
            candidates = [
                (bx + bw + 0.2, by, iw, ih),          # right of bed
                (bx - iw - 0.2, by, iw, ih),          # left of bed
                (bx + bw + 0.2, by + bh - ih, iw, ih), # right, foot-end
            ]
            ok = False
            for cx, cy, cw, ch in candidates:
                if (cx >= 0.2 and cx + cw <= W - 0.2 and
                    cy >= 0.2 and cy + ch <= H - 0.2 and
                    not _overlaps_zone(cx, cy, cw, ch, door_zones) and
                    not _overlaps_item(cx, cy, cw, ch, placed)):
                    placed.append((name, cx, cy, cw, ch, color))
                    ok = True
                    break
            if not ok:
                pass  # skip if no room
            continue

        # Try both orientations
        orientations = [(iw, ih)]
        if iw != ih:
            orientations.append((ih, iw))

        best = None
        for ow, oh in orientations:
            if affinity == "back":
                # Top wall preferred (far from door typically at bottom)
                cands = list(_wall_candidates(W, H, ow, oh))
                # Sort: prefer top wall (largest y first)
                cands.sort(key=lambda p: -p[1])
            elif affinity == "any":
                cands = list(_wall_candidates(W, H, ow, oh))
            else:
                cands = list(_free_candidates(W, H, ow, oh))

            for cx, cy in cands:
                if (cx + ow <= W and cy + oh <= H and
                    not _overlaps_zone(cx, cy, ow, oh, door_zones) and
                    not _overlaps_item(cx, cy, ow, oh, placed)):
                    best = (name, cx, cy, ow, oh, color)
                    break
            if best:
                break

        if best:
            placed.append(best)
            if name == "Bed":
                bed_rect = (best[1], best[2], best[3], best[4])

    return placed


# ──────────────────────────────────────────────────────────────
# Constraint-based kitchen furniture placement
# ──────────────────────────────────────────────────────────────

# Standard appliance dimensions (feet)
COUNTER_D  = 2.0   # depth (24″ standard)
STOVE_W    = 2.5   # width (30″)
SINK_W     = 2.0   # width (24″)
FRIDGE_W   = 2.5   # width (30″)
FRIDGE_D   = 2.5   # depth (30″ including handle)
MIN_AISLE  = 3.0   # minimum passage between counter and table
GAP        = 0.25  # clearance between appliances


def place_kitchen_furniture(W: float, H: float, doors_rel=None):
    """
    Return furniture items [(name, x, y, w, h, color), ...] positioned
    using real constraints.  All coordinates relative to room origin.

    doors_rel: list of (dx, dy, is_vertical) — door positions relative
               to the room origin, so we can keep clearance zones open.

    Layout strategy — counter along one wall, appliances embedded,
    fridge at end, table in remaining open space avoiding door zones.

    Constraints enforced:
      • Counter + appliances along one wall (away from doors)
      • Stove & sink embedded in counter (same depth)
      • Fridge at counter end, taller
      • Work triangle: stove↔sink ≤ 6′, sink↔fridge ≤ 6′
      • 3′ clearance zone in front of every door
      • Table in remaining open space, not blocking any door
    """
    if doors_rel is None:
        doors_rel = []

    PAD = 0.25
    CLEARANCE = 3.0  # door swing clearance

    # --- Identify door zones as (cx, cy, radius) in room-local coords ---
    # Each door needs a CLEARANCE-radius keep-out circle
    door_zones = []
    for dx, dy, is_vert in doors_rel:
        door_zones.append((dx, dy, CLEARANCE))

    def overlaps_door(fx, fy, fw, fh):
        """Check if a rectangle overlaps any door clearance zone."""
        for zx, zy, zr in door_zones:
            # Closest point on rect to zone center
            cx = max(fx, min(zx, fx + fw))
            cy = max(fy, min(zy, fy + fh))
            if (cx - zx) ** 2 + (cy - zy) ** 2 < zr ** 2:
                return True
        return False

    # --- Determine which wall to place counter on ---
    # Pick the wall with the fewest / no doors.
    # Walls: bottom (y=0), top (y=H), left (x=0), right (x=W)
    wall_scores = {"bottom": 0, "top": 0, "left": 0, "right": 0}
    for dx, dy, is_vert in doors_rel:
        if dy < 0.5:          wall_scores["bottom"] += 1
        if dy > H - 0.5:      wall_scores["top"] += 1
        if dx < 0.5:          wall_scores["left"] += 1
        if dx > W - 0.5:      wall_scores["right"] += 1

    # Prefer bottom, then left, sorting by score (fewest doors)
    wall_pref = sorted(["bottom", "top", "left", "right"],
                       key=lambda w: (wall_scores[w], w != "bottom", w != "left"))
    counter_wall = wall_pref[0]

    # --- Place counter run along chosen wall ---
    # We'll work in a canonical frame then rotate at the end
    # Canonical: counter along bottom, room is cW wide × cH tall
    if counter_wall in ("bottom", "top"):
        cW, cH = W, H
    else:
        cW, cH = H, W

    # Counter
    fridge_w = FRIDGE_W
    counter_h = COUNTER_D
    fridge_h = min(COUNTER_D + 1.0, cH * 0.35)

    # --- Decide which end gets the fridge (check door zones) ---
    # Transform canonical positions to room coords for door-zone check
    def canonical_to_room_pos(cx, cy, cw, ch):
        if counter_wall == "bottom":
            return cx, cy, cw, ch
        elif counter_wall == "top":
            return W - cx - cw, H - cy - ch, cw, ch
        elif counter_wall == "left":
            return cy, W - cx - cw, ch, cw
        else:
            return H - cy - ch, cx, ch, cw

    # Try fridge on right end first, then left end
    fridge_right_x = cW - fridge_w - PAD
    fridge_left_x = PAD
    rr = canonical_to_room_pos(fridge_right_x, PAD, fridge_w, fridge_h)
    rl = canonical_to_room_pos(fridge_left_x, PAD, fridge_w, fridge_h)
    fridge_on_right = not overlaps_door(rr[0], rr[1], rr[2], rr[3])
    fridge_on_left = not overlaps_door(rl[0], rl[1], rl[2], rl[3])

    if fridge_on_right:
        fridge_x = fridge_right_x
    elif fridge_on_left:
        fridge_x = fridge_left_x
    else:
        fridge_x = fridge_right_x  # fallback

    # Counter fills the opposite end from fridge
    if fridge_x > cW / 2:  # fridge on right
        counter_x = PAD
        counter_w = cW - fridge_w - GAP - 2 * PAD
    else:  # fridge on left
        counter_x = fridge_x + fridge_w + GAP
        counter_w = cW - counter_x - PAD

    if counter_w < STOVE_W + SINK_W + 2 * GAP:
        fridge_w = max(1.5, fridge_w - (STOVE_W + SINK_W + 2 * GAP - counter_w))
        if fridge_x > cW / 2:
            fridge_x = cW - fridge_w - PAD
            counter_w = cW - fridge_w - GAP - 2 * PAD
        else:
            counter_x = fridge_x + fridge_w + GAP
            counter_w = cW - counter_x - PAD

    # Stove
    stove_x = counter_x
    stove_y = PAD
    stove_w = STOVE_W
    stove_h = counter_h

    # Sink
    sink_x = stove_x + stove_w + GAP
    sink_y = PAD + 0.25
    sink_w = SINK_W
    sink_h = counter_h - 0.5

    # Right counter segment (between sink and fridge, if fridge on right)
    if fridge_x > cW / 2:
        right_ctr_x = sink_x + sink_w + GAP
        right_ctr_w = fridge_x - GAP - right_ctr_x
    else:
        right_ctr_x = sink_x + sink_w + GAP
        right_ctr_w = counter_x + counter_w - right_ctr_x
    has_right_counter = right_ctr_w > 0.5

    # Fridge y
    fridge_y = PAD

    # --- Table: find a spot that doesn't block any door ---
    table_w = min(3.5, cW * 0.5)
    table_h = min(2.5, cH * 0.3)

    # Try several candidate positions, pick first that's clear
    candidates = [
        ((cW - table_w) / 2, cH - table_h - PAD),            # top center
        (PAD, cH - table_h - PAD),                            # top left
        (cW - table_w - PAD, cH - table_h - PAD),             # top right
        ((cW - table_w) / 2, counter_h + COUNTER_D + MIN_AISLE),  # middle
    ]

    # Transform candidates back to room coords for door-zone check
    def canonical_to_room(cx, cy):
        if counter_wall == "bottom":
            return cx, cy
        elif counter_wall == "top":
            return cW - cx, cH - cy
        elif counter_wall == "left":
            return cy, cW - cx
        else:  # right
            return cH - cy, cx

    table_x, table_y = None, None
    for tx, ty in candidates:
        # Check in room coords
        rx, ry = canonical_to_room(tx, ty)
        rw, rh = table_w, table_h
        if counter_wall in ("left", "right"):
            rw, rh = table_h, table_w
        if not overlaps_door(rx, ry, rw, rh) and ty + table_h <= cH - PAD and ty > counter_h + MIN_AISLE - 0.5:
            table_x, table_y = tx, ty
            break

    has_table = table_x is not None

    # --- Build items in canonical coords then transform ---
    raw = []
    counter_y = PAD
    raw.append(("Counter", counter_x, counter_y, counter_w, counter_h, "#C4A882"))
    if has_right_counter:
        raw.append(("", right_ctr_x, counter_y, right_ctr_w, counter_h, "#C4A882"))
    raw.append(("Stove", stove_x, stove_y, stove_w, stove_h, "#888888"))
    raw.append(("Sink", sink_x, sink_y, sink_w, sink_h, "#B0D4F1"))
    raw.append(("Fridge", fridge_x, fridge_y, fridge_w, fridge_h, "#D0D0D0"))
    if has_table:
        raw.append(("Table", table_x, table_y, table_w, table_h, "#8B6F4E"))

    # Transform from canonical to room-local
    items = []
    for name, ix, iy, iw, ih, ic in raw:
        if counter_wall == "bottom":
            items.append((name, ix, iy, iw, ih, ic))
        elif counter_wall == "top":
            items.append((name, W - ix - iw, H - iy - ih, iw, ih, ic))
        elif counter_wall == "left":
            items.append((name, iy, W - ix - iw, ih, iw, ic))
        else:  # right
            items.append((name, H - iy - ih, ix, ih, iw, ic))

    return items


def draw_plan(ax, plan: FloorPlan, show_furniture=True, title_prefix=""):
    """Render a floor plan on a matplotlib Axes."""
    # Outer shell
    shell = mpatches.Rectangle(
        (0, 0), plan.bw, plan.bh,
        linewidth=3, facecolor='#F5F0E8', edgecolor='#222')
    ax.add_patch(shell)

    for room in plan.rooms:
        color = COLORS.get(room.name, "#DDD")
        rect = mpatches.FancyBboxPatch(
            (room.x, room.y), room.w, room.h,
            boxstyle="round,pad=0.06",
            facecolor=color, edgecolor='#333', linewidth=1.4, alpha=0.88)
        ax.add_patch(rect)

        # Room label
        fs = 8 if min(room.w, room.h) > 3 else 6
        ax.text(room.cx, room.cy + 0.4, room.name,
                ha='center', va='center', fontsize=fs, fontweight='bold', color='#222')
        ax.text(room.cx, room.cy - 0.35,
                f"{room.w:.0f}′×{room.h:.0f}′={room.area:.0f}sf",
                ha='center', va='center', fontsize=max(fs - 2, 4.5), color='#444')

        # Furniture
        if show_furniture:
            # Collect door clearance zones for this room
            door_zones = _get_door_zones(room, plan.doors)

            if room.name == "Kitchen":
                doors_rel = [(d.x - room.x, d.y - room.y, d.is_vertical)
                             for d in plan.doors
                             if d.room_a == "Kitchen" or d.room_b == "Kitchen"]
                items = place_kitchen_furniture(room.w, room.h, doors_rel)
            elif "Bedroom" in room.name:
                items = place_room_furniture("Bedroom", room.w, room.h, door_zones)
            elif "Bath" in room.name:
                items = place_room_furniture("Bath", room.w, room.h, door_zones)
            elif room.name == "Entry":
                items = place_room_furniture("Entry", room.w, room.h, door_zones)
            else:
                items = []

            for fname, fx, fy, fw, fh, fc in items:
                frect = mpatches.Rectangle(
                    (room.x + fx, room.y + fy), fw, fh,
                    facecolor=fc, edgecolor='#555', linewidth=0.5, alpha=0.45)
                ax.add_patch(frect)
                ax.text(room.x + fx + fw / 2, room.y + fy + fh / 2,
                        fname, ha='center', va='center', fontsize=4,
                        color='#222', alpha=0.7)

    # Doors (red lines with swing arcs)
    for door in plan.doors:
        if door.is_vertical:
            ax.plot([door.x, door.x],
                    [door.y - DOOR_W / 2, door.y + DOOR_W / 2],
                    color='#CC4444', linewidth=3.5, solid_capstyle='round')
            arc = Arc((door.x, door.y - DOOR_W / 2), DOOR_W, DOOR_W,
                      angle=0, theta1=0, theta2=90,
                      color='#CC4444', linewidth=0.8, linestyle='--')
            ax.add_patch(arc)
        else:
            ax.plot([door.x - DOOR_W / 2, door.x + DOOR_W / 2],
                    [door.y, door.y],
                    color='#CC4444', linewidth=3.5, solid_capstyle='round')
            arc = Arc((door.x - DOOR_W / 2, door.y), DOOR_W, DOOR_W,
                      angle=0, theta1=0, theta2=90,
                      color='#CC4444', linewidth=0.8, linestyle='--')
            ax.add_patch(arc)

    # Dimension annotations
    ax.annotate('', xy=(plan.bw, -1.0), xytext=(0, -1.0),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1))
    ax.text(plan.bw / 2, -1.5, f"{plan.bw:.1f}′", ha='center', fontsize=7, color='#333')

    ax.annotate('', xy=(-1.0, plan.bh), xytext=(-1.0, 0),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1))
    ax.text(-1.6, plan.bh / 2, f"{plan.bh:.1f}′", ha='center', fontsize=7,
            color='#333', rotation=90)

    connected, unreachable = bfs_reachable(plan)
    conn_str = "✓ all reachable" if connected else f"✗ {', '.join(unreachable)}"

    ax.set_title(
        f"{title_prefix}{plan.name}\n"
        f"{plan.bw:.1f}′×{plan.bh:.1f}′ = {plan.total_area:.0f} sf  "
        f"({plan.efficiency:.0f}%)  {conn_str}",
        fontsize=8, fontweight='bold', pad=8)

    ax.set_xlim(-2.5, plan.bw + 1.5)
    ax.set_ylim(-2.5, plan.bh + 1.5)
    ax.set_aspect('equal')
    ax.axis('off')


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    all_plans = generate_plans(max_area=430.0)

    # Also generate defaults as fallback
    defaults = []
    for fn in LAYOUTS:
        p = fn()
        defaults.append(p)

    plans = all_plans if all_plans else [p for p in defaults if p.total_area <= 500]
    plans.sort(key=lambda p: (-p.efficiency, p.total_area))

    print("=" * 65)
    print("BACKYARD SUITE — Floor Plan Configurations v2")
    print("En-suite baths · Hallway-connected · Doors placed")
    print(f"Max area: 430 sq ft  |  Found: {len(all_plans)} valid configs")
    print("=" * 65)

    show = plans[:10]
    for i, p in enumerate(show, 1):
        conn, unr = bfs_reachable(p)
        print(f"\n{'━' * 60}")
        print(f"  {i}. {p.name}")
        print(f"     {p.desc}")
        print(f"     {p.bw:.1f}′ × {p.bh:.1f}′ = {p.total_area:.0f} sf  "
              f"| eff {p.efficiency:.0f}%  | aspect {p.aspect:.2f}")
        print(f"     Connectivity: {'✓ ALL OK' if conn else '✗ UNREACHABLE: ' + str(unr)}")
        for r in p.rooms:
            print(f"       {r.name:14s}  {r.w:.0f}×{r.h:.0f} = {r.area:.0f} sf  @({r.x:.1f},{r.y:.1f})")
        for d in p.doors:
            sym = "│" if d.is_vertical else "─"
            print(f"       door: {d.room_a:14s} ↔ {d.room_b:14s}  @({d.x:.1f},{d.y:.1f}) {sym}")

    # ── Overview figure ──
    n = min(len(show), 6)
    ncols = min(n, 3)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(8 * ncols, 10 * nrows))
    if n == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes.reshape(1, -1)
    elif ncols == 1:
        axes = axes.reshape(-1, 1)

    fig.suptitle(
        "Backyard Suite — Floor Plans v2 (≤ 430 sf)\n"
        "En-suite bathrooms · Hallway connections · Door placements\n"
        "Red lines = door openings with swing arcs",
        fontsize=13, fontweight='bold', y=0.99)

    for idx in range(n):
        r, c = divmod(idx, ncols)
        draw_plan(axes[r][c], show[idx], show_furniture=False,
                  title_prefix=f"#{idx+1}  ")

    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig("floorplan_v2_overview.png", dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\nSaved: floorplan_v2_overview.png")

    # ── Best plan detailed ──
    best = show[0]
    fig2, ax2 = plt.subplots(1, 1, figsize=(14, 12))
    draw_plan(ax2, best, show_furniture=True, title_prefix="BEST: ")
    legend_patches = [mpatches.Patch(facecolor=COLORS.get(n, "#DDD"), edgecolor='#333', label=n)
                      for n in ["Bedroom 1", "Bedroom 2", "Bath 1", "Bath 2",
                                "Kitchen", "Entry", "Hallway"]]
    legend_patches.append(plt.Line2D([0], [0], color='#CC4444', linewidth=3, label='Door'))
    ax2.legend(handles=legend_patches, loc='upper right', fontsize=8,
               framealpha=0.9, title="Legend")
    fig2.suptitle("Best Configuration — Detailed with Furniture & Doors",
                  fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig2.savefig("floorplan_v2_detail.png", dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: floorplan_v2_detail.png")

    # ── Connectivity diagram ──
    n_conn = min(3, len(show))
    fig3, axes3 = plt.subplots(1, n_conn, figsize=(7 * n_conn, 8))
    if n_conn == 1:
        axes3 = [axes3]
    fig3.suptitle("Room Connectivity — doors shown as red edges",
                  fontsize=13, fontweight='bold')

    for idx in range(n_conn):
        ax = axes3[idx]
        p = show[idx]
        positions = {r.name: (r.cx, r.cy) for r in p.rooms}

        # Draw door edges first (behind nodes)
        for d in p.doors:
            pa = positions.get(d.room_a)
            pb = positions.get(d.room_b)
            if pa and pb:
                ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                        color='#CC4444', linewidth=2, alpha=0.6, zorder=1)

        # Draw room nodes
        for r in p.rooms:
            color = COLORS.get(r.name, "#DDD")
            rad = 1.0 + r.area / 100
            circle = mpatches.Circle((r.cx, r.cy), rad,
                                      facecolor=color, edgecolor='#333',
                                      linewidth=1.5, alpha=0.85, zorder=2)
            ax.add_patch(circle)
            short = (r.name.replace("Bedroom", "Bed")
                     .replace("Hallway", "Hall")
                     .replace("Kitchen", "Kit"))
            ax.text(r.cx, r.cy, short,
                    ha='center', va='center', fontsize=6, fontweight='bold', zorder=3)

        conn, _ = bfs_reachable(p)
        ax.set_xlim(-3, p.bw + 3)
        ax.set_ylim(-3, p.bh + 3)
        ax.set_aspect('equal')
        ax.set_title(f"#{idx+1} {p.name}\n{'✓ connected' if conn else '✗ disconnected'}",
                     fontsize=8, fontweight='bold')
        ax.axis('off')

    plt.tight_layout()
    fig3.savefig("floorplan_v2_connectivity.png", dpi=150, bbox_inches='tight',
                 facecolor='white')
    print(f"Saved: floorplan_v2_connectivity.png")


if __name__ == "__main__":
    main()
