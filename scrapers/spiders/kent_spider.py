"""Kent Building Supplies spider.
Scrapes product listings from kent.ca category pages (Magento frontend).
Prices render server-side — no JS/Playwright needed for basic product data.
"""
import re
import scrapy
from scrapers.items import BuildingMaterialItem


class KentSpider(scrapy.Spider):
    name = "kent"
    allowed_domains = ["kent.ca"]

    # All building material categories relevant to backyard suite BOM
    CATEGORIES = {
        "dimensional-lumber": "/en/shop/building-materials/lumber-composites/dimensional-lumber-studs",
        "plywood": "/en/shop/building-materials/lumber-composites/plywood",
        "pressure-treated": "/en/shop/building-materials/lumber-composites/pressure-treated-lumber",
        "insulation-fiberglass": "/en/shop/building-materials/insulation/fiberglass",
        "insulation-rigid": "/en/shop/building-materials/insulation/rigid-insulation",
        "insulation-mineral-wool": "/en/shop/building-materials/insulation/mineral-wool-insulation",
        "drywall": "/en/shop/building-materials/drywall",
        "roofing": "/en/shop/building-materials/roofing",
        "siding": "/en/shop/exterior-siding",
        "concrete": "/en/shop/building-materials/concrete-landscaping-products",
    }

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, category=None, max_pages=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_category = category  # None = all categories
        self.max_pages = int(max_pages)

    def start_requests(self):
        if self.target_category and self.target_category in self.CATEGORIES:
            cats = {self.target_category: self.CATEGORIES[self.target_category]}
        else:
            cats = self.CATEGORIES

        for cat_name, path in cats.items():
            url = f"https://www.kent.ca{path}"
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta={"category": cat_name, "page": 1},
            )

    def parse_category(self, response):
        """Parse a Kent.ca category listing page. Extract product cards."""
        category = response.meta["category"]
        page = response.meta["page"]

        # Kent uses Magento — products are in <li> or <div> with product-item class
        # Based on the HTML we fetched, products appear as linked blocks with price text
        products = response.css("li.product-item, div.product-item, ol.products li")

        if not products:
            # Fallback: try to find product links with prices in page text
            self.logger.info(f"No product-item elements on {response.url}, trying link extraction")
            yield from self._parse_flat_listing(response, category)
            return

        for product in products:
            item = BuildingMaterialItem()

            # Product name
            name_el = product.css("a.product-item-link::text, .product-item-name a::text")
            item["name"] = name_el.get("").strip() if name_el else ""

            # Product URL
            link = product.css("a.product-item-link::attr(href), .product-item-name a::attr(href)")
            item["url"] = link.get("") if link else ""

            # SKU — often in a data attribute or text
            sku_el = product.css("[data-product-sku]::attr(data-product-sku), .sku::text")
            if sku_el:
                item["sku"] = sku_el.get("").strip()
            else:
                # Try to extract from URL (Kent URLs often end with SKU)
                url = item.get("url", "")
                match = re.search(r"-(\d{6,8})$", url)
                item["sku"] = match.group(1) if match else ""

            # Price
            price_el = product.css(".price::text, .special-price .price::text, [data-price-amount]::attr(data-price-amount)")
            raw_price = price_el.get("") if price_el else ""
            item["price"] = raw_price

            # Unit (EA, SH, BG, BD, RL, ft, PK)
            unit_el = product.css(".price-label::text, .uom::text")
            unit_text = unit_el.get("") if unit_el else ""
            item["unit"] = self._extract_unit(unit_text, raw_price)

            # Brand
            brand_el = product.css(".product-brand::text, .brand::text")
            item["brand"] = brand_el.get("").strip() if brand_el else ""

            # Stock
            stock_el = product.css(".stock::text, .availability::text")
            stock_text = stock_el.get("") if stock_el else ""
            item["in_stock"] = "out of stock" not in stock_text.lower()

            # Category
            item["category"] = category
            item["subcategory"] = ""
            item["store"] = "Kent Building Supplies"

            if item["name"]:
                yield item

        # Pagination — follow next page
        if page < self.max_pages:
            next_page = response.css("a.action.next::attr(href), li.pages-item-next a::attr(href)")
            if next_page:
                yield scrapy.Request(
                    next_page.get(),
                    callback=self.parse_category,
                    meta={"category": category, "page": page + 1},
                )

    def _parse_flat_listing(self, response, category):
        """Fallback parser — extract product data from anchor tags with prices."""
        links = response.css("a[href*='/en/']")
        for link in links:
            href = link.attrib.get("href", "")
            text = link.css("::text").get("").strip()

            # Only product pages (have SKU-like suffix)
            if not re.search(r"-\d{6,8}$", href):
                continue
            if not text or len(text) < 5:
                continue

            item = BuildingMaterialItem()
            item["name"] = text
            item["url"] = response.urljoin(href)
            item["sku"] = re.search(r"-(\d{6,8})$", href).group(1)
            item["category"] = category
            item["store"] = "Kent Building Supplies"
            item["in_stock"] = True
            item["price"] = ""
            item["unit"] = ""
            item["brand"] = ""
            item["subcategory"] = ""
            yield item

    @staticmethod
    def _extract_unit(unit_text, price_text):
        """Parse the unit of measure from price label text."""
        combined = f"{unit_text} {price_text}".upper()
        for code in ["/EA", "/SH", "/BG", "/BD", "/RL", "/FT", "/PK", "/LF"]:
            if code in combined:
                return code.strip("/")
        return "EA"
