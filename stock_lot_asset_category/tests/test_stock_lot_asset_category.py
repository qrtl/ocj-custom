# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestStockLotAssetCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.own, cls.other = cls.env["stock.lot.asset.category"].create(
            [{"name": "Own Asset", "code": "own"}, {"name": "Other", "code": "other"}]
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "tracking": "serial",
                "lot_asset_category_id": cls.own.id,
            }
        )

    def _create_lot(self, name, **vals):
        return self.env["stock.lot"].create(
            {"name": name, "product_id": self.product.id, **vals}
        )

    def test_lot_takes_product_default(self):
        """A lot gets its product's default unless it is given its own."""
        self.assertEqual(self._create_lot("SN-0001").asset_category_id, self.own)
        lot = self._create_lot("SN-0002", asset_category_id=self.other.id)
        self.assertEqual(lot.asset_category_id, self.other)

    def test_product_default_change_keeps_existing_lots(self):
        """A new product default applies to new lots only."""
        lot = self._create_lot("SN-0001")
        self.assertEqual(lot.asset_category_id, self.own)
        self.product.lot_asset_category_id = self.other
        self.env.invalidate_all()
        self.assertEqual(lot.asset_category_id, self.own)
        self.assertEqual(self._create_lot("SN-0002").asset_category_id, self.other)

    def test_quant_follows_lot(self):
        """The quant's stored category follows a change on its lot."""
        lot = self._create_lot("SN-0001")
        quant = self.env["stock.quant"].create(
            {
                "lot_id": lot.id,
                "product_id": self.product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.assertEqual(quant.asset_category_id, self.own)
        lot.asset_category_id = self.other
        self.assertEqual(quant.asset_category_id, self.other)

    def test_only_assigners_set_the_category(self):
        """Without the group, neither a lot nor a product default can be set."""
        user = new_test_user(
            self.env,
            login="stock_manager",
            groups="stock.group_stock_manager,product.group_product_manager",
        )
        lot = self._create_lot("SN-0001").with_user(user)
        product = self.product.with_user(user)
        with self.assertRaises(AccessError):
            lot.asset_category_id = self.other
        with self.assertRaises(AccessError):
            lot.create(
                {
                    "name": "SN-0002",
                    "product_id": product.id,
                    "asset_category_id": self.other.id,
                }
            )
        with self.assertRaises(AccessError):
            product.lot_asset_category_id = self.other
        with self.assertRaises(AccessError):
            product.product_tmpl_id.copy({"lot_asset_category_id": self.other.id})
        created = lot.create({"name": "SN-0003", "product_id": product.id})
        self.assertEqual(created.asset_category_id, self.own)
        self.assertEqual(lot.copy({"name": "SN-0004"}).asset_category_id, self.own)
        product.product_tmpl_id.copy()
        user.group_ids = [
            Command.link(
                self.env.ref("stock_lot_asset_category.group_assign_asset_category").id
            )
        ]
        lot.asset_category_id = self.other
        product.lot_asset_category_id = self.other
        self.assertEqual(lot.asset_category_id, self.other)
        self.assertEqual(product.lot_asset_category_id, self.other)
