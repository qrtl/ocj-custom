# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import Form, TransactionCase


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

    def test_a_contact_cannot_set_a_policy_of_its_own(self):
        # The sync runs downward only, so an edit on the contact would stick
        # there and silently differ from the company's policy.
        company = self.env["res.partner"].create(
            {"name": "病院B", "is_company": True, "prorated_billing": False}
        )
        contact = self.env["res.partner"].create(
            {"name": "請求先担当", "parent_id": company.id, "type": "invoice"}
        )
        with Form(contact) as form:
            self.assertTrue(form._get_modifier("prorated_billing", "readonly"))
            self.assertTrue(form._get_modifier("billing_scope", "readonly"))
