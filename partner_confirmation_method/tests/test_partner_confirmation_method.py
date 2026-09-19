# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import TransactionCase


class TestPartnerConfirmationMethod(TransactionCase):
    def test_defaults_to_fax_and_accepts_other_values(self):
        partner = self.env["res.partner"].create({"name": "Method Test"})
        self.assertEqual(partner.confirmation_method, "fax")
        partner.confirmation_method = "web"
        self.assertEqual(partner.confirmation_method, "web")
