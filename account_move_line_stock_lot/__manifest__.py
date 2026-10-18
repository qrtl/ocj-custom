# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Account Move Line Stock Lot",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Record the lot/serial number on journal items",
    "installable": True,
    "depends": ["account", "stock"],
    "data": [
        "views/account_move_views.xml",
    ],
}
