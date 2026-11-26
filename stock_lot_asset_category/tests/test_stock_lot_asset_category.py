# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import Form
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

    def _create_user(self):
        return new_test_user(
            self.env,
            login="stock_manager",
            groups="stock.group_stock_manager,product.group_product_manager,"
            "stock.group_production_lot",
        )

    def test_form_locks_only_the_saved_category(self):
        """The form field stays editable until the picked value is saved."""
        lot = self._create_lot("SN-0001", asset_category_id=False)
        lot = lot.with_user(self._create_user())
        with Form(lot) as form:
            form.asset_category_id = self.own
            form.asset_category_id = self.other
        self.assertEqual(lot.asset_category_id, self.other)
        with Form(lot) as form, self.assertRaises(AssertionError):
            form.asset_category_id = self.own

    def test_only_assigners_change_a_set_category(self):
        """Without the group, an empty category can be filled but not a set one."""
        user = self._create_user()
        lot = self._create_lot("SN-0001").with_user(user)
        product = self.product.with_user(user)
        for record, fname in [
            (lot, "asset_category_id"),
            (product, "lot_asset_category_id"),
        ]:
            with self.assertRaises(AccessError):
                record[fname] = self.other
            with self.assertRaises(AccessError):
                record[fname] = False
            record[fname] = self.own
        template = (
            self.env["product.template"]
            .with_user(user)
            .create({"name": "New Product", "lot_asset_category_id": self.other.id})
        )
        self.assertEqual(template.lot_asset_category_id, self.other)
        template = template.copy()
        template.lot_asset_category_id = self.own
        lot = lot.create(
            {
                "name": "SN-0002",
                "product_id": product.id,
                "asset_category_id": self.other.id,
            }
        )
        self.assertEqual(lot.asset_category_id, self.other)
        user.group_ids = [
            Command.link(
                self.env.ref("stock_lot_asset_category.group_assign_asset_category").id
            )
        ]
        lot.asset_category_id = self.own
        product.lot_asset_category_id = self.other
        self.assertEqual(lot.asset_category_id, self.own)
        self.assertEqual(product.lot_asset_category_id, self.other)
