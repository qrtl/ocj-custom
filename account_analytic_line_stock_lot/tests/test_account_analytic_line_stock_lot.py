# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountAnalyticLineStockLot(TransactionCase):
    def test_analytic_item_follows_the_journal_item(self):
        # The lot is copied when the item is made, and again when it changes.
        product = self.env["product.product"].create(
            {"name": "Machine", "is_storable": True, "tracking": "serial"}
        )
        lots = self.env["stock.lot"].create(
            [{"name": name, "product_id": product.id} for name in ("SN-1", "SN-2")]
        )
        plan = self.env["account.analytic.plan"].create({"name": "Plan"})
        account = self.env["account.analytic.account"].create(
            {"name": "Analytic", "plan_id": plan.id}
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.env["res.partner"].create({"name": "Customer"}).id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "price_unit": 100.0,
                            "lot_id": lots[0].id,
                            "analytic_distribution": {str(account.id): 100},
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        item = invoice.invoice_line_ids.analytic_line_ids
        self.assertEqual(item.lot_product_id, product)
        self.assertEqual(item.lot_id, lots[0])
        invoice.invoice_line_ids.lot_id = lots[1]
        self.assertEqual(item.lot_id, lots[1])
