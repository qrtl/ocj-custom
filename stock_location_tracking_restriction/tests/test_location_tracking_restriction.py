# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

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

    def _move(self, product, source, dest, qty=1.0):
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": qty,
                "location_id": source.id,
                "location_dest_id": dest.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        if product.tracking != "none" and source == self.supplier_location:
            move.move_line_ids.lot_id = self.env["stock.lot"].create(
                {"name": f"{product.name} {dest.name}", "product_id": product.id}
            )
        move.picked = True
        move._action_done()
        return move

    def test_tracked_location_accepts_tracked_products(self):
        for product in (self.serial_product, self.lot_product):
            with self.subTest(product=product.name):
                move = self._move(
                    product, self.supplier_location, self.tracked_location
                )
                self.assertEqual(move.state, "done")

    def test_tracked_location_refuses_untracked_product(self):
        with self.assertRaisesRegex(UserError, "not tracked by serial or lot"):
            self._move(
                self.untracked_product, self.supplier_location, self.tracked_location
            )

    def test_quantity_location_accepts_untracked_product(self):
        move = self._move(
            self.untracked_product, self.supplier_location, self.quantity_location
        )
        self.assertEqual(move.state, "done")

    def test_quantity_location_refuses_tracked_products(self):
        for product in (self.serial_product, self.lot_product):
            with self.subTest(product=product.name):
                with self.assertRaisesRegex(UserError, "is tracked by serial or lot"):
                    self._move(product, self.supplier_location, self.quantity_location)

    def test_unrestricted_location(self):
        move = self._move(
            self.untracked_product, self.supplier_location, self.free_location
        )
        self.assertEqual(move.state, "done")

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
        # With no setting of its own, a sublocation follows its parent.
        self._move(self.untracked_product, self.supplier_location, shared)
        with self.assertRaises(UserError):
            self._move(self.serial_product, self.supplier_location, shared)
        # A sublocation with its own setting follows that one, and so do the
        # locations under it.
        for location in (personal, shelf):
            with self.subTest(location=location.name):
                self._move(self.serial_product, self.supplier_location, location)
                with self.assertRaises(UserError):
                    self._move(self.untracked_product, self.supplier_location, location)

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

    def test_existing_stock_can_move_out(self):
        self._move(self.untracked_product, self.supplier_location, self.free_location)
        self.free_location.product_tracking_restriction = "tracked"
        move = self._move(
            self.untracked_product, self.free_location, self.supplier_location
        )
        self.assertEqual(move.state, "done")

    def test_edit_done_line_destination(self):
        move = self._move(
            self.untracked_product, self.supplier_location, self.free_location
        )
        with self.assertRaises(UserError):
            move.move_line_ids.location_dest_id = self.tracked_location

    def test_error_lists_every_product(self):
        other_product = self.env["product.product"].create(
            {"name": "Other Product", "is_storable": True, "tracking": "none"}
        )
        moves = self.env["stock.move"].create(
            [
                {
                    "product_id": product.id,
                    "product_uom_qty": 1.0,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.tracked_location.id,
                }
                for product in (self.untracked_product, other_product)
            ]
        )
        moves._action_confirm()
        moves._action_assign()
        moves.picked = True
        with self.assertRaises(UserError) as error:
            moves._action_done()
        for product in moves.product_id:
            self.assertIn(product.display_name, str(error.exception))
