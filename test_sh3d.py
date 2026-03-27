#!/usr/bin/env python3
"""Test the generated .sh3d file for correctness."""
import zipfile
import xml.sax
import xml.sax.handler

class TestHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.elements = {}
    def startElement(self, name, attrs):
        self.elements[name] = self.elements.get(name, 0) + 1

# 1. Check ZIP structure
print("=== ZIP Contents ===")
with zipfile.ZipFile("stjohns_suite.sh3d", "r") as zf:
    for info in zf.infolist():
        print(f"  {info.filename:30s} {info.file_size:>8d} bytes")
    xml_data = zf.read("Home.xml")

print(f"\nHome.xml: {len(xml_data)} bytes")

# 2. Check file header
with open("stjohns_suite.sh3d", "rb") as f:
    header = f.read(4)
    is_pk = header[:2] == b"PK"
    print(f"ZIP header: {header.hex()} ({'PK' if is_pk else 'NOT PK'})")

# 3. SAX parse test
handler = TestHandler()
try:
    xml.sax.parseString(xml_data, handler)
    print("\n=== SAX Parse: SUCCESS ===")
    print("Element counts:")
    for name, count in sorted(handler.elements.items()):
        print(f"  {name:30s} {count}")
except Exception as e:
    print(f"\n=== SAX Parse: FAILED ===")
    print(f"Error: {e}")

# 4. Verify color format (should be 8-char hex)
import re
xml_str = xml_data.decode("utf-8")
colors = re.findall(r'(?:Color|color)="([^"]+)"', xml_str)
print(f"\n=== Color Format Check ===")
all_ok = True
for c in colors:
    is_hex = bool(re.match(r'^[0-9A-F]{8}$', c))
    if not is_hex:
        print(f"  BAD: {c}")
        all_ok = False
if all_ok:
    print(f"  All {len(colors)} colors are valid 8-char hex")

# 5. Verify observer camera element
if "<observerCamera " in xml_str:
    print("\n=== Observer Camera: <observerCamera> element OK ===")
else:
    print("\n=== Observer Camera: WRONG element! ===")
