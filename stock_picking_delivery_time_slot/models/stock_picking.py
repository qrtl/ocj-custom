# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_time_slot_id = fields.Many2one(
        "stock.delivery.time.slot",
        string="Delivery Time Slot",
        index="btree_not_null",
        help="Time slot the recipient requested for the delivery.",
    )
