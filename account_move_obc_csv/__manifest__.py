# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move OBC CSV",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["kanda999"],
    "license": "AGPL-3",
    "summary": "Export journal entries as CSV for the OBC (Bugyo) accounting system",
    "installable": True,
    "depends": ["account", "report_csv"],
    "data": [
        "security/account_move_obc_export_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/obc_csv_report_data.xml",
        "views/account_analytic_account_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_obc_export_views.xml",
        "views/account_move_views.xml",
        "views/account_tax_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
