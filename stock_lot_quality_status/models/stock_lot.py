# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _default_quality_status_id(self):
        return self.env["stock.lot.quality.status"].search(
            [("is_default", "=", True)], limit=1
        )

    quality_status_id = fields.Many2one(
        comodel_name="stock.lot.quality.status",
        string="Quality Status",
        ondelete="restrict",
        tracking=True,
        default=lambda self: self._default_quality_status_id(),
        help="Quality status of this serial/lot number.",
    )
