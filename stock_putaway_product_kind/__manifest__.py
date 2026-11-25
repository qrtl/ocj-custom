# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Putaway Product Kind",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yurikamori33"],
    "license": "LGPL-3",
    "summary": "Putaway rules that apply to one product kind",
    "installable": True,
    "depends": ["stock", "product_classification"],
    "data": [
        "views/stock_putaway_rule_views.xml",
    ],
}
