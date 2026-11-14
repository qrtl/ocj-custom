# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from collections import defaultdict

from odoo import Command, models


class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    def _get_amounts_by_analytic_distribution(self):
        """Split the settlement total by the analytic distribution of the settled
        invoice lines."""
        amounts = defaultdict(float)
        for line in self.line_ids:
            distribution = line.invoice_line_id.analytic_distribution or {}
            amounts[frozenset(distribution.items())] += line.settled_amount
        return {
            key: self.currency_id.round(amount)
            for key, amount in amounts.items()
            if not self.currency_id.is_zero(amount)
        }

    def _prepare_invoice(self, journal, product, date=False):
        vals = super()._prepare_invoice(journal, product, date=date)
        line_commands = []
        for command in vals["invoice_line_ids"]:
            line_vals = command[2]
            settlement = self.browse(line_vals.get("settlement_id"))
            amounts = settlement._get_amounts_by_analytic_distribution()
            if not any(amounts):
                line_commands.append(command)
                continue
            for distribution, amount in amounts.items():
                split_vals = {
                    **line_vals,
                    "quantity": -1 if amount < 0 else 1,
                    "price_unit": abs(amount),
                }
                if distribution:
                    split_vals["analytic_distribution"] = dict(distribution)
                line_commands.append(Command.create(split_vals))
        vals["invoice_line_ids"] = line_commands
        return vals
