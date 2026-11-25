# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestStockPutawayProductKind(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock = cls.warehouse.lot_stock_id
        Location = cls.env["stock.location"]
        cls.consumables = Location.create(
            {"name": "Consumables", "location_id": cls.stock.id}
        )
        cls.shelf = Location.create({"name": "Shelf", "location_id": cls.stock.id})
        cls.env["stock.putaway.rule"].create(
            {
                "location_in_id": cls.stock.id,
                "location_out_id": cls.consumables.id,
                "product_kind": "consumable",
                "sequence": 10,
            }
        )
        classification = cls.env["product.equipment.classification"].create(
            {"name": "Test Classification", "code": "T7420PA"}
        )
        Product = cls.env["product.product"]
        cls.consumable = Product.create(
            {"name": "Consumable", "is_storable": True, "product_kind": "consumable"}
        )
        cls.equipment = Product.create(
            {
                "name": "Equipment",
                "is_storable": True,
                "product_kind": "equipment",
                "equipment_classification_id": classification.id,
            }
        )
        cls.unclassified = Product.create({"name": "Unclassified", "is_storable": True})

    def test_rule_applies_to_its_kind_only(self):
        self.assertEqual(
            self.stock._get_putaway_strategy(self.consumable), self.consumables
        )
        for product in (self.equipment, self.unclassified):
            with self.subTest(product=product.name):
                self.assertEqual(self.stock._get_putaway_strategy(product), self.stock)

    def test_rule_without_kind_still_applies(self):
        self.env["stock.putaway.rule"].create(
            {
                "location_in_id": self.stock.id,
                "location_out_id": self.shelf.id,
                "sequence": 100,
            }
        )
        # Read the rules back in their stored order, by sequence.
        self.env.invalidate_all()
        self.assertEqual(
            self.stock._get_putaway_strategy(self.consumable), self.consumables
        )
        self.assertEqual(self.stock._get_putaway_strategy(self.equipment), self.shelf)

    def test_receipt(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.consumable.id,
                "product_uom_qty": 2.0,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.consumables)
