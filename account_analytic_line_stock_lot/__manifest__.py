# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Account Analytic Line Stock Lot",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Show the lot/serial number of the journal item on analytic items",
    "installable": True,
    "depends": ["account_move_line_stock_lot"],
    "data": [
        "views/account_analytic_line_views.xml",
    ],
}
