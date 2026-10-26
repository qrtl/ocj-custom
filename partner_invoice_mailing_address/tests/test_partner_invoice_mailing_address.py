# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.base.tests.common import BaseCommon


class TestPartnerInvoiceMailingAddress(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["account.journal"].create(
            {"code": "SALE", "name": "Sales", "type": "sale"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Clinic",
                "is_company": True,
                "invoice_mailing_address": "Mailing Street 2-2",
            }
        )
        cls.Report = cls.env["ir.actions.report"].with_context(
            apply_alternative_layout=True
        )

    def _render(self, report_ref, record):
        return str(self.Report._render_qweb_html(report_ref, record.ids)[0])

    def test_invoice(self):
        invoice = self.env["account.move"].create(
            {"move_type": "out_invoice", "partner_id": self.partner.id}
        )
        html = self._render("account.account_invoices", invoice)
        self.assertIn("Mailing Street 2-2", html)

    def test_summary_invoice(self):
        billing = self.env["account.billing"].create(
            {
                "partner_id": self.partner.id,
                "bill_type": "out_invoice",
                "threshold_date": "2026-10-31",
            }
        )
        html = self._render(
            "l10n_jp_summary_invoice.report_jp_summary_invoice", billing
        )
        self.assertIn("Mailing Street 2-2", html)
