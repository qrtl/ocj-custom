# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestInstallationStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True, "tracking": "serial"}
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "LOT-0001", "product_id": cls.product.id}
        )

    def test_set_installed_sets_both_dates(self):
        self.lot.installation_status = "installed"
        self.assertTrue(self.lot.installation_status_change_date)
        self.assertTrue(self.lot.installation_completed_date)
        self.assertEqual(
            self.lot.installation_status_change_date,
            self.lot.installation_completed_date,
        )

    def test_create_installed_sets_both_dates(self):
        # Creating a lot directly as "installed" (e.g. via import) must stamp
        # the dates, since create() does not route through write().
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-0002",
                "product_id": self.product.id,
                "installation_status": "installed",
            }
        )
        self.assertTrue(lot.installation_status_change_date)
        self.assertTrue(lot.installation_completed_date)

    def test_revert_keeps_completed_date(self):
        self.lot.installation_status = "installed"
        completed_date = self.lot.installation_completed_date
        # Reverting to "not_installed" refreshes the change date but must keep
        # the historical completion date.
        self.lot.write({"installation_status": "not_installed"})
        self.assertEqual(self.lot.installation_completed_date, completed_date)
        self.assertEqual(self.lot.installation_status, "not_installed")

    def test_reinstall_refreshes_completed_date(self):
        # Seed an old completion date, then revert (which keeps it).
        old_date = fields.Datetime.now() - timedelta(days=2)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_completed_date": old_date,
            }
        )
        self.lot.write({"installation_status": "not_installed"})
        self.assertEqual(self.lot.installation_completed_date, old_date)
        # Transitioning back to "installed" sets a fresh completion date.
        self.lot.write({"installation_status": "installed"})
        self.assertGreater(self.lot.installation_completed_date, old_date)

    def test_other_write_does_not_touch_dates(self):
        self.lot.installation_status = "installed"
        change_date = self.lot.installation_status_change_date
        completed_date = self.lot.installation_completed_date
        # A write that does not include installation_status leaves the dates as
        # they were.
        self.lot.write({"name": "LOT-0001-RENAMED"})
        self.assertEqual(self.lot.installation_status_change_date, change_date)
        self.assertEqual(self.lot.installation_completed_date, completed_date)

    def test_manual_date_takes_priority(self):
        manual_date = fields.Datetime.now() - timedelta(days=2)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_status_change_date": manual_date,
                "installation_completed_date": manual_date,
            }
        )
        self.assertEqual(self.lot.installation_status_change_date, manual_date)
        self.assertEqual(self.lot.installation_completed_date, manual_date)

    def test_quant_related_fields(self):
        self.lot.installation_status = "installed"
        quant = self.env["stock.quant"].create(
            {
                "lot_id": self.lot.id,
                "product_id": self.product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        self.assertEqual(quant.installation_status, "installed")
        self.assertEqual(
            quant.installation_completed_date,
            self.lot.installation_completed_date,
        )
