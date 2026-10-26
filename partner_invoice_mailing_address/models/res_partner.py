# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_mailing_address = fields.Text(
        help="Address printed on customer invoices and summary invoices in place of "
        "the customer's own address. The customer's name and phone are printed as "
        "usual.",
    )
