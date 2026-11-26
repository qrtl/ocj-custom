# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Asset Category",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["kanda999"],
    "license": "LGPL-3",
    "summary": "Record who owns each serial/lot number, defaulted from its product",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/stock_lot_asset_category_views.xml",
        "views/product_template_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_quant_views.xml",
    ],
}
