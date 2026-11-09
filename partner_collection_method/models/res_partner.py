# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    collection_method = fields.Selection(
        selection=[
            ("bank_transfer", "Bank Transfer"),
            ("direct_debit", "Direct Debit"),
            ("electronic_receivable", "Electronic Receivable"),
            ("cash", "Cash"),
        ],
        help="How payment is collected from this customer.",
    )
    collection_company = fields.Selection(
        selection=[
            ("smbc", "SMBC"),
            ("mitsuuroko", "Mitsuuroko"),
            ("widenet", "Widenet"),
        ],
        compute="_compute_collection_company",
        store=True,
        readonly=False,
        help="Company that handles direct debit collection for this customer.",
    )

    @api.depends("collection_method")
    def _compute_collection_company(self):
        for partner in self:
            if partner.collection_method != "direct_debit":
                partner.collection_company = False
