# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Product Rental Fee Link",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Link an equipment product to the service product used to bill "
    "its rental",
    "installable": True,
    "depends": ["product_classification"],
    "data": [
        "views/product_template_views.xml",
    ],
}
