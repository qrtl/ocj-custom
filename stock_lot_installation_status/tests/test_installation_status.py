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

    def test_rewrite_same_status_keeps_dates(self):
        old_date = fields.Datetime.now() - timedelta(days=30)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_status_change_date": old_date,
                "installation_completed_date": old_date,
            }
        )
        # Not a transition, so the dates must not move.
        self.lot.write({"installation_status": "installed"})
        self.assertEqual(self.lot.installation_status_change_date, old_date)
        self.assertEqual(self.lot.installation_completed_date, old_date)

    def test_mixed_recordset_only_stamps_transitions(self):
        other = self.env["stock.lot"].create(
            {"name": "LOT-0003", "product_id": self.product.id}
        )
        old_date = fields.Datetime.now() - timedelta(days=30)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_status_change_date": old_date,
                "installation_completed_date": old_date,
            }
        )
        # One write, two outcomes.
        (self.lot | other).write({"installation_status": "installed"})
        self.assertEqual(self.lot.installation_completed_date, old_date)
        self.assertGreater(other.installation_completed_date, old_date)

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

    def test_first_installation_date_is_set_on_the_first_install(self):
        self.lot.installation_status = "installed"
        self.assertEqual(
            self.lot.first_installation_date, self.lot.installation_completed_date
        )

    def test_first_installation_date_survives_a_reinstall(self):
        original = fields.Datetime.now() - timedelta(days=400)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_completed_date": original,
            }
        )
        self.assertEqual(self.lot.first_installation_date, original)
        # Recovered, then installed again: only the completion date moves.
        self.lot.write({"installation_status": "not_installed"})
        self.lot.write({"installation_status": "installed"})
        self.assertEqual(self.lot.first_installation_date, original)
        self.assertGreater(self.lot.installation_completed_date, original)

    def test_first_installation_date_is_not_set_by_a_recovery(self):
        self.lot.write({"installation_status": "not_installed"})
        self.assertFalse(self.lot.first_installation_date)

    def test_first_installation_date_created_as_installed(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-0004",
                "product_id": self.product.id,
                "installation_status": "installed",
            }
        )
        self.assertEqual(lot.first_installation_date, lot.installation_completed_date)

    def test_first_installation_date_accepts_a_manual_correction(self):
        corrected = fields.Datetime.now() - timedelta(days=900)
        self.lot.installation_status = "installed"
        self.lot.first_installation_date = corrected
        # A later installation must not undo it.
        self.lot.write({"installation_status": "not_installed"})
        self.lot.write({"installation_status": "installed"})
        self.assertEqual(self.lot.first_installation_date, corrected)

    def test_mixed_recordset_splits_on_the_first_installation(self):
        original = fields.Datetime.now() - timedelta(days=400)
        self.lot.write(
            {
                "installation_status": "installed",
                "installation_completed_date": original,
            }
        )
        self.lot.write({"installation_status": "not_installed"})
        never = self.env["stock.lot"].create(
            {"name": "LOT-0005", "product_id": self.product.id}
        )
        # One write: the veteran keeps its date, the new lot gets one.
        (self.lot | never).write({"installation_status": "installed"})
        self.assertEqual(self.lot.first_installation_date, original)
        self.assertEqual(
            never.first_installation_date, never.installation_completed_date
        )

    def test_first_installation_date_is_tracked(self):
        # Tracking runs on precommit; draining the fixture's own batch first
        # stops Odoo folding the change into the creation.
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.lot.installation_status = "installed"
        self.env.flush_all()
        self.env.cr.precommit.run()
        messages = self.env["mail.message"].search(
            [("model", "=", "stock.lot"), ("res_id", "=", self.lot.id)]
        )
        tracked = messages.tracking_value_ids.field_id.mapped("name")
        self.assertIn("first_installation_date", tracked)

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
        self.assertEqual(
            quant.first_installation_date, self.lot.first_installation_date
        )
