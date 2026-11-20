# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveLineStockLot(TransactionCase):
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
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.lot = cls.env["stock.lot"].create(
            {"name": "SN-0001", "product_id": cls.product_serial.id}
        )

    def _create_invoice(self, product, lot=None, **vals):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2026-01-31",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "lot_id": lot.id if lot else False,
                            **vals,
                        }
                    )
                ],
            }
        )

    def test_lot_stored_on_invoice_line(self):
        invoice = self._create_invoice(self.product_serial, self.lot)
        self.assertEqual(invoice.invoice_line_ids.lot_id, self.lot)

    def test_lot_product_mismatch(self):
        with self.assertRaises(ValidationError):
            self._create_invoice(self.product_other, self.lot)

    def test_product_change_on_line_with_lot(self):
        invoice = self._create_invoice(self.product_serial, self.lot)
        with self.assertRaises(ValidationError):
            invoice.invoice_line_ids.product_id = self.product_other

    def test_service_line_names_its_lot_product(self):
        # A service has no lots: the line says which product the lot is of.
        invoice = self._create_invoice(
            self.product_other, self.lot, lot_product_id=self.product_serial.id
        )
        self.assertEqual(invoice.invoice_line_ids.lot_id, self.lot)

    def test_storable_line_keeps_its_own_product(self):
        other = self.product_serial.copy()
        with self.assertRaises(ValidationError):
            self._create_invoice(self.product_serial, lot_product_id=other.id)
