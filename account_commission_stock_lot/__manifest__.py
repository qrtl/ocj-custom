# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Commission Stock Lot",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "AGPL-3",
    "summary": "Commission line menu with product and lot/serial number",
    "installable": True,
    "depends": [
        "account_commission_oca",
        "account_move_line_stock_lot",
    ],
    "data": [
        "views/commission_settlement_line_views.xml",
    ],
}
