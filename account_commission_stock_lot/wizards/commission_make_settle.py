# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    def _prepare_settlement_line_vals(self, settlement, line):
        """Snapshot the source invoice line info at settlement time, so that a later
        change on the source invoice line does not rewrite the settlement.
        """
        res = super()._prepare_settlement_line_vals(settlement, line)
        if self.settlement_type == "sale_invoice":
            invoice_line = line.object_id
            res.update(
                {
                    "product_id": invoice_line.product_id.id,
                    "lot_id": invoice_line.lot_id.id,
                }
            )
        return res
