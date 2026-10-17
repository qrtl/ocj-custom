# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial Number",
        index="btree_not_null",
        domain="[('product_id', '=', product_id)]",
        help="Lot/serial number this line refers to. It is recorded independently"
        " from the stock moves, so that it can also be set on lines that are not"
        " backed by a delivery.",
    )

    @api.constrains("lot_id", "product_id")
    def _check_lot_product(self):
        for line in self.filtered("lot_id"):
            if line.lot_id.product_id != line.product_id:
                raise ValidationError(
                    self.env._(
                        "Lot/serial number %(lot)s does not belong to product"
                        " %(product)s.",
                        lot=line.lot_id.display_name,
                        product=line.product_id.display_name,
                    )
                )
