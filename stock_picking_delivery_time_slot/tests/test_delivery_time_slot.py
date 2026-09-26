# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import psycopg2

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestDeliveryTimeSlot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Slot = cls.env["stock.delivery.time.slot"]
        cls.slot = cls.Slot.create({"code": "T1", "name": "Test Slot"})

    def test_code_is_unique(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(psycopg2.IntegrityError):
            with self.env.cr.savepoint():
                self.Slot.create({"code": "T1", "name": "Duplicate"})

    def test_search_by_code(self):
        self.assertEqual(self.Slot.name_search("T1"), [(self.slot.id, "Test Slot")])

    def test_assign_to_picking(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        picking.delivery_time_slot_id = self.slot
        self.assertEqual(picking.delivery_time_slot_id, self.slot)
