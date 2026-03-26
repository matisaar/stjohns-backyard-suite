import re

with open('bom_data.py', 'r') as f:
    lines = f.readlines()

in_item = False
current_item = {}
item_start = None
results = []

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == '{':
        in_item = True
        current_item = {}
        item_start = i
    elif stripped.startswith('}') and in_item:
        if 'image_url' not in current_item:
            results.append((current_item.get('name', 'UNKNOWN'), item_start+1, i+1))
        in_item = False
    elif in_item:
        m = re.search(r'"name"\s*:\s*"(.+?)"', stripped)
        if m:
            current_item['name'] = m.group(1)
        if '"image_url"' in stripped:
            current_item['image_url'] = True

for name, start, end in results:
    print(f"Line {start}-{end}: {name}")
print(f"\nTotal missing: {len(results)}")
