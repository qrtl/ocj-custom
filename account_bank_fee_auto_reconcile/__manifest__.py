# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Bank Fee Auto Reconciliation",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainer": "Quartile",
    "license": "LGPL-3",
    "summary": "Let the bank fee reconciliation model post its entry automatically",
    "installable": True,
    "depends": ["account_accountant"],
    "post_init_hook": "post_init_hook",
}
