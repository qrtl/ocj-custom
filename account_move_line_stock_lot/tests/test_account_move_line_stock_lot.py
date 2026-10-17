# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveLineStockLot(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Serial tracked product",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.product_other = cls.env["product.product"].create({"name": "Other product"})
        cls.lot = cls.env["stock.lot"].create(
            {"name": "SN-0001", "product_id": cls.product_serial.id}
        )

    def _create_invoice(self, product, lot=None):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "invoice_date": "2026-01-31",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "lot_id": lot.id if lot else False,
                        }
                    )
                ],
            }
        )

    def test_01_lot_stored_on_invoice_line(self):
        invoice = self._create_invoice(self.product_serial, self.lot)
        self.assertEqual(invoice.invoice_line_ids.lot_id, self.lot)

    def test_02_lot_product_mismatch(self):
        with self.assertRaises(ValidationError):
            self._create_invoice(self.product_other, self.lot)
