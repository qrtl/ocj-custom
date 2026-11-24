# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestLocationProductKindRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        Location = cls.env["stock.location"]
        cls.free_location = Location.create(
            {"name": "Free", "location_id": warehouse.view_location_id.id}
        )
        cls.branch_location = Location.create(
            {
                "name": "Branch",
                "location_id": warehouse.view_location_id.id,
                "product_kind_restriction": "consumable",
            }
        )
        cls.consumable_location = Location.create(
            {"name": "Consumables", "location_id": cls.branch_location.id}
        )
        cls.personal_location = Location.create(
            {
                "name": "Personal",
                "location_id": cls.branch_location.id,
                "product_kind_restriction": "equipment",
            }
        )
        classification = cls.env["product.equipment.classification"].create(
            {"name": "Test Classification", "code": "T7420"}
        )
        Product = cls.env["product.product"]
        cls.equipment = Product.create(
            {
                "name": "Equipment",
                "is_storable": True,
                "tracking": "serial",
                "product_kind": "equipment",
                "equipment_classification_id": classification.id,
            }
        )
        cls.serial_accessory = Product.create(
            {
                "name": "Serial Accessory",
                "is_storable": True,
                "tracking": "serial",
                "product_kind": "accessory",
                "equipment_classification_id": classification.id,
            }
        )
        cls.accessory = Product.create(
            {
                "name": "Accessory",
                "is_storable": True,
                "tracking": "none",
                "product_kind": "accessory",
                "equipment_classification_id": classification.id,
            }
        )
        cls.consumable = Product.create(
            {
                "name": "Consumable",
                "is_storable": True,
                "tracking": "none",
                "product_kind": "consumable",
            }
        )
        cls.unclassified = Product.create(
            {"name": "Unclassified", "is_storable": True, "tracking": "none"}
        )

    def _move(self, products, source, dest, qty=1.0):
        moves = self.env["stock.move"].create(
            [
                {
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "location_id": source.id,
                    "location_dest_id": dest.id,
                }
                for product in products
            ]
        )
        moves._action_confirm()
        moves._action_assign()
        if source == self.supplier_location:
            for move in moves.filtered(lambda m: m.product_id.tracking != "none"):
                move.move_line_ids.lot_id = self.env["stock.lot"].create(
                    {
                        "name": f"{move.product_id.name} {dest.name}",
                        "product_id": move.product_id.id,
                    }
                )
        moves.picked = True
        moves._action_done()
        return moves

    def test_incoming_moves(self):
        shelf = self.env["stock.location"].create(
            {"name": "Shelf", "location_id": self.personal_location.id}
        )
        equipment_kinds = self.equipment | self.serial_accessory | self.accessory
        cases = [
            (self.personal_location, equipment_kinds, self.consumable),
            (shelf, equipment_kinds, self.consumable),
            (self.branch_location, self.consumable, equipment_kinds),
            (self.consumable_location, self.consumable, equipment_kinds),
        ]
        for location, accepted, refused in cases:
            with self.subTest(location=location.name):
                moves = self._move(
                    accepted | self.unclassified, self.supplier_location, location
                )
                self.assertEqual(set(moves.mapped("state")), {"done"})
                for product in refused:
                    with self.assertRaisesRegex(UserError, "cannot be put in") as error:
                        self._move(product, self.supplier_location, location)
                    self.assertIn(product.display_name, str(error.exception))

    def test_existing_stock(self):
        incoming = self._move(
            self.consumable, self.supplier_location, self.free_location, qty=2.0
        )
        self.free_location.product_kind_restriction = "equipment"
        outgoing = self._move(
            self.consumable, self.free_location, self.supplier_location, qty=2.0
        )
        self.assertEqual(outgoing.state, "done")
        outgoing.move_line_ids.quantity = 1.0
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.consumable, self.free_location
            ),
            1.0,
        )
        with self.assertRaisesRegex(UserError, "cannot be put in"):
            incoming.move_line_ids.quantity = 3.0

    def test_inventory_adjustment(self):
        quant = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": self.consumable.id,
                    "location_id": self.personal_location.id,
                    "inventory_quantity": 5.0,
                }
            )
        )
        with self.assertRaisesRegex(UserError, "cannot be put in"):
            quant.action_apply_inventory()

    def test_done_transfer_changes(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.consumable_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.consumable.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.consumable_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_assign()
        picking.move_ids.picked = True
        picking._action_done()
        self.assertEqual(picking.state, "done")
        with self.assertRaisesRegex(UserError, "cannot be put in"):
            picking.move_line_ids.location_dest_id = self.personal_location
        with self.assertRaisesRegex(UserError, "cannot be put in"):
            self.env["stock.move"].create(
                {
                    "picking_id": picking.id,
                    "product_id": self.accessory.id,
                    "product_uom_qty": 1.0,
                    "quantity": 1.0,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.consumable_location.id,
                }
            )
