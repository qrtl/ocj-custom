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

    def test_link_service_product(self):
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(self.equipment.rental_fee_product_tmpl_id, self.rental_fee)

    def test_goods_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.equipment.rental_fee_product_tmpl_id = self.equipment.copy()

    def test_self_reference_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.equipment.rental_fee_product_tmpl_id = self.equipment

    def test_storable_service_is_allowed(self):
        # "Track Inventory" can be switched on for a service by a user default,
        # so it must not disqualify a service from being a rental fee product.
        self.rental_fee.is_storable = True
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(self.equipment.rental_fee_product_tmpl_id, self.rental_fee)

    def test_shared_between_equipments(self):
        other_equipment = self.equipment.copy({"name": "Oxygen Concentrator 2"})
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        other_equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            other_equipment.rental_fee_product_tmpl_id,
            self.equipment.rental_fee_product_tmpl_id,
        )

    def test_the_fee_product_knows_the_equipment_it_bills(self):
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            self.rental_fee.rental_fee_for_product_tmpl_ids, self.equipment
        )

    def test_classification_is_derived_from_the_equipment(self):
        # The fee product carries no classification of its own; the value comes
        # from the equipment so it does not have to be kept in step by hand.
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            self.rental_fee.rented_equipment_classification_id, self.classification
        )

    def test_equipment_agreeing_on_a_classification_still_derives_one(self):
        other_equipment = self.equipment.copy({"name": "Oxygen Concentrator 2"})
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        other_equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            self.rental_fee.rented_equipment_classification_id, self.classification
        )

    def test_equipment_disagreeing_on_a_classification_derives_nothing(self):
        # Sharing a fee product is allowed, so two classifications can meet on
        # one fee product. Reporting either would be a guess.
        other_classification = self.env["product.equipment.classification"].create(
            {"name": "Ventilator", "code": "200"}
        )
        other_equipment = self.equipment.copy({"name": "Ventilator 1"})
        other_equipment.equipment_classification_id = other_classification
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        other_equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertFalse(self.rental_fee.rented_equipment_classification_id)

    def test_the_derived_classification_follows_the_equipment(self):
        new_classification = self.env["product.equipment.classification"].create(
            {"name": "Nebulizer", "code": "300"}
        )
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.equipment.equipment_classification_id = new_classification
        self.assertEqual(
            self.rental_fee.rented_equipment_classification_id, new_classification
        )

    def test_unlinking_the_equipment_clears_the_derived_classification(self):
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.equipment.rental_fee_product_tmpl_id = False
        self.assertFalse(self.rental_fee.rented_equipment_classification_id)

    def test_the_derived_classification_is_searchable(self):
        # Stored, because an integration selects fee products with it.
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        found = self.env["product.template"].search(
            [("rented_equipment_classification_id", "=", self.classification.id)]
        )
        self.assertIn(self.rental_fee, found)

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
        self.equipment.rental_fee_product_tmpl_id = self.rental_fee
        self.assertEqual(
            len(self.equipment.rental_fee_product_tmpl_id.product_variant_ids), 2
        )
