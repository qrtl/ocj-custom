# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    billing_scope = fields.Selection(
        selection=[
            ("full", "Full Billing"),
            ("partial", "Partial Billing"),
        ],
        help="Whether the whole engagement or only part of it is billed.",
    )
    prorated_billing = fields.Boolean(
        help="Whether amounts are prorated by usage days on mid-period "
        "start/cancellation.",
    )
    revenue_timing = fields.Selection(
        selection=[
            ("invoice_date", "Invoice Date"),
            ("delivery_date", "Delivery Date"),
            ("acceptance_date", "Acceptance Date"),
            ("period_end", "Period End"),
        ],
        string="Revenue Recognition Timing",
        help="Point in time at which revenue is recognized.",
    )
    bill_on_loss = fields.Boolean(
        help="Whether lost goods may be billed to the customer.",
    )

    @api.model
    def _commercial_fields(self):
        # A billing policy is the company's, so a contact or invoice address
        # under it carries the same values rather than blank ones of its own.
        return super()._commercial_fields() + [
            "billing_scope",
            "prorated_billing",
            "revenue_timing",
            "bill_on_loss",
        ]
