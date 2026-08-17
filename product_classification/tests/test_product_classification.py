# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestProductClassification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.classification = cls.env["product.equipment.classification"].create(
            {"name": "Ventilator", "code": "100"}
        )
        cls.manufacturer = cls.env["product.manufacturer"].create(
            {"name": "Acme Medical", "code": "300"}
        )
        cls.product = cls.env["product.template"].create({"name": "Test Device"})

    def test_assign_equipment_classifications(self):
        self.product.write(
            {
                "product_kind": "equipment",
                "manufacturer_id": self.manufacturer.id,
                "equipment_classification_id": self.classification.id,
            }
        )
        self.assertEqual(self.product.product_kind, "equipment")
        self.assertEqual(self.product.manufacturer_id, self.manufacturer)
        self.assertEqual(self.product.equipment_classification_id, self.classification)

    def test_assign_accessory_classification(self):
        self.product.write(
            {
                "product_kind": "accessory",
                "equipment_classification_id": self.classification.id,
            }
        )
        self.assertEqual(self.product.product_kind, "accessory")
        self.assertEqual(self.product.equipment_classification_id, self.classification)

    @mute_logger("odoo.sql_db")
    def test_classification_code_unique(self):
        with self.assertRaises(IntegrityError):
            self.env["product.equipment.classification"].create(
                {"name": "Duplicate", "code": "100"}
            )

    @mute_logger("odoo.sql_db")
    def test_manufacturer_code_unique(self):
        with self.assertRaises(IntegrityError):
            self.env["product.manufacturer"].create(
                {"name": "Duplicate", "code": "300"}
            )
