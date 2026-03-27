# St. John's 430 sqft Backyard Suite — Bill of Materials

A comprehensive BOM tracker with live pricing for a **430 sqft backyard suite** in St. John's, NL. Includes a Kent.ca web scraper for real-time lumber & material pricing and a Flask dashboard to view the complete bill of materials.

## Design

- **Footprint**: 20' × 21.5' (430 sqft)
- **Layout**: 2 bedrooms, 2 bathrooms, kitchen, entry with laundry — symmetrical, no living room
- **Structure**: 2×6 wood frame @ 16" OC, FPSF foundation
- **Roof**: Mono-slope 3:12 pitch (8' → 12'), sloping up toward entrance, max 5m height
- **Insulation**: Zone 7A — R-24 walls, R-50 ceiling, R-10 under-slab
- **Budget**: Under $100K CAD

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# View the BOM in your browser (static prices)
python -m web.app
# Open http://localhost:5000

# Scrape live Kent.ca prices
python run_scraper.py --all

# Scrape a single category
python run_scraper.py --category dimensional-lumber --max-pages 2

# List available scraper categories
python run_scraper.py --list-categories
```

## Project Structure

```
stjohns-backyard-suite/
├── bom_data.py              # Complete 12-division BOM with pricing
├── run_scraper.py            # CLI to run the Kent.ca scraper
├── scrapy.cfg
├── scrapers/
│   ├── items.py              # BuildingMaterialItem model
│   ├── pipelines.py          # Cleaning, dedup, SQLite, CSV pipelines
│   ├── settings.py           # Scrapy configuration
│   ├── spiders/
│   │   └── kent_spider.py    # Kent Building Supplies spider
│   └── middlewares/
│       ├── anti_detection.py # UA rotation & realistic headers
│       └── smart_retry.py    # Exponential backoff retry
├── web/
│   ├── app.py                # Flask application
│   └── templates/
│       └── index.html        # BOM dashboard template
├── data/                     # Auto-created by scraper
│   ├── building_materials.db # SQLite database
│   └── *.csv                 # Per-category CSV exports
└── requirements.txt
```

## Suppliers

| Supplier               | Categories                                                      | Link                                       |
| ---------------------- | --------------------------------------------------------------- | ------------------------------------------ |
| Kent Building Supplies | Lumber, plywood, insulation, drywall, roofing, siding, concrete | [kent.ca](https://www.kent.ca)             |
| Home Depot Canada      | Windows, doors, appliances                                      | [homedepot.ca](https://www.homedepot.ca)   |
| IKEA Canada            | Kitchen cabinets & countertops                                  | [ikea.com/ca](https://www.ikea.com/ca/en/) |

## BOM Divisions

1. **General Requirements** — permits, survey, engineering, insurance
2. **Site Work & Foundation** — excavation, frost-protected shallow foundation, concrete
3. **Framing** — 2×6 walls, floor, roof trusses, sheathing
4. **Exterior Envelope** — siding, housewrap, windows, doors
5. **Roofing** — IKO Cambridge shingles, ice & water shield, drip edge
6. **Insulation & Air Barrier** — R-20 batts, R-28/R-31 ceiling, XPS sub-slab, poly barrier
7. **Interior Finishes** — drywall, flooring, paint, trim, doors
8. **Plumbing** — rough-in, fixtures, water heater
9. **Electrical** — panel, wiring, fixtures, smoke/CO
10. **HVAC** — Mitsubishi mini-split, baseboard backup, HRV, bath fans
11. **Kitchen** — IKEA cabinets, countertop, sink, appliances
12. **Laundry** — washer/dryer, hookups

## Updating Prices

Run the scraper to fetch current Kent.ca prices. The Flask app compares scraped prices to BOM estimates and highlights changes:

```bash
python run_scraper.py --all --max-pages 3
python -m web.app
```

Scraped data is stored in `data/building_materials.db` (SQLite) and exported to `data/*.csv`.
