# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CommissionSettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    product_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_invoice_line_info",
        store=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial Number",
        compute="_compute_invoice_line_info",
        store=True,
    )

    @api.depends("invoice_agent_line_id")
    def _compute_invoice_line_info(self):
        """Snapshot the source invoice line info at settlement time.
        The dependency is deliberately not dotted: a settlement line is a
        historical record, so a later change on the source invoice line must not
        rewrite the settlements that have already been generated.
        """
        for line in self:
            invoice_line = line.invoice_agent_line_id.object_id
            line.product_id = invoice_line.product_id
            line.lot_id = invoice_line.lot_id
