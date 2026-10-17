# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CommissionSettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    lot_id = fields.Many2one(
        comodel_name="stock.lot", string="Lot/Serial Number", readonly=True
    )
