# Copyright 2026 Quartile (https://www.quartile.co.jp)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    installation_status = fields.Selection(
        related="lot_id.installation_status",
        store=True,
    )
    installation_status_change_date = fields.Datetime(
        related="lot_id.installation_status_change_date",
        store=True,
    )
    installation_completed_date = fields.Datetime(
        related="lot_id.installation_completed_date",
        store=True,
    )
