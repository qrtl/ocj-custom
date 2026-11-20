# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import psycopg2

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestQualityStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True, "tracking": "serial"}
        )
        cls.status = cls.env["stock.lot.quality.status"].create(
            {"name": "Test Status", "code": "test"}
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "LOT-0001",
                "product_id": cls.product.id,
                "quality_status_id": False,
            }
        )

    def test_assign_quality_status(self):
        self.lot.quality_status_id = self.status
        self.assertEqual(self.lot.quality_status_id, self.status)

    def test_quant_related_field_reflects_lot(self):
        quant = self.env["stock.quant"].create(
            {
                "lot_id": self.lot.id,
                "product_id": self.product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.assertFalse(quant.quality_status_id)
        # The stored related field must refresh when the lot's status changes
        # after the quant already exists.
        self.lot.quality_status_id = self.status
        self.assertEqual(quant.quality_status_id, self.status)

    def test_new_lot_defaults_to_default_status(self):
        # A freshly created lot picks up the status flagged as is_default.
        default_status = self.env["stock.lot.quality.status"].create(
            {"name": "Default Status", "is_default": True}
        )
        lot = self.env["stock.lot"].create(
            {"name": "LOT-0002", "product_id": self.product.id}
        )
        self.assertEqual(lot.quality_status_id, default_status)

    def test_only_one_default_allowed(self):
        # With a default already set, flagging a second status raises.
        self.env["stock.lot.quality.status"].create(
            {"name": "First Default", "is_default": True}
        )
        with self.assertRaises(ValidationError):
            self.env["stock.lot.quality.status"].create(
                {"name": "Another Default", "is_default": True}
            )

    @mute_logger("odoo.sql_db")
    def test_status_in_use_cannot_be_deleted(self):
        self.lot.quality_status_id = self.status
        # ondelete="restrict" enforces at the database level, so removing a
        # status still referenced by a lot raises an integrity error.
        with self.assertRaises(psycopg2.IntegrityError), self.cr.savepoint():
            self.status.unlink()
