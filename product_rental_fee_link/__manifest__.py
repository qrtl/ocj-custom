# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Product Rental Fee Link",
    "version": "19.0.1.1.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Record the set of equipment a rental fee service product "
    "bills, and look a product up by that combination",
    "installable": True,
    "depends": ["product_classification"],
    "data": [
        "views/product_template_views.xml",
    ],
}
