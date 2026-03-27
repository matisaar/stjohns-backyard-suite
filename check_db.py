#!/usr/bin/env python3
"""Check DB for IKO shingles and scraper behavior"""
import sqlite3
import os

db_path = 'data/building_materials.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

for table_name, in tables:
    cursor.execute(f"SELECT * FROM [{table_name}] LIMIT 5")
    cols = [d[0] for d in cursor.description]
    print(f"\n--- {table_name} columns: {cols} ---")
    for row in cursor.fetchall():
        print(row)

# Search for IKO shingles
cursor.execute("SELECT * FROM materials WHERE sku LIKE '%1010785%' OR name LIKE '%IKO%' OR name LIKE '%shingle%'")
results = cursor.fetchall()
print("\nIKO shingles results:")
for r in results:
    print(r)

# Also check today's scrape date
cursor.execute("SELECT DISTINCT scraped_date FROM materials ORDER BY scraped_date DESC LIMIT 5")
print("\nScrape dates:", cursor.fetchall())

# Check 10/3 wire, countertop, siding, XPS
for sku in ['1026026', '1015537', '1598067', '1694221']:
    cursor.execute("SELECT sku, name, price, bom_price FROM materials WHERE sku=?", (sku,))
    r = cursor.fetchone()
    if r:
        print(f"\n{sku}: {r}")

conn.close()
