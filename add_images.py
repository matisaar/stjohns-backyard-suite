"""Add image_url fields to bom_data.py for all items that have downloaded images."""
import re, os

IMAGES_DIR = "web/static/images"
available_images = {f.replace('.jpg', '') for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')}

with open("bom_data.py", "r") as f:
    content = f.read()

# For each Kent.ca URL in bom_data.py, extract SKU and add image_url if:
# 1. The image file exists
# 2. There's no image_url already on that item

# Pattern: find blocks like "url": f"{KENT_BASE}/...-SKU" or "url": "https://kent.ca/en/...-SKU"
# that do NOT already have "image_url" nearby

lines = content.split('\n')
new_lines = []
i = 0
added = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Check if this is a url line with a kent.ca reference
    if '"url":' in line and ('KENT_BASE' in line or 'kent.ca' in line):
        # Extract SKU from the URL
        sku_match = re.search(r'-(\d{5,})["\']', line)
        if sku_match:
            sku = sku_match.group(1)
            # Check if image exists
            if sku in available_images:
                # Look ahead to see if image_url already exists within the next 3 lines
                has_image = False
                for j in range(1, 5):
                    if i + j < len(lines) and 'image_url' in lines[i + j]:
                        has_image = True
                        break
                    if i + j < len(lines) and '"name"' in lines[i + j]:
                        break  # Next item started
                    if i + j < len(lines) and '},' in lines[i + j].strip():
                        break  # Item ended
                
                if not has_image:
                    # Get indentation from current line
                    indent = re.match(r'^(\s*)', line).group(1)
                    # Insert image_url after the notes line (or after url if no notes)
                    # Actually, let's find the notes line and add after it
                    # For now, add right after the url line before notes
                    # Check next line - if it's notes, add after notes
                    if i + 1 < len(lines) and '"notes"' in lines[i + 1]:
                        # Add notes line first, then image_url
                        pass  # Will handle below
                    else:
                        # Insert image_url right after url
                        new_lines.append(f'{indent}"image_url": "/static/images/{sku}.jpg",')
                        added += 1
    
    # Also handle: add image_url after "notes" line if the preceding url was kent.ca with a valid SKU
    if '"notes":' in line and i >= 1:
        # Check if previous line was a kent URL
        prev_url_line = None
        for j in range(1, 4):
            if i - j >= 0 and '"url":' in lines[i - j]:
                prev_url_line = lines[i - j]
                break
        if prev_url_line and ('KENT_BASE' in prev_url_line or 'kent.ca' in prev_url_line):
            sku_match = re.search(r'-(\d{5,})["\']', prev_url_line)
            if sku_match:
                sku = sku_match.group(1)
                if sku in available_images:
                    # Check if image_url already exists nearby
                    has_image = False
                    for j in range(1, 4):
                        if i + j < len(lines) and 'image_url' in lines[i + j]:
                            has_image = True
                            break
                        if i + j < len(lines) and ('"name"' in lines[i + j] or '},' in lines[i + j].strip()):
                            break
                    # Also check lines already added
                    if not has_image and len(new_lines) >= 2:
                        for nl in new_lines[-3:]:
                            if 'image_url' in nl:
                                has_image = True
                                break
                    
                    if not has_image:
                        indent = re.match(r'^(\s*)', line).group(1)
                        # Check if this notes line ends with a comma (single line) or continues
                        if line.rstrip().endswith('",'):
                            new_lines.append(f'{indent}"image_url": "/static/images/{sku}.jpg",')
                            added += 1
    
    i += 1

with open("bom_data.py", "w") as f:
    f.write('\n'.join(new_lines))

print(f"Added image_url to {added} items")
