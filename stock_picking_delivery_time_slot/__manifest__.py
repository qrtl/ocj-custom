# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Picking Delivery Time Slot",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Record the requested delivery time slot on transfers",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_delivery_time_slot_views.xml",
        "views/stock_picking_views.xml",
    ],
}
