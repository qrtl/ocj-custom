# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    collection_method = fields.Selection(
        selection=[
            ("bank_transfer", "Bank Transfer"),
            ("direct_debit", "Direct Debit"),
            ("electronic_receivable", "Electronic Receivable"),
        ],
        help="How payment is collected from this customer.",
    )
    collection_company = fields.Selection(
        selection=[
            ("smbc", "SMBC"),
            ("mitsuuroko", "Mitsuuroko"),
            ("widenet", "Widenet"),
        ],
        help="Company that handles direct debit collection for this customer.",
    )
