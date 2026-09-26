# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductRentalFeeSet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Template = cls.env["product.template"]
        cls.classification = cls.env["product.equipment.classification"].create(
            {"name": "Oxygen Concentrator", "code": "100"}
        )
        cls.concentrator = cls._create_goods("Concentrator", "equipment")
        cls.demand_valve = cls._create_goods("Demand Valve", "accessory")
        cls.flow_meter = cls._create_goods("Flow Meter", "accessory")
        cls.rental_fee = cls.Template.create(
            {"name": "Concentrator Set Rental Fee", "type": "service"}
        )

    @classmethod
    def _create_goods(cls, name, kind):
        return cls.Template.create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
                "product_kind": kind,
                "equipment_classification_id": cls.classification.id,
            }
        ).product_variant_id

    def _set_components(self, template, components):
        template.rental_set_component_ids = [Command.set(components.ids)]

    def test_key_is_order_independent(self):
        components = self.concentrator | self.demand_valve | self.flow_meter
        expected = ",".join(str(i) for i in sorted(components.ids))
        self._set_components(self.rental_fee, components)
        self.assertEqual(self.rental_fee.rental_set_key, expected)
        self.assertEqual(
            self.Template._rental_set_key(list(reversed(components.ids))), expected
        )
        # A repeated component says nothing a set does not already say.
        self.assertEqual(
            self.Template._rental_set_key(components.ids + [self.flow_meter.id]),
            expected,
        )

    def test_key_follows_the_components(self):
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        self._set_components(self.rental_fee, self.concentrator)
        self.assertEqual(self.rental_fee.rental_set_key, str(self.concentrator.id))
        self.rental_fee.rental_set_component_ids = [Command.clear()]
        self.assertFalse(self.rental_fee.rental_set_key)

    def test_find_by_rental_set_matches_exactly(self):
        components = self.concentrator | self.demand_valve | self.flow_meter
        self._set_components(self.rental_fee, components)
        self.assertEqual(
            self.Template._find_by_rental_set(list(reversed(components.ids))),
            self.rental_fee,
        )
        # A part of the set, and the set plus something else, are different
        # combinations - what to charge for those is not this product's answer.
        self.assertFalse(
            self.Template._find_by_rental_set(
                [self.concentrator.id, self.flow_meter.id]
            )
        )
        other = self._create_goods("Humidifier", "accessory")
        self.assertFalse(self.Template._find_by_rental_set(components.ids + [other.id]))

    def test_find_by_rental_set_ignores_empty_and_unknown(self):
        self._set_components(self.rental_fee, self.concentrator)
        # An empty combination must not match the products that have no
        # components - a fee billed on its own carries no set at all.
        bare_fee = self.Template.create({"name": "Other Fee", "type": "service"})
        self.assertFalse(self.Template._find_by_rental_set([]))
        self.assertFalse(bare_fee.rental_set_key)
        self.assertFalse(self.Template._find_by_rental_set([self.flow_meter.id]))

    def test_find_by_rental_set_skips_archived(self):
        self._set_components(self.rental_fee, self.concentrator)
        self.rental_fee.active = False
        self.assertFalse(self.Template._find_by_rental_set([self.concentrator.id]))

    def test_match_is_one_product_whatever_its_variants(self):
        # The set is the product's, the price classes are its variants: a
        # combination names one rental fee product, which then answers with
        # every variant it has.
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
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        matched = self.Template._find_by_rental_set(
            [self.demand_valve.id, self.concentrator.id]
        )
        self.assertEqual(matched, self.rental_fee)
        self.assertEqual(len(matched.product_variant_ids), 2)

    def test_sets_are_visible_from_the_component(self):
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        self.assertEqual(self.concentrator.rental_set_fee_tmpl_ids, self.rental_fee)
        self.assertEqual(
            self.concentrator.product_tmpl_id.rental_set_fee_tmpl_ids, self.rental_fee
        )
        self.assertFalse(self.flow_meter.rental_set_fee_tmpl_ids)

    def test_storable_service_can_bill_a_set(self):
        # "Track Inventory" can be switched on for a service by a user default,
        # so it must not disqualify a service from billing a set.
        self.rental_fee.is_storable = True
        self._set_components(self.rental_fee, self.concentrator)
        self.assertEqual(self.rental_fee.rental_set_component_ids, self.concentrator)

    def test_goods_cannot_bill_a_set(self):
        with self.assertRaises(ValidationError):
            self._set_components(self.concentrator.product_tmpl_id, self.demand_valve)

    def test_consumable_cannot_be_a_component(self):
        consumable = self.Template.create(
            {"name": "Cannula", "type": "consu", "product_kind": "consumable"}
        ).product_variant_id
        with self.assertRaises(ValidationError):
            self._set_components(self.rental_fee, consumable)

    def test_self_reference_not_allowed(self):
        # A service has no product kind that qualifies, so this is only
        # reachable on data that contradicts itself - which is when a set
        # naming its own product would otherwise be created.
        self.rental_fee.write(
            {
                "product_kind": "equipment",
                "equipment_classification_id": self.classification.id,
            }
        )
        with self.assertRaises(ValidationError):
            self._set_components(self.rental_fee, self.rental_fee.product_variant_id)

    def test_a_combination_names_one_product(self):
        components = self.concentrator | self.flow_meter
        self._set_components(self.rental_fee, components)
        other_fee = self.Template.create(
            {"name": "Concentrator Set Rental Fee (2)", "type": "service"}
        )
        with self.assertRaises(ValidationError):
            self._set_components(other_fee, components)

    def test_archived_set_does_not_block_its_replacement(self):
        components = self.concentrator | self.flow_meter
        self._set_components(self.rental_fee, components)
        self.rental_fee.active = False
        replacement = self.Template.create(
            {"name": "Concentrator Set Rental Fee (new)", "type": "service"}
        )
        self._set_components(replacement, components)
        self.assertEqual(self.Template._find_by_rental_set(components.ids), replacement)
