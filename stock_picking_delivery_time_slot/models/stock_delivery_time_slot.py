# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockDeliveryTimeSlot(models.Model):
    _name = "stock.delivery.time.slot"
    _description = "Delivery Time Slot"
    _order = "sequence, id"
    _rec_names_search = ["name", "code"]

    code = fields.Char(
        required=True,
        help="Key exchanged with external systems. Matches the carrier's time slot "
        "code where the carrier defines one.",
    )
    name = fields.Char(
        required=True,
        help="Label passed to the warehouse as is, and printed on the waybill.",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint("unique(code)", "The code must be unique.")
