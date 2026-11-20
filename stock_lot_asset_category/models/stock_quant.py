# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    asset_category_id = fields.Many2one(
        related="lot_id.asset_category_id",
        store=True,
    )
