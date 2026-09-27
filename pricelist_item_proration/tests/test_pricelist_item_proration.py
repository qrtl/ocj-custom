# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPricelistItemProration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "機器A"})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "医療機関別"})
        cls.item = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": cls.product.id,
                "compute_price": "fixed",
                "fixed_price": 1000.0,
            }
        )

    def test_proration_is_off_by_default(self):
        self.assertFalse(self.item.is_prorated)
        # The method still carries its agreed default, so turning proration on
        # does not require choosing it again.
        self.assertEqual(self.item.proration_method, "3")

    def test_prorated_price_needs_both_parameters(self):
        # Either one missing leaves the consumer unable to compute the amount,
        # and the gap would only show up as a wrong invoice.
        with self.assertRaises(ValidationError):
            self.item.is_prorated = True

    def test_prorated_price_with_both_parameters_is_accepted(self):
        self.item.write(
            {"is_prorated": True, "proration_method": "3", "proration_rounding": "1"}
        )
        self.assertTrue(self.item.is_prorated)

    def test_the_setting_is_per_customer_and_product(self):
        # Two items on the same pricelist, one prorated and one not: the same
        # customer is prorated on one product and not the other.
        other = self.env["product.product"].create({"name": "機器B"})
        second = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "0_product_variant",
                "product_id": other.id,
                "compute_price": "fixed",
                "fixed_price": 2000.0,
                "is_prorated": True,
                "proration_method": "3",
                "proration_rounding": "1",
            }
        )
        self.assertFalse(self.item.is_prorated)
        self.assertTrue(second.is_prorated)
