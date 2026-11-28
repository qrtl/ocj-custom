# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account_accountant.tests.common import TestBankRecWidgetCommon


@tagged("post_install", "-at_install")
class TestBankFeeAutoReconcile(TestBankRecWidgetCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "account_accountant.bank_rec_payment_tolerance", "0.03"
        )
        cls.journal = cls.company_data["default_journal_bank"]
        cls.fee_account = cls.company_data["default_account_expense"]
        cls.fee_model = cls.env["account.reconcile.model"]._load_records(
            [
                {
                    "xml_id": f"account.account_reco_model_fee_{cls.journal.id}",
                    "values": {
                        "company_id": cls.journal.company_id.id,
                        "name": "Fees",
                        "trigger": "auto_reconcile",
                        "match_journal_ids": [Command.set(cls.journal.ids)],
                        "line_ids": [
                            Command.create(
                                {
                                    "account_id": cls.fee_account.id,
                                    "label": "Bank Fees",
                                    "amount_type": "percentage",
                                    "amount_string": "100",
                                }
                            )
                        ],
                    },
                }
            ]
        )
        # The XMLID only exists once _load_records is through, so the value
        # stored while creating the model does not reflect it yet.
        cls.fee_model.invalidate_recordset(["can_be_proposed"])
        cls.fee_model.modified(["trigger"])

    def _create_receivable_invoice(self, price_unit):
        return self._create_invoice_line(
            "out_invoice",
            partner_id=self.partner_a.id,
            invoice_date="2019-01-01",
            invoice_line_ids=[{"price_unit": price_unit}],
        )

    def test_fee_model_is_not_proposable(self):
        self.assertFalse(
            self.fee_model.can_be_proposed,
            "An automated fee model must stay out of the proposable models, "
            "or it applies to every transaction it is offered for.",
        )

    def test_fee_is_written_off_on_import(self):
        invoice = self._create_receivable_invoice(1000.0)
        st_line = self._create_st_line(
            990.0,
            date="2019-01-10",
            partner_id=self.partner_a.id,
            update_create_date=False,
        )
        st_line._try_auto_reconcile_statement_lines()
        self.assertRecordValues(
            st_line.line_ids,
            [
                {"account_id": self.journal.default_account_id.id, "balance": 990.0},
                {"account_id": invoice.account_id.id, "balance": -1000.0},
                {"account_id": self.fee_account.id, "balance": 10.0},
            ],
        )
        self.assertTrue(st_line.is_reconciled)
        self.assertEqual(invoice.move_id.payment_state, "paid")

    def test_unmatched_transaction_is_left_alone(self):
        st_line = self._create_st_line(
            990.0,
            date="2019-01-10",
            partner_id=self.partner_a.id,
            update_create_date=False,
        )
        st_line._try_auto_reconcile_statement_lines()
        self.assertRecordValues(
            st_line.line_ids,
            [
                {"account_id": self.journal.default_account_id.id, "balance": 990.0},
                {"account_id": self.journal.suspense_account_id.id, "balance": -990.0},
            ],
        )
        self.assertFalse(st_line.is_reconciled)

    def test_fee_above_the_limit_is_left_alone(self):
        # 100 out of 900 is far beyond what Odoo accepts as a fee, so the
        # transaction has to reach the accountant rather than be written off.
        self._create_receivable_invoice(1000.0)
        st_line = self._create_st_line(
            900.0,
            date="2019-01-10",
            partner_id=self.partner_a.id,
            update_create_date=False,
        )
        st_line._try_auto_reconcile_statement_lines()
        self.assertNotIn(self.fee_account, st_line.line_ids.account_id)
        self.assertFalse(st_line.is_reconciled)
