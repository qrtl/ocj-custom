# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.commission_oca.tests.test_commission import TestCommissionBase


@tagged("post_install", "-at_install")
class TestAccountCommissionAnalytic(TestCommissionBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.commission = cls.commission_model.create(
            {"name": "10%", "fix_qty": 10.0, "amount_base_type": "net_amount"}
        )
        cls.agent = cls.res_partner_model.create(
            {
                "name": "Agent",
                "agent": True,
                "settlement": "monthly",
                "commission_id": cls.commission.id,
            }
        )
        plan = cls.env["account.analytic.plan"].create({"name": "Cost Center"})
        cls.center_a, cls.center_b = cls.env["account.analytic.account"].create(
            [{"name": name, "plan_id": plan.id} for name in "AB"]
        )
        cls.product = cls.env["product.product"].create({"name": "Sold product"})

    def _settle(self, sales):
        invoices = self.env["account.move"].create(
            [
                {
                    "move_type": move_type,
                    "partner_id": self.partner.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "price_unit": price,
                                "tax_ids": [Command.clear()],
                                "analytic_distribution": center
                                and {str(center.id): 100},
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
                for move_type, price, center in sales
            ]
        )
        invoices.action_post()
        wizard = self.make_settle_model.create(
            self._get_make_settle_vals(self.agent, period=1)
            | {"settlement_type": "sale_invoice"}
        )
        wizard.action_settle()
        settlement = self.settle_model.search([("agent_id", "=", self.agent.id)])
        self.assertEqual(len(settlement), 1)
        return settlement

    def _bill_lines(self, settlement):
        bill = settlement.make_invoices(self.journal, self.commission_product)
        return {
            line.analytic_distribution
            and next(iter(line.analytic_distribution)): line.price_subtotal
            for line in bill.invoice_line_ids
        }

    def test_bill_lines_follow_the_settled_invoices(self):
        # One line per distribution; a line without one is left to the models.
        settlement = self._settle(
            [
                ("out_invoice", 100, self.center_a),
                ("out_invoice", 100, self.center_a),
                ("out_invoice", 100, self.center_b),
                ("out_invoice", 100, False),
            ]
        )
        self.assertEqual(
            self._bill_lines(settlement),
            {str(self.center_a.id): 20, str(self.center_b.id): 10, False: 10},
        )

    def test_refund_settled_with_invoices_keeps_its_sign(self):
        # A part can be negative while the settlement total is positive.
        settlement = self._settle(
            [("out_invoice", 200, self.center_a), ("out_refund", 100, self.center_b)]
        )
        self.assertEqual(
            self._bill_lines(settlement),
            {str(self.center_a.id): 20, str(self.center_b.id): -10},
        )
