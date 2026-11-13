# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartnerPayer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env["res.partner"]
        cls.payer = Partner.create({"name": "Head Office", "is_company": True})
        cls.outer = Partner.create({"name": "Outer", "is_company": True})
        cls.member = Partner.create(
            {
                "name": "Member",
                "is_company": True,
                "payer_partner_id": cls.payer.id,
            }
        )

    def test_payer_of_others_cannot_be_paid_for_while_member_archived(self):
        """The guard must still see a member that is archived."""
        self.member.action_archive()
        with self.assertRaises(ValidationError):
            self.payer.payer_partner_id = self.outer

    def test_paid_for_includes_archived_member(self):
        """An archived member's open invoices stay in the payer's group."""
        self.member.action_archive()
        self.assertIn(self.member.id, self.payer._get_paid_for_partner_ids())

    def test_child_contact_follows_commercial_payer(self):
        """Receivable lines carry the commercial partner, so the payer is set there."""
        child = self.env["res.partner"].create(
            {"name": "Billing", "type": "invoice", "parent_id": self.member.id}
        )
        self.assertEqual(child.payer_partner_id, self.payer)
        self.member.payer_partner_id = False
        self.assertFalse(child.payer_partner_id)
        self.assertNotIn(self.member.id, self.payer._get_paid_for_partner_ids())
