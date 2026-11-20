# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveLineStockLotRentalFee(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        classification = cls.env["product.equipment.classification"].create(
            {"name": "Oxygen Concentrator", "code": "100"}
        )
        cls.machine, cls.other = cls.env["product.product"].create(
            [
                {
                    "name": name,
                    "is_storable": True,
                    "tracking": "serial",
                    "product_kind": "equipment",
                    "equipment_classification_id": classification.id,
                }
                for name in ("Concentrator", "Other machine")
            ]
        )
        cls.fee = cls.env["product.product"].create(
            {
                "name": "Rental fee",
                "type": "service",
                "product_kind": "rental_fee",
                "equipment_classification_id": classification.id,
                "rental_set_component_ids": [
                    Command.set(cls.machine.product_tmpl_id.ids)
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})

    def _invoice(self, lot_product):
        lot = self.env["stock.lot"].create(
            {"name": lot_product.name, "product_id": lot_product.id}
        )
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.fee.id,
                            "quantity": 1,
                            "lot_product_id": lot_product.id,
                            "lot_id": lot.id,
                        }
                    )
                ],
            }
        )

    def test_lot_of_set_component(self):
        # The fee line names a machine of its set, no other.
        self.assertTrue(self._invoice(self.machine).invoice_line_ids.lot_id)
        with self.assertRaises(ValidationError):
            self._invoice(self.other)
