# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Partner Payer",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainer": "Quartile",
    "license": "LGPL-3",
    "summary": "Record the contact that settles a customer's invoices",
    "installable": True,
    "depends": ["account"],
    "data": [
        "views/res_partner_views.xml",
    ],
}
