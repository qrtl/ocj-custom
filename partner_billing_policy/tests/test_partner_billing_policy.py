# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestPartnerBillingPolicy(TransactionCase):
    def test_a_contact_carries_its_company_policy(self):
        company = self.env["res.partner"].create(
            {
                "name": "病院A",
                "is_company": True,
                "billing_scope": "full",
                "prorated_billing": True,
                "revenue_timing": "period_end",
                "bill_on_loss": True,
            }
        )
        contact = self.env["res.partner"].create(
            {"name": "請求先担当", "parent_id": company.id, "type": "invoice"}
        )
        self.assertEqual(contact.billing_scope, "full")
        self.assertTrue(contact.prorated_billing)
        self.assertEqual(contact.revenue_timing, "period_end")
        self.assertTrue(contact.bill_on_loss)
        # A later change on the company reaches the contact as well.
        company.prorated_billing = False
        self.assertFalse(contact.prorated_billing)
