# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lot_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Lot Product",
        compute="_compute_lot_product_id",
        store=True,
        readonly=False,
        precompute=True,
        check_company=True,
        domain="[('is_storable', '=', True)]",
        help="Storable product this line is about. It is the line's product when"
        " that one is storable; on a line of a service, such as a rental fee, it"
        " is set by hand.",
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial Number",
        index="btree_not_null",
        check_company=True,
        domain="[('product_id', '=', lot_product_id)]",
        help="Lot/serial number this line refers to. It is recorded independently"
        " from the stock moves, so that it can also be set on lines that are not"
        " backed by a delivery.",
    )

    @api.depends("product_id")
    def _compute_lot_product_id(self):
        for line in self:
            product = line.product_id
            line.lot_product_id = product if product.is_storable else False

    @api.constrains("lot_id", "lot_product_id", "product_id")
    def _check_lot_product(self):
        for line in self:
            product = line.product_id
            if product.is_storable and line.lot_product_id != product:
                raise ValidationError(
                    self.env._(
                        "The lot product of a line of %(product)s is that product.",
                        product=product.display_name,
                    )
                )
            if line.lot_id and line.lot_id.product_id != line.lot_product_id:
                raise ValidationError(
                    self.env._(
                        "Lot/serial number %(lot)s does not belong to the lot"
                        " product of the line.",
                        lot=line.lot_id.display_name,
                    )
                )
