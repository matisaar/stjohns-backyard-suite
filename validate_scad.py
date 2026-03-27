import re

with open("stjohns_suite.scad") as f:
    code = f.read()

lines = code.split('\n')
print(f"File: {len(lines)} lines, {len(code)} chars")

counts = {'(': 0, ')': 0, '[': 0, ']': 0, '{': 0, '}': 0}
for ch in code:
    if ch in counts:
        counts[ch] += 1

print(f"Parens:   ( {counts['(']}  ) {counts[')']}  {'OK' if counts['(']==counts[')'] else 'MISMATCH!'}")
print(f"Brackets: [ {counts['[']}  ] {counts[']']}  {'OK' if counts['[']==counts[']'] else 'MISMATCH!'}")
b_open, b_close = counts['{'], counts['}']
print(f"Braces:   open {b_open}  close {b_close}  {'OK' if b_open==b_close else 'MISMATCH!'}")

modules = re.findall(r'module\s+(\w+)\s*\(', code)
print(f"\nModules defined: {len(modules)}")
for m in modules:
    print(f"  - {m}")

print("\nValidation complete.")
