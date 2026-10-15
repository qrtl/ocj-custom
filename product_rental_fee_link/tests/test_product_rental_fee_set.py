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
        cls.rental_fee = cls._create_fee("Concentrator Set Rental Fee")

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
        )

    @classmethod
    def _create_fee(cls, name):
        return cls.Template.create(
            {
                "name": name,
                "type": "service",
                "product_kind": "rental_fee",
                "equipment_classification_id": cls.classification.id,
            }
        )

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
        # combinations.
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
        bare_fee = self._create_fee("Other Fee")
        self.assertFalse(self.Template._find_by_rental_set([]))
        self.assertFalse(bare_fee.rental_set_key)
        self.assertFalse(self.Template._find_by_rental_set([self.flow_meter.id]))

    def test_find_by_rental_set_skips_archived(self):
        self._set_components(self.rental_fee, self.concentrator)
        self.rental_fee.active = False
        self.assertFalse(self.Template._find_by_rental_set([self.concentrator.id]))

    def test_sets_are_visible_from_the_component(self):
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        self.assertEqual(self.concentrator.rental_set_fee_tmpl_ids, self.rental_fee)
        self.assertFalse(self.flow_meter.rental_set_fee_tmpl_ids)
        missing = self.Template.search(
            [
                ("rental_set_fee_tmpl_ids", "=", False),
                ("product_kind", "in", ("equipment", "accessory")),
            ]
        )
        self.assertIn(self.flow_meter, missing)
        self.assertNotIn(self.concentrator, missing)

    def test_consumable_cannot_be_a_component(self):
        consumable = self.Template.create(
            {"name": "Cannula", "type": "consu", "product_kind": "consumable"}
        )
        with self.assertRaises(ValidationError):
            self._set_components(self.rental_fee, consumable)

    def test_only_a_rental_fee_can_bill_a_set(self):
        service = self.Template.create({"name": "Delivery", "type": "service"})
        with self.assertRaises(ValidationError):
            self._set_components(service, self.concentrator)
        with self.assertRaises(ValidationError):
            self._set_components(self.concentrator, self.demand_valve)
        self._set_components(self.rental_fee, self.concentrator)
        with self.assertRaises(ValidationError):
            self.rental_fee.product_kind = False

    def test_archived_member_stays_in_the_set(self):
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        self.concentrator.active = False
        self.assertFalse(self.Template._find_by_rental_set(self.demand_valve.ids))
        self.assertFalse(self.Template._find_rental_sets_within(self.demand_valve.ids))

    def test_deleted_member_leaves_the_set(self):
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        self.demand_valve.unlink()
        self.assertEqual(
            self.Template._find_by_rental_set(self.concentrator.ids), self.rental_fee
        )

    def test_set_is_checked_from_the_member_side(self):
        self._set_components(self.rental_fee, self.demand_valve)
        with self.assertRaises(ValidationError):
            self.demand_valve.product_kind = "consumable"
        service = self.Template.create({"name": "Delivery", "type": "service"})
        with self.assertRaises(ValidationError):
            self.concentrator.rental_set_fee_tmpl_ids = [Command.link(service.id)]

    def test_find_rental_sets_within(self):
        single = self._create_fee("Concentrator Rental Fee")
        self._set_components(single, self.concentrator)
        self._set_components(self.rental_fee, self.concentrator | self.demand_valve)
        humidifier = self._create_goods("Humidifier", "accessory")
        within = self.Template._find_rental_sets_within(
            (self.concentrator | self.demand_valve | humidifier).ids
        )
        self.assertEqual(within, single | self.rental_fee)
        # A set reaching beyond the combination is not part of it.
        self.assertEqual(
            self.Template._find_rental_sets_within(self.concentrator.ids), single
        )
        self.assertFalse(self.Template._find_rental_sets_within([]))

    def test_a_combination_can_be_billed_by_several_products(self):
        components = self.concentrator | self.flow_meter
        self._set_components(self.rental_fee, components)
        other_fee = self._create_fee("Concentrator Set Rental Fee (2)")
        self._set_components(other_fee, components)
        self.assertEqual(
            self.Template._find_by_rental_set(components.ids),
            self.rental_fee | other_fee,
        )
        self.assertEqual(
            self.concentrator.rental_set_fee_tmpl_ids, self.rental_fee | other_fee
        )

    def test_archived_set_does_not_block_its_replacement(self):
        components = self.concentrator | self.flow_meter
        self._set_components(self.rental_fee, components)
        self.rental_fee.active = False
        replacement = self._create_fee("Concentrator Set Rental Fee (new)")
        self._set_components(replacement, components)
        self.assertEqual(self.Template._find_by_rental_set(components.ids), replacement)
