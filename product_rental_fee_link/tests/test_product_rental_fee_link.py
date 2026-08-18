# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductRentalFeeLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Template = cls.env["product.template"]
        cls.classification = cls.env["product.equipment.classification"].create(
            {"name": "Oxygen Concentrator", "code": "100"}
        )
        cls.equipment = Template.create(
            {
                "name": "Oxygen Concentrator",
                "type": "consu",
                "is_storable": True,
                "product_kind": "equipment",
                "equipment_classification_id": cls.classification.id,
            }
        )
        cls.rental_fee = Template.create(
            {"name": "Oxygen Concentrator Rental Fee", "type": "service"}
        )

    def test_01_link_service_product(self):
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(self.equipment.rental_fee_product_tmpl_id, self.rental_fee)

    def test_02_goods_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.equipment.rental_fee_product_tmpl_id = self.equipment.copy()

    def test_03_self_reference_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.equipment.rental_fee_product_tmpl_id = self.equipment

    def test_04_storable_service_is_allowed(self):
        # "Track Inventory" can be switched on for a service by a user default,
        # so it must not disqualify a service from being a rental fee product.
        self.rental_fee.is_storable = True
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(self.equipment.rental_fee_product_tmpl_id, self.rental_fee)

    def test_05_shared_between_equipments(self):
        other_equipment = self.equipment.copy({"name": "Oxygen Concentrator 2"})
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        other_equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            other_equipment.rental_fee_product_tmpl_id,
            self.equipment.rental_fee_product_tmpl_id,
        )

    def test_06_variants_of_linked_product_are_billable_items(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Price Category",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "First Unit"}),
                    (0, 0, {"name": "Second Unit"}),
                ],
            }
        )
        self.rental_fee.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, attribute.value_ids.ids)],
                },
            )
        ]
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            len(self.equipment.rental_fee_product_tmpl_id.product_variant_ids), 2
        )
