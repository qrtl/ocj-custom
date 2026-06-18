# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Installation Status",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainer": "Quartile",
    "license": "LGPL-3",
    "summary": "Track installation status on serial/lot numbers",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/stock_lot_views.xml",
        "views/stock_quant_views.xml",
    ],
}
