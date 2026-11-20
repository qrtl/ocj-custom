# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    lot_product_id = fields.Many2one(
        related="move_line_id.lot_product_id", store=True, index="btree_not_null"
    )
    lot_id = fields.Many2one(
        related="move_line_id.lot_id", store=True, index="btree_not_null"
    )
