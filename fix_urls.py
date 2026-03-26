"""Remove all category-level URLs from bom_data.py, keeping only exact product links."""
import re

with open("bom_data.py", "r") as f:
    content = f.read()

# Match any URL containing kent.ca/en/shop/ or homedepot.ca/en/home/categories/
count = 0
lines = content.split('\n')
new_lines = []
for line in lines:
    if '"url"' in line:
        url_match = re.search(r'"url":\s*"(https?://[^"]+)"', line)
        if url_match:
            url = url_match.group(1)
            if 'kent.ca/en/shop/' in url or 'homedepot.ca/en/home/categories/' in url:
                new_line = line.replace(url, '')
                new_lines.append(new_line)
                count += 1
                print(f"Removed: {url}")
                continue
    new_lines.append(line)

with open("bom_data.py", "w") as f:
    f.write('\n'.join(new_lines))

print(f"\nTotal category URLs removed: {count}")
