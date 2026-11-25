# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import csv
from collections import defaultdict

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools import date_utils, float_repr

DELIMITER = "OBCD001"  # "*" marks the first row of an OBC entry
DATE = "CSJS005"
REMARKS = "CSJS100"
# Debit and credit column codes, in the order of the values of a row key.
SIDE_COLUMNS = {
    "account": {"dr": "CSJS201", "cr": "CSJS301"},
    "subaccount": {"dr": "CSJS202", "cr": "CSJS302"},
    "department": {"dr": "CSJS200", "cr": "CSJS300"},
    "tax_categ": {"dr": "CSJS203", "cr": "CSJS303"},
    "tax_rate_type": {"dr": "CSJS222", "cr": "CSJS322"},
    "tax_rate": {"dr": "CSJS220", "cr": "CSJS320"},
}
TAX_AUTO_CALC = {"dr": "CSJS206", "cr": "CSJS306"}
BASE_AMOUNT = {"dr": "CSJS213", "cr": "CSJS313"}
TAX_AMOUNT = {"dr": "CSJS214", "cr": "CSJS314"}


class AccountMoveObcCsv(models.AbstractModel):
    _name = "report.account_move_obc_csv.report_obc_csv"
    _inherit = "report.report_csv.abstract"
    _description = "OBC CSV Report"

    def _get_fields(self):
        return [
            DELIMITER,
            DATE,
            *[
                codes[drcr]
                for drcr in ("dr", "cr")
                for codes in (
                    SIDE_COLUMNS["department"],
                    SIDE_COLUMNS["account"],
                    SIDE_COLUMNS["subaccount"],
                    SIDE_COLUMNS["tax_categ"],
                    SIDE_COLUMNS["tax_rate_type"],
                    SIDE_COLUMNS["tax_rate"],
                    TAX_AUTO_CALC,
                    BASE_AMOUNT,
                    TAX_AMOUNT,
                )
            ],
            REMARKS,
        ]

    @api.model
    def _get_entry_key(self, line):
        """Return the (date, journal, is cost of sales) of a journal item's entry."""
        is_cogs = line.display_type == "cogs"
        if is_cogs or line.journal_id.obc_aggregation == "month":
            return date_utils.end_of(line.date, "month"), line.journal_id, is_cogs
        return line.date, line.journal_id, is_cogs

    @api.model
    def _get_row_key(self, line):
        """Return the values journal items must share to be summed into one row."""
        company = line.company_id
        account = line.account_id.with_company(company)
        # "111.2" is account 111, sub-account 2 in OBC.
        account_code, _sep, subaccount_code = (account.code or "").partition(".")
        department = self.env["account.analytic.account"]
        if account.internal_group in ("income", "expense"):
            department = line.distribution_analytic_account_ids.filtered(
                "obc_department_code"
            )[:1]
        tax = line.tax_ids[:1]
        return (
            bool(line.tax_line_id),  # sorts the tax rows last
            account_code,
            subaccount_code,
            department.obc_department_code or company.obc_default_department_code or "",
            # tax_categ '0' means non-taxable (対象外)
            tax.obc_tax_category or "0",
            tax.obc_tax_rate_type or line.tax_line_id.obc_tax_rate_type or "",
            tax.amount or "",
        )

    @api.model
    def _get_remarks(self, export, journal, is_cogs):
        text = f"{export.name} {journal.name}"
        if is_cogs:
            text += " " + self.env._("Cost of Sales")
        remarks, width = "", 0
        for char in text:
            # The column holds 40 half-width characters; a full-width one counts two.
            width += len(char.encode("cp932", "replace"))
            if width > 40:
                break
            remarks += char
        return remarks

    def _get_entries(self, export):
        """Return {entry key: {"dr": {row key: amount}, "cr": {...}}}."""
        entries = defaultdict(
            lambda: {"dr": defaultdict(float), "cr": defaultdict(float)}
        )
        for line in export.move_ids.line_ids:
            amount = line.debit or line.credit
            if amount:
                drcr = "dr" if line.debit else "cr"
                entry = entries[self._get_entry_key(line)]
                entry[drcr][self._get_row_key(line)] += amount
        return entries

    def _get_rows(self, export, entry_key, sides):
        date, journal, is_cogs = entry_key
        currency = export.company_id.currency_id
        if currency.compare_amounts(
            sum(sides["dr"].values()), sum(sides["cr"].values())
        ):
            raise UserError(
                self.env._(
                    "The journal items of %(journal)s on %(date)s do not balance.",
                    journal=journal.display_name,
                    date=date,
                )
            )
        rows = []
        for drcr in ("dr", "cr"):
            # Tax rows last, then the largest amount first.
            items = sorted(sides[drcr].items(), key=lambda x: (x[0][0], -x[1]))
            for index, (row_key, amount) in enumerate(items):
                # The first debit row and the first credit row share the first row.
                if index == 0 and rows:
                    vals = rows[0]
                else:
                    vals = {
                        DATE: date.strftime("%Y/%m/%d"),
                        REMARKS: self._get_remarks(export, journal, is_cogs),
                    }
                    rows.append(vals)
                for codes, value in zip(
                    SIDE_COLUMNS.values(), row_key[1:], strict=True
                ):
                    vals[codes[drcr]] = value
                vals[TAX_AUTO_CALC[drcr]] = 0  # No tax calculation
                vals[BASE_AMOUNT[drcr]] = float_repr(amount, currency.decimal_places)
        rows[0][DELIMITER] = "*"
        return rows

    def generate_csv_report(self, writer, data, records):
        writer.writeheader()
        for export in records:
            entries = self._get_entries(export)
            for entry_key in sorted(
                entries, key=lambda x: (x[0], x[1].sequence, x[1].id, x[2])
            ):
                writer.writerows(self._get_rows(export, entry_key, entries[entry_key]))

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].extend(self._get_fields())
        res["delimiter"] = ","
        res["quoting"] = csv.QUOTE_MINIMAL
        return res
