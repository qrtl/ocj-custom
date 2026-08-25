# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
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

    def test_link_equipment(self):
        self.rental_fee.equipment_tmpl_ids = self.equipment
        self.assertEqual(self.rental_fee.equipment_tmpl_ids, self.equipment)
        self.assertEqual(self.equipment.rental_fee_product_tmpl_ids, self.rental_fee)

    def test_goods_not_allowed_as_rental_fee(self):
        with self.assertRaises(ValidationError):
            self.equipment.rental_fee_product_tmpl_ids = self.equipment.copy()

    def test_consumable_not_allowed_as_equipment(self):
        consumable = self.equipment.copy(
            {
                "name": "Consumable",
                "product_kind": "consumable",
                "equipment_classification_id": False,
            }
        )
        with self.assertRaises(ValidationError):
            self.rental_fee.equipment_tmpl_ids = consumable

    def test_self_reference_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.rental_fee.equipment_tmpl_ids = self.rental_fee

    def test_storable_service_is_allowed(self):
        # "Track Inventory" can be switched on for a service by a user default,
        # so it must not disqualify a service from billing a rental.
        self.rental_fee.is_storable = True
        self.rental_fee.equipment_tmpl_ids = self.equipment
        self.assertEqual(self.rental_fee.equipment_tmpl_ids, self.equipment)

    def test_equipment_can_have_several_rental_fee_products(self):
        # A base fee and a fee for a specific accessory bundle are separate
        # service products, both billing the same equipment.
        other_rental_fee = self.env["product.template"].create(
            {"name": "Oxygen Concentrator Rental Fee (Bundle)", "type": "service"}
        )
        self.rental_fee.equipment_tmpl_ids = self.equipment
        other_rental_fee.equipment_tmpl_ids = self.equipment
        self.assertEqual(
            self.equipment.rental_fee_product_tmpl_ids,
            self.rental_fee | other_rental_fee,
        )

    def test_rental_fee_product_can_be_shared(self):
        other_equipment = self.equipment.copy({"name": "Oxygen Concentrator 2"})
        self.rental_fee.equipment_tmpl_ids = [
            Command.set([self.equipment.id, other_equipment.id])
        ]
        self.assertEqual(
            self.rental_fee.equipment_tmpl_ids, self.equipment | other_equipment
        )

    def test_variants_of_linked_product_are_billable_items(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Price Category",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "First Unit"}),
                    Command.create({"name": "Second Unit"}),
                ],
            }
        )
        self.rental_fee.attribute_line_ids = [
            Command.create(
                {
                    "attribute_id": attribute.id,
                    "value_ids": [Command.set(attribute.value_ids.ids)],
                }
            )
        ]
        self.rental_fee.equipment_tmpl_ids = self.equipment
        self.assertEqual(len(self.rental_fee.product_variant_ids), 2)
