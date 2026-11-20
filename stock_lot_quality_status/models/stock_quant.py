# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    quality_status_id = fields.Many2one(
        related="lot_id.quality_status_id",
        store=True,
    )
