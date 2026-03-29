#!/usr/bin/env python3
"""
Mathematical Model: Backyard Suite Floor Plan Configurations
=============================================================
Max exterior footprint: 430 sq ft
Required rooms: 1 kitchen, 1 entrance, 2 bathrooms, 2 bedrooms

Approach:
  1. Estimate furniture/object sizes per room
  2. Derive minimum L×W for each room from furniture + clearance
  3. Enumerate rectangular room arrangements that tile into
     a bounding rectangle ≤ 430 sq ft
  4. Rank by compactness, hallway waste, and aspect ratio
"""

from itertools import product
from dataclasses import dataclass, field
from typing import List, Tuple
import math

# ──────────────────────────────────────────────────────────────
# STEP 1 — Furniture / object size estimates (feet)
# ──────────────────────────────────────────────────────────────

FURNITURE = {
    "bedroom": {
        "double_bed":       (4.5, 6.5),   # W × D  (54″ × 75″)
        "nightstand":       (1.5, 1.5),
        "small_dresser":    (3.0, 1.5),
        "desk":             (3.5, 2.0),
        "desk_chair":       (2.0, 2.0),
        "closet_rod_area":  (3.0, 2.0),   # minimal reach-in closet
    },
    "bathroom": {
        "toilet":           (1.5, 2.5),   # including clearance
        "sink_vanity":      (2.0, 1.5),
        "shower_stall":     (3.0, 3.0),   # 36″×36″ stall
        "door_swing":       (2.5, 2.5),
    },
    "kitchen": {
        "counter_run":      (8.0, 2.0),   # L-shaped or galley
        "fridge":           (3.0, 2.5),
        "stove":            (2.5, 2.0),
        "sink":             (2.0, 2.0),
        "small_table_2seat":(3.0, 2.5),
    },
    "entrance": {
        "door_landing":     (3.0, 3.0),
        "coat_hooks":       (3.0, 0.5),
        "shoe_area":        (2.0, 1.0),
        "bench":            (3.0, 1.5),
    },
}

def print_furniture_summary():
    """Print a formatted table of all furniture estimates."""
    print("=" * 65)
    print("STEP 1 — Furniture & Object Size Estimates (W × D in feet)")
    print("=" * 65)
    for room, items in FURNITURE.items():
        print(f"\n  {room.upper()}")
        for name, (w, d) in items.items():
            area = w * d
            print(f"    {name:25s}  {w:4.1f} × {d:4.1f}  = {area:5.1f} sq ft")


# ──────────────────────────────────────────────────────────────
# STEP 2 — Derive minimum room dimensions from furniture
# ──────────────────────────────────────────────────────────────
# We add circulation clearance (≥ 3 ft walkway) around the
# dominant furniture cluster, then round to half-foot increments.

@dataclass
class RoomSpec:
    name: str
    min_w: float        # minimum width  (ft)
    min_d: float        # minimum depth  (ft)
    notes: str = ""

    @property
    def area(self):
        return self.min_w * self.min_d


def derive_room_specs() -> List[RoomSpec]:
    """
    Bottom-up room sizing:
      – lay dominant furniture along one wall
      – add 3 ft clearance / circulation
      – round up to nearest 0.5 ft
    """
    specs = []

    # ── Bedroom ──
    # Bed (4.5 × 6.5) along one wall + 3 ft walkway on side
    # Depth: bed depth 6.5 + dresser 1.5 + 2 ft aisle = 10 → keep compact
    # Width: bed 4.5 + nightstand 1.5 + closet 2.0 + 0.5 gap = 8.5 → round 9
    # But that's huge for 430 sq ft total; use compact layout:
    #   Width = bed 4.5 + 1.5 nightstand + 1.5 circulation = 7.5  → 8
    #   Depth = bed 6.5 + 2.5 (dresser/desk zone) + walk  = 9.5 → 10
    # Even tighter feasible minimum:
    #   W=8, D=9 = 72 sq ft  — snug but livable
    #   W=9, D=10 = 90 sq ft — comfortable
    specs.append(RoomSpec("bedroom1", 8.0, 9.0,
        "double bed + nightstand + dresser/desk, tight"))
    specs.append(RoomSpec("bedroom2", 8.0, 9.0,
        "same program as bedroom1"))

    # ── Bathroom ──
    # 3×3 shower + toilet (1.5×2.5) + vanity (2×1.5)
    # Linear layout: W = 3 + 1.5 + 2 = 6.5 → 7;  D = 3 shower depth + door = 5
    # Compact: W=5, D=7 = 35 sq ft  (standard 3-piece bath)
    specs.append(RoomSpec("bathroom1", 5.0, 7.0,
        "3-piece: shower, toilet, vanity"))
    specs.append(RoomSpec("bathroom2", 5.0, 7.0,
        "same as bathroom1"))

    # ── Kitchen ──
    # Galley or L-shape: counter run 8 ft × 2 ft deep on one side
    # Opposite: fridge + table
    # W = 8;  D = counter 2 + aisle 3.5 + table 2.5 = 8;  = 64 sq ft
    # Compact: W=8, D=7 = 56 sq ft — workable galley
    specs.append(RoomSpec("kitchen", 7.0, 8.0,
        "galley: counter run, fridge, 2-seat table"))

    # ── Entrance / Mudroom ──
    # Door landing 3×3, coat hooks, bench
    # W=4, D=4 = 16 sq ft (compact foyer)
    specs.append(RoomSpec("entrance", 4.0, 4.0,
        "landing pad, coat hooks, shoe area"))

    return specs


def print_room_specs(specs: List[RoomSpec]):
    print("\n" + "=" * 65)
    print("STEP 2 — Minimum Room Dimensions (feet)")
    print("=" * 65)
    total = 0
    for s in specs:
        print(f"  {s.name:12s}  {s.min_w:4.1f} × {s.min_d:4.1f}  = {s.area:5.1f} sq ft   ({s.notes})")
        total += s.area
    print(f"\n  {'TOTAL':12s}  {'':>11s}  = {total:5.1f} sq ft (room area, no walls/hallway)")


# ──────────────────────────────────────────────────────────────
# STEP 3 — Generate geometric configurations
# ──────────────────────────────────────────────────────────────
# Strategy: treat each room as an axis-aligned rectangle that
# can be placed in either orientation (swap W↔D).  We try to
# pack 6 rooms into a bounding rectangle whose area ≤ 430 sq ft.
#
# Because exact 2-D bin packing is NP-hard, we use a practical
# heuristic: we consider "strip" layouts common in small homes —
# rooms arranged in 2 or 3 horizontal strips (rows) where each
# strip's rooms share the same depth (the max depth among rooms
# in that strip).

@dataclass
class PlacedRoom:
    name: str
    x: float
    y: float
    w: float
    d: float

@dataclass
class Configuration:
    label: str
    bounding_w: float
    bounding_d: float
    rooms: List[PlacedRoom] = field(default_factory=list)
    wall_thickness: float = 0.0

    @property
    def total_area(self):
        return self.bounding_w * self.bounding_d

    @property
    def usable_area(self):
        return sum(r.w * r.d for r in self.rooms)

    @property
    def efficiency(self):
        return self.usable_area / self.total_area * 100 if self.total_area else 0

    @property
    def aspect_ratio(self):
        if self.bounding_d == 0:
            return float('inf')
        return max(self.bounding_w, self.bounding_d) / min(self.bounding_w, self.bounding_d)


def make_oriented_sizes(spec: RoomSpec) -> List[Tuple[float, float]]:
    """Return both orientations (w,d) and (d,w)."""
    if spec.min_w == spec.min_d:
        return [(spec.min_w, spec.min_d)]
    return [(spec.min_w, spec.min_d), (spec.min_d, spec.min_w)]


# Wall thickness adds to each room boundary
WALL = 0.33  # ~4″ interior wall half-thickness per side


def strip_pack(strip_assignments: List[List[Tuple[str, float, float]]],
               label: str) -> Configuration:
    """
    Given a list of strips, where each strip is a list of (name, w, d),
    compute a configuration.  Each strip is placed vertically one atop
    the next. Rooms within a strip are placed side-by-side.

    Wall thickness is added between rooms and on the perimeter.
    """
    rooms = []
    y_cursor = WALL  # start after outer wall
    max_total_w = 0

    for strip in strip_assignments:
        strip_depth = max(d for _, _, d in strip) + 2 * WALL
        x_cursor = WALL
        for name, w, d in strip:
            rooms.append(PlacedRoom(name, x_cursor, y_cursor, w, d))
            x_cursor += w + WALL
        max_total_w = max(max_total_w, x_cursor)
        y_cursor += strip_depth

    bounding_w = max_total_w
    bounding_d = y_cursor + WALL  # outer wall at end

    return Configuration(label, round(bounding_w, 1), round(bounding_d, 1),
                         rooms, WALL)


def generate_configurations(specs: List[RoomSpec],
                            max_area: float = 430.0) -> List[Configuration]:
    """
    Try many strip partitions of the 6 rooms and keep those
    that fit within max_area.  We consider 2-strip and 3-strip
    layouts with both room orientations.
    """

    room_data = {}  # name -> list of (w,d) orientations
    for s in specs:
        room_data[s.name] = make_oriented_sizes(s)

    names = [s.name for s in specs]
    configs = []

    # ── Predefined strip groupings (room indices) ──
    # 6 rooms: bedroom1, bedroom2, bathroom1, bathroom2, kitchen, entrance
    #   idx:      0          1          2          3         4        5
    # We try logical groupings:

    strip_plans = {
        # ── 2-strip layouts ──
        "2-strip: beds+ent | baths+kitchen": [
            [0, 1, 5],   # bedrooms + entrance
            [2, 3, 4],   # bathrooms + kitchen
        ],
        "2-strip: beds+bath | kitchen+bath+ent": [
            [0, 1, 2],
            [3, 4, 5],
        ],
        "2-strip: beds | baths+kitchen+ent": [
            [0, 1],
            [2, 3, 4, 5],
        ],
        # ── 3-strip layouts ──
        "3-strip: beds | baths | kitchen+ent": [
            [0, 1],
            [2, 3],
            [4, 5],
        ],
        "3-strip: bed+bath | bed+bath | kitchen+ent": [
            [0, 2],
            [1, 3],
            [4, 5],
        ],
        "3-strip: kitchen | beds+ent | baths": [
            [4],
            [0, 1, 5],
            [2, 3],
        ],
        "3-strip: kitchen+ent | beds | baths": [
            [4, 5],
            [0, 1],
            [2, 3],
        ],
        "3-strip: bed+bath+ent | bed+bath | kitchen": [
            [0, 2, 5],
            [1, 3],
            [4],
        ],
    }

    for plan_label, strips_indices in strip_plans.items():
        # For each room, try both orientations
        orient_options = [room_data[names[i]] for i in range(len(names))]

        # Build cartesian product of orientations
        orient_combos = list(product(*orient_options))

        for orient in orient_combos:
            strips = []
            for idx_list in strips_indices:
                strip = [(names[i], orient[i][0], orient[i][1]) for i in idx_list]
                strips.append(strip)

            cfg = strip_pack(strips, plan_label)
            if cfg.total_area <= max_area:
                configs.append(cfg)

    # Deduplicate by (bounding_w, bounding_d, label)
    seen = set()
    unique = []
    for c in configs:
        key = (c.label, c.bounding_w, c.bounding_d)
        if key not in seen:
            seen.add(key)
            unique.append(c)

    # Sort by efficiency descending, then area ascending
    unique.sort(key=lambda c: (-c.efficiency, c.total_area))
    return unique


# ──────────────────────────────────────────────────────────────
# STEP 4 — Output & visualisation
# ──────────────────────────────────────────────────────────────

def ascii_floorplan(cfg: Configuration, scale: float = 2.0) -> str:
    """Render a simple ASCII floor plan."""
    cols = int(cfg.bounding_w * scale) + 1
    rows = int(cfg.bounding_d * scale) + 1
    grid = [[' '] * cols for _ in range(rows)]

    # Draw outer boundary
    for c in range(cols):
        grid[0][c] = '─'
        grid[rows - 1][c] = '─'
    for r in range(rows):
        grid[r][0] = '│'
        grid[r][cols - 1] = '│'
    grid[0][0] = '┌'
    grid[0][cols - 1] = '┐'
    grid[rows - 1][0] = '└'
    grid[rows - 1][cols - 1] = '┘'

    for room in cfg.rooms:
        x0 = int(room.x * scale)
        y0 = int(room.y * scale)
        x1 = int((room.x + room.w) * scale)
        y1 = int((room.y + room.d) * scale)
        # Clamp
        x0 = max(1, min(x0, cols - 2))
        x1 = max(1, min(x1, cols - 2))
        y0 = max(1, min(y0, rows - 2))
        y1 = max(1, min(y1, rows - 2))

        # Draw room borders
        for c in range(x0, x1 + 1):
            if 0 <= y0 < rows:
                grid[y0][c] = '·'
            if 0 <= y1 < rows:
                grid[y1][c] = '·'
        for r in range(y0, y1 + 1):
            if 0 <= r < rows:
                grid[r][x0] = '·'
                grid[r][x1] = '·'

        # Label
        label = room.name[:6]
        mid_r = (y0 + y1) // 2
        mid_c = (x0 + x1) // 2 - len(label) // 2
        for i, ch in enumerate(label):
            cc = mid_c + i
            if 0 < cc < cols - 1 and 0 < mid_r < rows - 1:
                grid[mid_r][cc] = ch

        # Area label
        area_str = f"{room.w * room.d:.0f}sf"
        ar = mid_r + 1
        ac = (x0 + x1) // 2 - len(area_str) // 2
        for i, ch in enumerate(area_str):
            cc = ac + i
            if 0 < cc < cols - 1 and 0 < ar < rows - 1:
                grid[ar][cc] = ch

    return '\n'.join(''.join(row) for row in grid)


def print_configurations(configs: List[Configuration], top_n: int = 8):
    print("\n" + "=" * 65)
    print(f"STEP 3 & 4 — Top {min(top_n, len(configs))} Configurations (of {len(configs)} found, ≤ 430 sq ft)")
    print("=" * 65)

    for i, cfg in enumerate(configs[:top_n]):
        print(f"\n{'─' * 65}")
        print(f"  CONFIG {i+1}: {cfg.label}")
        print(f"  Bounding box: {cfg.bounding_w:.1f} × {cfg.bounding_d:.1f} ft "
              f"= {cfg.total_area:.0f} sq ft")
        print(f"  Usable room area: {cfg.usable_area:.0f} sq ft  |  "
              f"Efficiency: {cfg.efficiency:.1f}%  |  "
              f"Aspect ratio: {cfg.aspect_ratio:.2f}")
        print()
        for r in cfg.rooms:
            print(f"    {r.name:12s}  @({r.x:5.1f},{r.y:5.1f})  "
                  f"{r.w:4.1f}×{r.d:4.1f} = {r.w*r.d:5.1f} sq ft")
        print()
        print(ascii_floorplan(cfg))


# ──────────────────────────────────────────────────────────────
# STEP 5 — Sensitivity: show how room size changes affect total
# ──────────────────────────────────────────────────────────────

def sensitivity_table(specs: List[RoomSpec]):
    print("\n" + "=" * 65)
    print("SENSITIVITY — Room size vs. total footprint")
    print("=" * 65)
    print(f"  {'Room':12s}  {'Min (sq ft)':>12s}  {'Compact':>10s}  {'Comfort':>10s}")
    print(f"  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*10}")

    compact_total = 0
    comfort_total = 0
    for s in specs:
        base = s.area
        # Compact: shrink each dim by 0.5 ft
        cw = max(s.min_w - 0.5, 4.0)
        cd = max(s.min_d - 0.5, 4.0)
        compact = cw * cd
        # Comfortable: grow each dim by 1 ft
        comfort = (s.min_w + 1) * (s.min_d + 1)
        compact_total += compact
        comfort_total += comfort
        print(f"  {s.name:12s}  {base:12.1f}  {compact:10.1f}  {comfort:10.1f}")

    base_total = sum(s.area for s in specs)
    print(f"\n  {'TOTAL':12s}  {base_total:12.1f}  {compact_total:10.1f}  {comfort_total:10.1f}")
    print(f"  + ~15% walls/circ ≈  {base_total*1.15:5.0f}        {compact_total*1.15:5.0f}        {comfort_total*1.15:5.0f}")


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    print_furniture_summary()

    specs = derive_room_specs()
    print_room_specs(specs)

    configs = generate_configurations(specs)
    print_configurations(configs, top_n=8)

    sensitivity_table(specs)

    # ── Summary ──
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    if configs:
        best = configs[0]
        print(f"  Best configuration: {best.label}")
        print(f"  Bounding box: {best.bounding_w} × {best.bounding_d} ft = {best.total_area:.0f} sq ft")
        print(f"  Efficiency: {best.efficiency:.1f}% of bounding area is usable room space")
        print(f"  Fits within 430 sq ft: {'YES' if best.total_area <= 430 else 'NO'}")
    else:
        print("  No configurations found that fit within 430 sq ft.")
        print("  Consider reducing room sizes or using the compact estimates.")
    print()


if __name__ == "__main__":
    main()
