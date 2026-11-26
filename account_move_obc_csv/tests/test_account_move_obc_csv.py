# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import csv
from io import StringIO

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveObcCsv(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.company_data["default_tax_sale"]
        cls.tax.write({"obc_tax_category": "60", "obc_tax_rate_type": "0"})
        cls.account_revenue = cls.company_data["default_account_revenue"]
        cls.account_revenue.code = "500.2"
        cls.account_expense = cls.company_data["default_account_expense"]
        cls.account_stock = cls.company_data["default_account_assets"]
        cls.env.company.obc_default_department_code = "0"
        plan = cls.env["account.analytic.plan"].create({"name": "Departments"})
        cls.department_a, cls.department_b = cls.env["account.analytic.account"].create(
            [
                {"name": "A", "plan_id": plan.id, "obc_department_code": "101"},
                {"name": "B", "plan_id": plan.id, "obc_department_code": "102"},
            ]
        )
        # Two invoices of department A and one of department B, on the same day.
        cls.invoices = cls.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": cls.partner_a.id,
                    "invoice_date": "2026-10-15",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Service",
                                "quantity": 1,
                                "price_unit": price_unit,
                                "account_id": cls.account_revenue.id,
                                "tax_ids": [Command.set(cls.tax.ids)],
                                "analytic_distribution": {str(department.id): 100},
                            }
                        ),
                        Command.create(
                            {"name": "Free", "quantity": 1, "price_unit": 0.0}
                        ),
                    ],
                }
                for price_unit, department in (
                    (1000.0, cls.department_a),
                    (2000.0, cls.department_a),
                    (4000.0, cls.department_b),
                )
            ]
        )
        # Cost of sales as stock_account adds it to an invoice.
        cls.env["account.move.line"].create(
            [
                {
                    "move_id": cls.invoices[0].id,
                    "display_type": "cogs",
                    "name": "Cost",
                    "account_id": account.id,
                    "debit": debit,
                    "credit": credit,
                    "analytic_distribution": {str(cls.department_a.id): 100},
                }
                for account, debit, credit in (
                    (cls.account_expense, 300.0, 0.0),
                    (cls.account_stock, 0.0, 300.0),
                )
            ]
        )
        cls.invoices.action_post()
        cls.export = cls.env["account.move.obc.export"].create(
            {"date_from": "2026-10-01", "date_to": "2026-10-31"}
        )

    def _export(self, export):
        action = export.action_export()
        content = self.env["ir.actions.report"]._render_csv(
            action["report_name"], export.ids, {}
        )[0]
        return list(csv.DictReader(StringIO(content.decode("cp932"))))

    def test_export_aggregates(self):
        # Row summing, entry dates, departments and the tax rows at the end.
        rows = self._export(self.export)
        receivable = self.company_data["default_account_receivable"]
        decimals = self.env.company.currency_id.decimal_places
        self.assertEqual(self.export.move_ids, self.invoices)
        self.assertEqual([row["OBCD001"] for row in rows], ["*", "", "", "*"])
        first, second, tax_row, cogs = rows
        self.assertEqual(first["CSJS005"], "2026/10/15")
        self.assertEqual(first["CSJS201"], receivable.code)
        self.assertEqual(first["CSJS200"], "0")
        self.assertEqual(first["CSJS203"], "0")
        self.assertEqual(
            first["CSJS213"],
            f"{sum(self.invoices.mapped('amount_total')):.{decimals}f}",
        )
        self.assertEqual(
            [first[code] for code in ("CSJS301", "CSJS302", "CSJS300", "CSJS303")],
            ["500", "2", "102", "60"],
        )
        self.assertEqual(float(first["CSJS313"]), 4000.0)
        self.assertEqual(float(first["CSJS320"]), self.tax.amount)
        self.assertEqual(first["CSJS306"], "0")
        self.assertEqual(second["CSJS201"], "")
        self.assertEqual(second["CSJS300"], "101")
        self.assertEqual(float(second["CSJS313"]), 3000.0)
        self.assertEqual(tax_row["CSJS300"], "0")
        self.assertEqual(tax_row["CSJS303"], "0")
        self.assertEqual(
            float(tax_row["CSJS313"]), sum(self.invoices.mapped("amount_tax"))
        )
        self.assertEqual(cogs["CSJS005"], "2026/10/31")
        self.assertEqual(cogs["CSJS201"], self.account_expense.code)
        self.assertEqual(cogs["CSJS200"], "101")
        self.assertEqual(cogs["CSJS301"], self.account_stock.code)
        self.assertEqual(cogs["CSJS300"], "0")
        self.assertEqual(float(cogs["CSJS213"]), 300.0)
        self.assertTrue(first["CSJS100"].startswith(self.export.name))
        self.assertLessEqual(len(cogs["CSJS100"].encode("cp932")), 40)

    def test_export_scope(self):
        # Exported once, excluded journals never, monthly journals at month end.
        journal = self.company_data["default_journal_misc"]
        entries = self.env["account.move"].create(
            [
                {
                    "journal_id": journal.id,
                    "date": date,
                    "line_ids": [
                        Command.create(
                            {"account_id": self.account_expense.id, "debit": 50.0}
                        ),
                        Command.create(
                            {"account_id": self.account_stock.id, "credit": 50.0}
                        ),
                    ],
                }
                for date in ("2026-10-10", "2026-10-20")
            ]
        )
        entries.action_post()
        self.invoices.journal_id.obc_export_excluded = True
        journal.obc_aggregation = "month"
        rows = self._export(self.export)
        self.assertEqual(self.export.move_ids, entries)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["CSJS005"], "2026/10/31")
        self.assertEqual(float(rows[0]["CSJS213"]), 100.0)
        self.invoices.journal_id.obc_export_excluded = False
        other = self.export.copy()
        self._export(other)
        self.assertEqual(other.move_ids, self.invoices)
        self.assertEqual(len(self._export(self.export)), 1)
        with self.assertRaises(UserError):
            self._export(self.export.copy())
        with self.assertRaises(UserError):
            entries.button_draft()
        self.export.unlink()
        entries.button_draft()

    def test_export_department_split(self):
        journal = self.company_data["default_journal_misc"]
        project = self.env["account.analytic.account"].create(
            {
                "name": "P",
                "plan_id": self.env["account.analytic.plan"].create({"name": "X"}).id,
            }
        )
        entry = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "date": "2026-10-10",
                "line_ids": [
                    Command.create(
                        {
                            "account_id": self.account_expense.id,
                            "debit": 100.0,
                            "analytic_distribution": {
                                str(self.department_a.id): 60,
                                str(self.department_b.id): 40,
                                str(project.id): 100,
                            },
                        }
                    ),
                    Command.create(
                        {"account_id": self.account_stock.id, "credit": 100.0}
                    ),
                ],
            }
        )
        entry.action_post()
        self.invoices.journal_id.obc_export_excluded = True
        rows = self._export(self.export)
        self.assertEqual(
            [(row["CSJS200"], float(row["CSJS213"])) for row in rows],
            [("101", 60.0), ("102", 40.0)],
        )
        self.assertEqual(float(rows[0]["CSJS313"]), 100.0)
