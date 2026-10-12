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
        help="Vendor contract condition for rented equipment: under full "
        "billing the vendor is paid for every month the device is installed, "
        "regardless of the patient's visits; under partial billing only "
        "months with a billable visit are paid.",
    )
    prorated_billing = fields.Boolean(
        help="Whether amounts are prorated by usage days on mid-period "
        "start/cancellation.",
    )

    @api.model
    def _commercial_fields(self):
        # A billing policy is the company's, so a contact or invoice address
        # under it carries the same values rather than blank ones of its own.
        return super()._commercial_fields() + ["billing_scope", "prorated_billing"]
