# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import Form
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

    def test_equipment_requires_classification(self):
        with self.assertRaises(ValidationError):
            self.product.write({"product_kind": "equipment"})

    def test_accessory_requires_classification(self):
        with self.assertRaises(ValidationError):
            self.env["product.template"].create(
                {"name": "Test Accessory", "product_kind": "accessory"}
            )

    def test_rental_fee_requires_classification(self):
        # The classification is what the fee is charged against, so a rental fee
        # without one cannot be reported as a rental at all.
        with self.assertRaises(ValidationError):
            self.env["product.template"].create(
                {
                    "name": "Test Rental Fee",
                    "type": "service",
                    "product_kind": "rental_fee",
                }
            )

    def test_rental_fee_keeps_its_classification(self):
        rental_fee = self.env["product.template"].create(
            {
                "name": "Test Rental Fee",
                "type": "service",
                "product_kind": "rental_fee",
                "equipment_classification_id": self.classification.id,
            }
        )
        self.assertEqual(rental_fee.equipment_classification_id, self.classification)

    def test_classification_cleared_on_rental_fee(self):
        rental_fee = self.env["product.template"].create(
            {
                "name": "Test Rental Fee",
                "type": "service",
                "product_kind": "rental_fee",
                "equipment_classification_id": self.classification.id,
            }
        )
        with self.assertRaises(ValidationError):
            rental_fee.equipment_classification_id = False

    def test_consumable_does_not_require_classification(self):
        self.product.write({"product_kind": "consumable"})
        self.assertFalse(self.product.equipment_classification_id)

    def test_classification_cleared_on_equipment(self):
        self.product.write(
            {
                "product_kind": "equipment",
                "equipment_classification_id": self.classification.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.product.equipment_classification_id = False

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

    def test_minor_category_belongs_to_middle_category(self):
        categ = self.env["product.category"].create({"name": "Consumables"})
        middle = self.env["product.middle.category"].create(
            {"name": "Filters", "categ_id": categ.id}
        )
        minor = self.env["product.minor.category"].create(
            {"name": "Standard Filter", "middle_category_id": middle.id}
        )
        self.assertEqual(minor.middle_category_id, middle)
        self.assertEqual(minor.middle_category_id.categ_id, categ)

    def test_change_middle_category_clears_minor_category(self):
        middle_1 = self.env["product.middle.category"].create({"name": "Filters"})
        middle_2 = self.env["product.middle.category"].create({"name": "Tubes"})
        minor = self.env["product.minor.category"].create(
            {"name": "Standard Filter", "middle_category_id": middle_1.id}
        )
        with Form(self.product) as form:
            form.middle_category_id = middle_1
            form.minor_category_id = minor
            form.middle_category_id = middle_2
            self.assertFalse(form.minor_category_id)
            form.middle_category_id = middle_1
            form.minor_category_id = minor
        self.assertEqual(self.product.minor_category_id, minor)

    def test_change_categ_clears_middle_and_minor_category(self):
        categ_1 = self.env["product.category"].create({"name": "Consumables"})
        categ_1_child = self.env["product.category"].create(
            {"name": "Filters", "parent_id": categ_1.id}
        )
        categ_2 = self.env["product.category"].create({"name": "Equipment"})
        middle = self.env["product.middle.category"].create(
            {"name": "Filters", "categ_id": categ_1.id}
        )
        minor = self.env["product.minor.category"].create(
            {"name": "Standard Filter", "middle_category_id": middle.id}
        )
        with Form(self.product) as form:
            form.categ_id = categ_1
            form.middle_category_id = middle
            form.minor_category_id = minor
            # A child of the middle category's product category keeps it.
            form.categ_id = categ_1_child
            self.assertEqual(form.middle_category_id, middle)
            form.categ_id = categ_2
            self.assertFalse(form.middle_category_id)
            self.assertFalse(form.minor_category_id)
