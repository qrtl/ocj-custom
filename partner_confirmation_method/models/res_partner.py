# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    confirmation_method = fields.Selection(
        selection=[
            ("fax", "Fax"),
            ("web", "Web"),
            ("staff", "Staff"),
        ],
        default="fax",
        required=True,
        help="How the customer is contacted to confirm an order or a "
        "delivery: by fax, over the web or by a member of staff. Delivered "
        "to navi in flow as the confirmation method of the customer master.",
    )
