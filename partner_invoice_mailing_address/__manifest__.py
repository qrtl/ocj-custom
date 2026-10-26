# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Partner Invoice Mailing Address",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["smorita7749"],
    "license": "AGPL-3",
    "summary": "Print a customer's invoice mailing address on invoices and summary "
    "invoices",
    "installable": True,
    "depends": ["l10n_jp_summary_invoice"],
    "data": [
        "reports/report_templates.xml",
        "views/res_partner_views.xml",
    ],
}
