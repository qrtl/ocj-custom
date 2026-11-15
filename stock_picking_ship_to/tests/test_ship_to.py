# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestShipTo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.partner"].create(
            {
                "name": "Clinic",
                "is_company": True,
                "state_id": cls.env.ref("base.state_jp_jp-13").id,
                "city": "港区",
                "street": "高輪2-19-17",
            }
        )
        cls.contact = cls.env["res.partner"].create(
            {"name": "Ward 3", "parent_id": cls.company.id, "phone": "03-0000-0000"}
        )

    def _picking(self, **vals):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                **vals,
            }
        )

    def test_defaults_from_contact(self):
        # A contact's name keeps its company in front, as a carrier needs it.
        picking = self._picking(partner_id=self.contact.id)
        self.assertEqual(picking.ship_to_name, "Clinic, Ward 3")
        self.assertEqual(picking.ship_to_address, "東京都港区高輪2-19-17")
        self.assertEqual(picking.ship_to_phone, "03-0000-0000")

    def test_values_given_on_create_are_kept(self):
        # An integration sets the partner and the destination in one create.
        picking = self._picking(
            partner_id=self.company.id,
            ship_to_name="Patient",
            ship_to_address="東京都千代田区千代田1-1",
            ship_to_phone=False,
        )
        self.assertEqual(picking.ship_to_name, "Patient")
        self.assertEqual(picking.ship_to_address, "東京都千代田区千代田1-1")
        self.assertFalse(picking.ship_to_phone)
