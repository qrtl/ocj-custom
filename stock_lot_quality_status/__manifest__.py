# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Quality Status",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Assign a configurable quality status to serial/lot numbers",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_lot_quality_status_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_quant_views.xml",
    ],
}
