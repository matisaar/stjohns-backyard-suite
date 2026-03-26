"""Data model for scraped building materials.
Adapted from calgary-grocery-scraper items.py pattern.
"""
import scrapy


class BuildingMaterialItem(scrapy.Item):
    name = scrapy.Field()
    sku = scrapy.Field()
    price = scrapy.Field()          # float, CAD
    unit = scrapy.Field()           # EA, SH, BG, BD, RL, ft, PK, etc.
    category = scrapy.Field()       # e.g. "dimensional-lumber", "plywood"
    subcategory = scrapy.Field()
    brand = scrapy.Field()
    url = scrapy.Field()
    in_stock = scrapy.Field()       # bool
    store = scrapy.Field()          # "Kent Building Supplies"
    scraped_date = scrapy.Field()   # ISO date string
    image_url = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
