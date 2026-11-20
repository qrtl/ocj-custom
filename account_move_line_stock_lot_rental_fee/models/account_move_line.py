# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lot_product_id = fields.Many2one(
        domain="[('is_storable', '=', True), ('product_tmpl_id"
        ".rental_set_fee_tmpl_ids.product_variant_ids', 'in', [product_id])]"
        " if lot_product_from_set else [('is_storable', '=', True)]",
    )
    lot_product_from_set = fields.Boolean(compute="_compute_lot_product_from_set")

    @api.depends("product_id")
    def _compute_lot_product_from_set(self):
        for line in self:
            line.lot_product_from_set = line.product_id.product_kind == "rental_fee"

    @api.constrains("lot_product_id", "product_id")
    def _check_lot_product_in_set(self):
        for line in self.filtered("lot_product_id"):
            product = line.product_id
            components = product.rental_set_component_ids.product_variant_ids
            if line.lot_product_from_set and line.lot_product_id not in components:
                raise ValidationError(
                    self.env._(
                        "%(lot_product)s is not a set component of %(product)s.",
                        lot_product=line.lot_product_id.display_name,
                        product=product.display_name,
                    )
                )
