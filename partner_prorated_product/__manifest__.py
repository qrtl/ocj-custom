# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Partner Prorated Equipment",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Narrow a customer's prorated billing to specific equipment",
    "installable": True,
    "depends": ["partner_billing_policy", "product_classification"],
    "data": [
        "views/res_partner_views.xml",
    ],
}
