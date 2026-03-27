#!/usr/bin/env python3
"""Check which price corrections were applied"""
checks = [
    ('10/3 NMD90 Wire', 80.00, 469.99),
    ('XPS Rigid Exterior', 40.00, 112.99),
    ('Matte Black Vanity', 499.00, 549.00),
    ('Refrigerator', 1395.00, 1445.00),
    ('Triple-Pane Vinyl Casement', 431.10, 479.00),
    ('Toilet', 229.99, 269.99),
    ('LED Slim Recessed', 87.99, 109.99),
    ('Volcano', 74.96, 88.19),
    ('R-20 Fiberglass Batt 15', 93.99, 89.57),
    ('Roof Vent', 17.59, 21.50),
    ('Washer Box', 19.12, 22.49),
    ('Soffit', 12.42, 14.42),
    ('IKO Cambridge', 42.99, 40.99),
    ('2x4x10', 5.97, 6.38),
    ('2x4x8', 4.28, 3.98),
    ('Receptacles', 2.09, 2.39),
]
with open('bom_data.py') as f:
    src = f.read()
src_lower = src.lower()
for name, old, new in checks:
    old_s = f'{old:.2f}'
    new_s = f'{new:.2f}'
    safe = name[:20].lower()
    has_new = new_s in src
    has_old = old_s in src
    has_name = safe in src_lower
    if has_new and has_name:
        print(f'  OK    {name}: {new_s}')
    elif has_old and has_name:
        print(f'  FAIL  {name}: still {old_s} (need {new_s})')
    else:
        print(f'  ???   {name}: name={has_name} old={has_old} new={has_new}')
