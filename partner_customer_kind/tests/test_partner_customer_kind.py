# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests.common import TransactionCase


class TestPartnerCustomerKind(TransactionCase):
    def test_customer_kind_is_optional_and_stored(self):
        partner = self.env["res.partner"].create({"name": "Kind Test"})
        self.assertFalse(partner.customer_kind)
        partner.customer_kind = "dealer"
        self.assertEqual(partner.customer_kind, "dealer")
