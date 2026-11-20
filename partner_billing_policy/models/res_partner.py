# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

# Booleans defaulting to True: "off" is a decision, not an unset value.
PRORATION_FIELDS = [
    "prorated_billing",
    "prorate_installation_month",
    "prorate_collection_month",
]


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
    # On by default: proration is the rule and the customers billed in full
    # are the exceptions OCJ lists.
    prorated_billing = fields.Boolean(
        default=True,
        help="Whether a rental is charged pro rata for a partial month. The "
        "two settings below choose which partial months.",
    )
    # Separate because a contract can prorate one end and not the other, e.g.
    # the installation month in full and the collection month pro rata.
    prorate_installation_month = fields.Boolean(
        default=True,
        help="Charge the installation month from the installation day to the "
        "month end, rather than in full.",
    )
    prorate_collection_month = fields.Boolean(
        default=True,
        help="Charge the collection month from the first of the month to the "
        "day before collection, rather than in full.",
    )

    @api.model
    def _commercial_fields(self):
        # A billing policy is the company's, so a contact or invoice address
        # under it carries the same values rather than blank ones of its own.
        return super()._commercial_fields() + ["billing_scope"] + PRORATION_FIELDS

    def _get_commercial_values(self):
        # Core copies only truthy values to a new child, so a company billed
        # in full would hand a new invoice address the default (prorated).
        return dict(
            super()._get_commercial_values(),
            **self._convert_fields_to_values(PRORATION_FIELDS),
        )
