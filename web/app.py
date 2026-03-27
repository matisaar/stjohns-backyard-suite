"""Flask web app — Bill of Materials viewer with live Kent.ca product links.
Adapted from matisaar/calgary-grocery-scraper web/app.py pattern.

Run: python web/app.py
Open: http://127.0.0.1:5000
"""
import os
import sqlite3
import sys

from flask import Flask, render_template, jsonify

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from bom_data import (
    ALL_DIVISIONS, calculate_bom_summary, calculate_division_total,
    get_all_linked_products, NL_HST, WASTE_FACTOR,
)

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(WEB_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(WEB_DIR, "templates"),
    static_folder=os.path.join(WEB_DIR, "static"),
)

DB_PATH = os.path.join(PROJECT_ROOT, "data", "building_materials.db")


def get_db():
    """Connect to scraped materials database if it exists."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_prices():
    """Fetch latest scraped prices keyed by SKU."""
    db = get_db()
    if not db:
        return {}
    try:
        rows = db.execute("""
            SELECT sku, price, scraped_date
            FROM materials
            WHERE sku != ''
            ORDER BY scraped_date DESC
        """).fetchall()
        prices = {}
        for row in rows:
            sku = row["sku"]
            if sku not in prices:
                prices[sku] = {"price": row["price"], "date": row["scraped_date"]}
        return prices
    finally:
        db.close()


@app.route("/")
def index():
    """Main BOM view."""
    summary = calculate_bom_summary()
    latest_prices = get_latest_prices()

    # Attach scraped price updates to divisions
    divisions_data = []
    for div in ALL_DIVISIONS:
        div_items = []
        for item in div["items"]:
            item_data = dict(item)
            item_data["extended"] = item["qty"] * item["unit_price"]
            # Check if we have a newer scraped price
            sku = item.get("sku", "")
            if sku and sku in latest_prices:
                scraped = latest_prices[sku]
                item_data["scraped_price"] = scraped["price"]
                item_data["scraped_date"] = scraped["date"]
                if scraped["price"] != item["unit_price"] and scraped["price"] > 0:
                    item_data["price_changed"] = True
                    item_data["scraped_extended"] = item["qty"] * scraped["price"]
            div_items.append(item_data)

        divisions_data.append({
            "name": div["name"],
            "line_items": div_items,
            "total": calculate_division_total(div),
        })

    return render_template(
        "index.html",
        divisions=divisions_data,
        summary=summary,
        hst_rate=NL_HST * 100,
        waste_rate=WASTE_FACTOR * 100,
        has_scraped_data=bool(latest_prices),
    )


@app.route("/model")
def model_view():
    """Interactive 3D building model with cross-section views."""
    summary = calculate_bom_summary()
    return render_template("model.html", summary=summary)


@app.route("/render")
def render_view():
    """Interactive material stack cross-section renderer."""
    # Pull foundation/flooring layers from BOM divisions
    layers = []
    div_map = {d["name"]: d for d in ALL_DIVISIONS}

    # Division 2: Site Work & Foundation
    site = div_map.get("Site Work & Foundation", {})
    for item in site.get("items", []):
        layers.append(dict(item))

    # Division 6: Insulation & Air Barrier (floor-relevant items)
    ins = div_map.get("Insulation & Air Barrier", {})
    for item in ins.get("items", []):
        layers.append(dict(item))

    # Division 7: Interior Finishes (flooring)
    fin = div_map.get("Interior Finishes", {})
    for item in fin.get("items", []):
        layers.append(dict(item))

    summary = calculate_bom_summary()
    return render_template("render.html", layers=layers, summary=summary)


@app.route("/finishes")
def finishes():
    """Finish board — every visible surface and fixture."""
    # Define which items a human sees, grouped by area
    FINISH_CATEGORIES = [
        ("Exterior", "Exterior Envelope", [
            "Mitten Oregon Pride",
            "Aluminum Fascia",
            "Triple-Pane Vinyl",
            "Steel Insulated Entry Door",
            "Dusco Moderna",
        ]),
        ("Roofing", "Roofing", [
            "IKO Cambridge",
        ]),
        ("Flooring & Tile", "Interior Finishes", [
            "Volcano",
            "White Large-Format Ceramic",
        ]),
        ("Walls & Trim", "Interior Finishes", [
            "Sico Evolution",
            "Alexandria",
        ]),
        ("Kitchen", "Kitchen", None),  # all items
        ("Bathroom Fixtures", "Plumbing", [
            "Toilet",
            "Vanity",
            "Shower Stall",
            "Shower Valve",
            "Bathroom Faucet",
        ]),
        ("Kitchen Plumbing", "Plumbing", [
            "Kitchen Sink",
            "Kitchen Faucet",
        ]),
        ("Laundry", "Laundry", [
            "Front Load Washer",
            "GE 24",
        ]),
    ]

    div_map = {d["name"]: d for d in ALL_DIVISIONS}
    sections = []
    for section_name, div_name, keywords in FINISH_CATEGORIES:
        div = div_map.get(div_name, {})
        items = []
        for item in div.get("items", []):
            if keywords is None:
                items.append(item)
            elif any(kw.lower() in item["name"].lower() for kw in keywords):
                items.append(item)
        if items:
            sections.append({"name": section_name, "products": items})

    summary = calculate_bom_summary()
    return render_template("finishes.html", sections=sections, summary=summary)


@app.route("/api/summary")
def api_summary():
    """JSON API for BOM summary."""
    return jsonify(calculate_bom_summary())


@app.route("/api/products")
def api_products():
    """JSON API for all linked products."""
    return jsonify(get_all_linked_products())


@app.route("/api/scraped")
def api_scraped():
    """JSON API for latest scraped prices."""
    return jsonify(get_latest_prices())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
