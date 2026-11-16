# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestLocationTrackingRestriction(TransactionCase):
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
        cls.tracked_location = Location.create(
            {
                "name": "Tracked Only",
                "location_id": warehouse.view_location_id.id,
                "product_tracking_restriction": "tracked",
            }
        )
        cls.quantity_location = Location.create(
            {
                "name": "Quantity Only",
                "location_id": warehouse.view_location_id.id,
                "product_tracking_restriction": "quantity",
            }
        )
        Product = cls.env["product.product"]
        cls.serial_product = Product.create(
            {"name": "Serial Product", "is_storable": True, "tracking": "serial"}
        )
        cls.lot_product = Product.create(
            {"name": "Lot Product", "is_storable": True, "tracking": "lot"}
        )
        cls.untracked_product = Product.create(
            {"name": "Untracked Product", "is_storable": True, "tracking": "none"}
        )

    def _move(self, products, source, dest):
        moves = self.env["stock.move"].create(
            [
                {
                    "product_id": product.id,
                    "product_uom_qty": 1.0,
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

    def test_tracked_location(self):
        moves = self._move(
            self.serial_product | self.lot_product,
            self.supplier_location,
            self.tracked_location,
        )
        self.assertEqual(set(moves.mapped("state")), {"done"})
        other_product = self.env["product.product"].create(
            {"name": "Other Product", "is_storable": True, "tracking": "none"}
        )
        products = self.untracked_product | other_product
        with self.assertRaisesRegex(UserError, "not tracked by serial or lot") as error:
            self._move(products, self.supplier_location, self.tracked_location)
        for product in products:
            self.assertIn(product.display_name, str(error.exception))

    def test_quantity_location(self):
        move = self._move(
            self.untracked_product, self.supplier_location, self.quantity_location
        )
        self.assertEqual(move.state, "done")
        for product in (self.serial_product, self.lot_product):
            with self.subTest(product=product.name):
                with self.assertRaisesRegex(UserError, "is tracked by serial or lot"):
                    self._move(product, self.supplier_location, self.quantity_location)

    def test_sublocation_follows_nearest_setting(self):
        Location = self.env["stock.location"]
        shared = Location.create(
            {"name": "Shared", "location_id": self.quantity_location.id}
        )
        personal = Location.create(
            {
                "name": "Personal",
                "location_id": self.quantity_location.id,
                "product_tracking_restriction": "tracked",
            }
        )
        shelf = Location.create({"name": "Shelf", "location_id": personal.id})
        self._move(self.untracked_product, self.supplier_location, shared)
        with self.assertRaises(UserError):
            self._move(self.serial_product, self.supplier_location, shared)
        for location in (personal, shelf):
            with self.subTest(location=location.name):
                self._move(self.serial_product, self.supplier_location, location)
                with self.assertRaises(UserError):
                    self._move(self.untracked_product, self.supplier_location, location)

    def test_existing_stock_can_move_out(self):
        self._move(self.untracked_product, self.supplier_location, self.free_location)
        self.free_location.product_tracking_restriction = "tracked"
        move = self._move(
            self.untracked_product, self.free_location, self.supplier_location
        )
        self.assertEqual(move.state, "done")

    def test_inventory_adjustment(self):
        quant = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": self.untracked_product.id,
                    "location_id": self.tracked_location.id,
                    "inventory_quantity": 5.0,
                }
            )
        )
        with self.assertRaises(UserError):
            quant.action_apply_inventory()

    def test_done_transfer_changes(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.quantity_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.untracked_product.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.quantity_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_assign()
        picking.move_ids.picked = True
        picking._action_done()
        self.assertEqual(picking.state, "done")
        with self.assertRaisesRegex(UserError, "not tracked by serial or lot"):
            picking.move_line_ids.location_dest_id = self.tracked_location
        with self.assertRaisesRegex(UserError, "is tracked by serial or lot"):
            self.env["stock.move"].create(
                {
                    "picking_id": picking.id,
                    "product_id": self.lot_product.id,
                    "product_uom_qty": 1.0,
                    "quantity": 1.0,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.quantity_location.id,
                }
            )
