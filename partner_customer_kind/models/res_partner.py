# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_kind = fields.Selection(
        selection=[
            ("hospital", "Hospital"),
            ("dealer", "Dealer"),
            ("individual", "Individual"),
            ("veterinary_hospital", "Veterinary Hospital"),
        ],
        help="Category of the customer: hospital, dealer, individual or "
        "veterinary hospital.",
    )
