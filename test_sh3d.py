#!/usr/bin/env python3
"""
test_sh3d.py — Comprehensive pytest suite for the St. John's .sh3d file.

Run:  python3 -m pytest test_sh3d.py -v
"""

import zipfile
import xml.etree.ElementTree as ET
import xml.sax
import xml.sax.handler
import math
import os
import re

import pytest

# ═══════════════════════════════════════════════════════
#  CONSTANTS (mirrors generate_sh3d.py)
# ═══════════════════════════════════════════════════════
CM = 2.54
W, D = 258, 240
EXT_T, INT_T = 5.5, 4.5
CEIL_H = 96
DIV_Y = 140
P1_X, P2_X = 86, 168

INNER_N = EXT_T
INNER_S = D - EXT_T
INNER_W = EXT_T
INNER_E = W - EXT_T

TOP_S = DIV_Y - INT_T / 2
BOT_N = DIV_Y + INT_T / 2
P1_L = P1_X - INT_T / 2
P1_R = P1_X + INT_T / 2
P2_L = P2_X - INT_T / 2
P2_R = P2_X + INT_T / 2

# Room bounding boxes: (x_min, y_min, x_max, y_max)
ROOMS = {
    "Bedroom A":           (INNER_W, INNER_N, P1_L,    TOP_S),
    "Shared Kitchen":      (P1_R,    INNER_N, P2_L,    TOP_S),
    "Bedroom B":           (P2_R,    INNER_N, INNER_E, TOP_S),
    "Ensuite A":           (INNER_W, BOT_N,   P1_L,    INNER_S),
    "Shared Utility Room": (P1_R,    BOT_N,   P2_L,    INNER_S),
    "Ensuite B":           (P2_R,    BOT_N,   INNER_E, INNER_S),
}

# Items allowed to be elevated
ELEVATED_OK = {
    "Hood", "HRV", "Mini-Split Head", "Sub-Panel", "Condenser",
    "Pendant Lamp", "Lamp", "White Laminate Counter", "Pillow", "Sink",
}

# Items allowed outside the building footprint
EXTERIOR_OK = {"Condenser"}

# Expected room contents (pieceOfFurniture names)
ROOM_CONTENTS = {
    "Bedroom A":           {"Bed", "Pillow", "Nightstand", "Lamp", "Baseboard"},
    "Bedroom B":           {"Bed", "Pillow", "Nightstand", "Lamp", "Baseboard"},
    "Shared Kitchen":      {"IKEA METOD+NICKEBO Lower", "White Laminate Counter",
                            "Sink", "Range", "Hood", "Fridge", "Dining Table",
                            "Chair", "Pendant Lamp", "Mini-Split Head"},
    "Ensuite A":           {"Shower", "Toilet", "Vanity"},
    "Ensuite B":           {"Shower", "Toilet", "Vanity"},
    "Shared Utility Room": {"Washer/Dryer", "Water Heater", "HRV", "Sub-Panel"},
}

# Pairs allowed at the same (x, y) position (stacked vertically)
ALLOWED_STACKS = [
    {"Range", "Hood"},
    {"IKEA METOD+NICKEBO Lower", "White Laminate Counter"},
    {"IKEA METOD+NICKEBO Lower", "Sink"},
    {"White Laminate Counter", "Sink"},
    {"Dining Table", "Pendant Lamp"},
    {"Nightstand", "Lamp"},
]

SH3D = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "stjohns_suite.sh3d")


def _in(cm_val):
    """cm → inches."""
    return cm_val / CM


def _find_room(x, y, tol=1):
    """Return room name if (x, y) is inside a room ± tolerance, else None."""
    for name, (x1, y1, x2, y2) in ROOMS.items():
        if x1 - tol <= x <= x2 + tol and y1 - tol <= y <= y2 + tol:
            return name
    return None


def _on_wall(x, y, tol=3):
    """True if (x, y) is on/near a wall centerline."""
    walls = [
        ("N", lambda: abs(y) < tol),
        ("S", lambda: abs(y - D) < tol),
        ("W", lambda: abs(x) < tol),
        ("E", lambda: abs(x - W) < tol),
        ("DIV", lambda: abs(y - DIV_Y) < tol),
        ("P1", lambda: abs(x - P1_X) < tol),
        ("P2", lambda: abs(x - P2_X) < tol),
    ]
    return any(fn() for _, fn in walls)


def _effective_bbox(x, y, w, d, angle):
    """Axis-aligned bounding box for a rotated piece."""
    a = abs(angle) % math.pi
    if abs(a - math.pi / 2) < 0.15:
        ew, ed = d, w
    else:
        ew, ed = w, d
    return x - ew / 2, y - ed / 2, x + ew / 2, y + ed / 2


# ═══════════════════════════════════════════════════════
#  FIXTURES — load once per session
# ═══════════════════════════════════════════════════════
@pytest.fixture(scope="session")
def sh3d_zip():
    """Opened ZIP file."""
    assert os.path.exists(SH3D), f"{SH3D} not found — run generate_sh3d.py first"
    return zipfile.ZipFile(SH3D, "r")


@pytest.fixture(scope="session")
def zip_names(sh3d_zip):
    return set(sh3d_zip.namelist())


@pytest.fixture(scope="session")
def xml_bytes(sh3d_zip):
    return sh3d_zip.read("Home.xml")


@pytest.fixture(scope="session")
def root(xml_bytes):
    return ET.fromstring(xml_bytes)


@pytest.fixture(scope="session")
def pieces(root):
    """All pieceOfFurniture elements as (name, x, y, w, d, h, elev, angle) tuples."""
    out = []
    for p in root.findall("pieceOfFurniture"):
        out.append({
            "name":  p.get("name"),
            "x":     _in(float(p.get("x", 0))),
            "y":     _in(float(p.get("y", 0))),
            "w":     _in(float(p.get("width", 0))),
            "d":     _in(float(p.get("depth", 0))),
            "h":     _in(float(p.get("height", 0))),
            "elev":  _in(float(p.get("elevation", 0))),
            "angle": float(p.get("angle", 0)),
            "model": p.get("model", ""),
        })
    return out


@pytest.fixture(scope="session")
def openings(root):
    """All doorOrWindow elements."""
    out = []
    for p in root.findall("doorOrWindow"):
        out.append({
            "name":  p.get("name"),
            "x":     _in(float(p.get("x", 0))),
            "y":     _in(float(p.get("y", 0))),
            "w":     _in(float(p.get("width", 0))),
            "d":     _in(float(p.get("depth", 0))),
            "h":     _in(float(p.get("height", 0))),
            "elev":  _in(float(p.get("elevation", 0))),
            "angle": float(p.get("angle", 0)),
            "model": p.get("model", ""),
            "wallThickness": p.get("wallThickness"),
            "wallDistance":  p.get("wallDistance"),
            "cutOutShape":   p.get("cutOutShape"),
            "boundToWall":   p.get("boundToWall"),
        })
    return out


# ═══════════════════════════════════════════════════════
#  STRUCTURE TESTS
# ═══════════════════════════════════════════════════════
class TestZipStructure:
    def test_is_valid_zip(self, sh3d_zip):
        assert sh3d_zip.testzip() is None

    def test_has_home_xml(self, zip_names):
        assert "Home.xml" in zip_names

    def test_zip_header(self):
        with open(SH3D, "rb") as f:
            assert f.read(2) == b"PK"


class TestXmlParsing:
    def test_sax_parse(self, xml_bytes):
        class Handler(xml.sax.handler.ContentHandler):
            pass
        xml.sax.parseString(xml_bytes, Handler())

    def test_etree_parse(self, root):
        assert root.tag == "home"


class TestColorFormat:
    def test_all_colors_8char_hex(self, xml_bytes):
        xml_str = xml_bytes.decode("utf-8")
        colors = re.findall(r'(?:Color|color)="([^"]+)"', xml_str)
        assert len(colors) > 0, "No color attributes found"
        bad = [c for c in colors if not re.match(r'^[0-9A-F]{8}$', c)]
        assert bad == [], f"Invalid color values: {bad}"


class TestCamera:
    def test_observer_camera_present(self, root):
        assert root.findall("observerCamera"), "No <observerCamera> element"

    def test_top_camera_present(self, root):
        cameras = root.findall("camera")
        assert any(c.get("attribute") == "topCamera" for c in cameras)


# ═══════════════════════════════════════════════════════
#  LAYOUT TESTS
# ═══════════════════════════════════════════════════════
class TestRooms:
    def test_room_count(self, root):
        assert len(root.findall("room")) == 6

    def test_room_names(self, root):
        names = {r.get("name") for r in root.findall("room")}
        expected = {"Bedroom A", "Shared Kitchen", "Bedroom B",
                    "Ensuite A", "Shared Utility Room", "Ensuite B"}
        assert names == expected

    def test_rooms_have_floor_color(self, root):
        for r in root.findall("room"):
            assert r.get("floorColor"), f"{r.get('name')} has no floor color"


class TestWalls:
    def test_wall_count(self, root):
        """4 exterior + 3 interior = 7 walls."""
        assert len(root.findall("wall")) == 7

    def test_exterior_walls_connected(self, root):
        """Each exterior wall should reference adjacent walls."""
        for w in root.findall("wall")[:4]:
            assert w.get("wallAtStart") or w.get("wallAtEnd"), \
                f"Wall {w.get('id')} has no connections"


# ═══════════════════════════════════════════════════════
#  MODEL TESTS
# ═══════════════════════════════════════════════════════
class TestModels:
    def test_catalog_items_have_catalog_id(self, root):
        """Items using catalog resource paths must have a catalogId."""
        bad = []
        for tag in ("pieceOfFurniture", "doorOrWindow"):
            for p in root.findall(tag):
                model = p.get("model", "")
                cat_id = p.get("catalogId", "")
                if model.startswith("/com/eteks/") and not cat_id:
                    bad.append(f"{p.get('name')}: catalog path but no catalogId")
        assert bad == [], f"Missing catalogId: {bad}"

    def test_fallback_models_in_zip(self, root, zip_names):
        """Items using Content/ paths must have their model in the ZIP."""
        missing = []
        for tag in ("pieceOfFurniture", "doorOrWindow"):
            for p in root.findall(tag):
                model = p.get("model", "")
                if model.startswith("Content/") and model not in zip_names:
                    missing.append(f"{p.get('name')}: {model}")
        assert missing == [], f"Missing fallback models: {missing}"

    def test_fallback_box_in_zip(self, zip_names):
        """The fallback box.obj must be present for non-catalog items."""
        assert "Content/box.obj" in zip_names


# ═══════════════════════════════════════════════════════
#  PLACEMENT TESTS — furniture
# ═══════════════════════════════════════════════════════
class TestFurnitureBounds:
    def test_all_inside_building(self, pieces):
        """Every piece (except exterior items) must be within the building envelope."""
        margin = EXT_T + 2
        oob = []
        for p in pieces:
            if p["name"] in EXTERIOR_OK:
                continue
            x1, y1, x2, y2 = _effective_bbox(
                p["x"], p["y"], p["w"], p["d"], p["angle"])
            if x1 < -margin or x2 > W + margin or y1 < -margin or y2 > D + margin:
                oob.append(f"{p['name']} bbox=({x1:.0f},{y1:.0f})-({x2:.0f},{y2:.0f})")
        assert oob == [], f"Out-of-bounds: {oob}"

    def test_no_unexpected_floating(self, pieces):
        """Items not in ELEVATED_OK must be at floor level (elevation=0)."""
        floating = []
        for p in pieces:
            if p["name"] in ELEVATED_OK:
                continue
            if p["elev"] > 0.5:
                floating.append(f"{p['name']} elev={p['elev']:.1f}in")
        assert floating == [], f"Floating items: {floating}"

    def test_nothing_through_ceiling(self, pieces):
        """Top of item (height + elevation) must not exceed ceiling + 4 inches."""
        bad = []
        for p in pieces:
            if p["name"] in EXTERIOR_OK:
                continue
            top = p["h"] + p["elev"]
            if top > CEIL_H + 4:
                bad.append(f"{p['name']} top={top:.0f}in > ceiling={CEIL_H}in")
        assert bad == [], f"Through ceiling: {bad}"


class TestFurnitureSizing:
    def test_no_degenerate_sizes(self, pieces):
        """Nothing should have a dimension < 1 inch."""
        bad = []
        for p in pieces:
            if p["w"] < 1 or p["d"] < 1 or p["h"] < 1:
                bad.append(f"{p['name']} ({p['w']:.1f}x{p['d']:.1f}x{p['h']:.1f})")
        assert bad == [], f"Degenerate sizes: {bad}"

    def test_beds_proper_size(self, pieces):
        """Beds should be 48-60" wide and 72-80" long."""
        for p in pieces:
            if p["name"] == "Bed":
                assert 48 <= p["w"] <= 60, f"Bed width {p['w']}"
                assert 72 <= p["d"] <= 80, f"Bed depth {p['d']}"

    def test_fridge_proper_height(self, pieces):
        """Fridge should be 55-72" tall."""
        for p in pieces:
            if p["name"] == "Fridge":
                assert 55 <= p["h"] <= 72, f"Fridge height {p['h']}"


class TestRoomAssignment:
    def test_furniture_in_correct_rooms(self, pieces):
        """Each piece should be inside its expected room."""
        misplaced = []
        for p in pieces:
            if p["name"] in EXTERIOR_OK:
                continue
            room = _find_room(p["x"], p["y"])
            if room is None:
                misplaced.append(f"{p['name']} at ({p['x']:.0f},{p['y']:.0f}): no room")
            elif p["name"] not in ROOM_CONTENTS.get(room, set()):
                misplaced.append(f"{p['name']} in {room} (unexpected)")
        assert misplaced == [], f"Misplaced: {misplaced}"

    def test_each_room_has_expected_fixtures(self, pieces):
        """Verify no expected fixtures are missing from a room."""
        # Build actual room→names mapping
        actual = {}
        for p in pieces:
            room = _find_room(p["x"], p["y"])
            if room:
                actual.setdefault(room, set()).add(p["name"])

        missing = []
        for room, expected in ROOM_CONTENTS.items():
            got = actual.get(room, set())
            diff = expected - got
            if diff:
                missing.append(f"{room} missing: {diff}")
        assert missing == [], f"Missing fixtures: {missing}"


class TestNoDuplicateStacking:
    def test_no_unexpected_stacking(self, pieces):
        """Items at the same (x, y) should be in ALLOWED_STACKS."""
        by_pos = {}
        for p in pieces:
            key = (round(p["x"] * 2) / 2, round(p["y"] * 2) / 2)
            by_pos.setdefault(key, []).append(p["name"])

        bad = []
        for pos, names in by_pos.items():
            if len(names) <= 1:
                continue
            name_set = set(names)
            # Check each pair is in an allowed stack
            covered = False
            for pair in ALLOWED_STACKS:
                if pair.issubset(name_set):
                    covered = True
                    break
            if not covered:
                bad.append(f"at ({pos[0]},{pos[1]}): {names}")
        assert bad == [], f"Unexpected stacking: {bad}"


# ═══════════════════════════════════════════════════════
#  PLACEMENT TESTS — doors & windows
# ═══════════════════════════════════════════════════════
class TestDoorWindowPlacement:
    def test_all_on_walls(self, openings):
        """Every door/window center must be on a wall centerline."""
        bad = []
        for o in openings:
            if not _on_wall(o["x"], o["y"]):
                bad.append(f"{o['name']} at ({o['x']:.0f},{o['y']:.0f})")
        assert bad == [], f"Not on walls: {bad}"

    def test_door_sizes(self, openings):
        """Doors must be ≥ 28" wide, ≥ 72" tall."""
        for o in openings:
            if "Door" in o["name"]:
                assert o["w"] >= 28, f"{o['name']} width={o['w']:.0f}in"
                assert o["h"] >= 72, f"{o['name']} height={o['h']:.0f}in"

    def test_window_sill_height(self, openings):
        """Windows should have sill elevation between 24-48 inches."""
        for o in openings:
            if "Casement" in o["name"]:
                assert 24 <= o["elev"] <= 48, \
                    f"{o['name']} sill={o['elev']:.0f}in"

    def test_bound_to_wall(self, openings):
        """All doors/windows should have boundToWall='true'."""
        bad = [o["name"] for o in openings if o["boundToWall"] != "true"]
        assert bad == [], f"Not bound to wall: {bad}"

    def test_cut_out_shape_present(self, openings):
        """All doors/windows need a cutOutShape for wall cuts."""
        bad = [o["name"] for o in openings if not o["cutOutShape"]]
        assert bad == [], f"No cutOutShape: {bad}"

    def test_depth_matches_wall(self, openings):
        """Door/window depth should match (or be close to) wall thickness."""
        bad = []
        for o in openings:
            expected_t = EXT_T if _on_exterior_wall(o["x"], o["y"]) else INT_T
            if abs(o["d"] - expected_t) > 1.5:
                bad.append(
                    f"{o['name']} depth={o['d']:.1f}in, wall={expected_t}in")
        assert bad == [], f"Depth mismatch: {bad}"


def _on_exterior_wall(x, y, tol=3):
    return (abs(y) < tol or abs(y - D) < tol or
            abs(x) < tol or abs(x - W) < tol)


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
