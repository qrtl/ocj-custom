# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.commission_oca.tests.test_commission import TestCommissionBase


@tagged("post_install", "-at_install")
class TestAccountCommissionStockLot(TestCommissionBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commission = cls.commission_model.create(
            {"name": "10% fixed commission", "fix_qty": 10.0}
        )
        cls.agent = cls.res_partner_model.create(
            {
                "name": "Test Agent - Lot",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": cls.commission.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Serial tracked product for commissions",
                "is_storable": True,
                "tracking": "serial",
                "list_price": 100.0,
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "SN-COMM-0001", "product_id": cls.product.id}
        )

    def _settle(self):
        wizard = self.make_settle_model.create(
            {
                "date_to": fields.Date.today() + relativedelta(months=1),
                "settlement_type": "sale_invoice",
                "agent_ids": [Command.link(self.agent.id)],
            }
        )
        wizard.action_settle()
        return self.env["commission.settlement.line"].search(
            [("agent_id", "=", self.agent.id)]
        )

    def test_settlement_line_product_and_lot(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "lot_id": self.lot.id,
                            "agent_ids": [
                                Command.create(
                                    {
                                        "agent_id": self.agent.id,
                                        "commission_id": self.commission.id,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        settlement_lines = self._settle()
        self.assertEqual(len(settlement_lines), 1)
        self.assertEqual(settlement_lines.product_id, self.product)
        self.assertEqual(settlement_lines.lot_id, self.lot)
        # The snapshot must not follow a later change on the source invoice line
        new_lot = self.env["stock.lot"].create(
            {"name": "SN-COMM-0002", "product_id": self.product.id}
        )
        invoice.invoice_line_ids.filtered("product_id").lot_id = new_lot
        self.assertEqual(settlement_lines.lot_id, self.lot)
