# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestProductEquipmentClassification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.classification = cls.env["product.equipment.classification"].create(
            {"name": "Ventilator", "code": "100"}
        )
        cls.classification_sub = cls.env["product.equipment.classification.sub"].create(
            {"name": "Humidifier", "code": "200"}
        )
        cls.product = cls.env["product.template"].create({"name": "Test Device"})

    def test_assign_classifications(self):
        self.product.write(
            {
                "equipment_classification_id": self.classification.id,
                "equipment_classification_sub_id": self.classification_sub.id,
            }
        )
        self.assertEqual(self.product.equipment_classification_id, self.classification)
        self.assertEqual(
            self.product.equipment_classification_sub_id, self.classification_sub
        )

    @mute_logger("odoo.sql_db")
    def test_classification_code_unique(self):
        with self.assertRaises(IntegrityError):
            self.env["product.equipment.classification"].create(
                {"name": "Duplicate", "code": "100"}
            )

    @mute_logger("odoo.sql_db")
    def test_classification_sub_code_unique(self):
        with self.assertRaises(IntegrityError):
            self.env["product.equipment.classification.sub"].create(
                {"name": "Duplicate", "code": "200"}
            )
