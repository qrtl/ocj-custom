# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Pricelist Item Proration",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Hold whether a rental price is prorated, and how, per customer "
    "and product",
    "installable": True,
    "depends": ["product"],
    "data": [
        "views/product_pricelist_item_views.xml",
    ],
}
