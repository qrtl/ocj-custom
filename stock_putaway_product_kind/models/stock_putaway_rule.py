# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    product_kind = fields.Selection(
        selection="_selection_product_kind",
        help="Apply the rule only to products of this kind. Leave empty to apply "
        "it to any product.",
    )

    def _selection_product_kind(self):
        # The labels of product_classification's field, in the user's language.
        field = self.env["product.template"]._fields["product_kind"]
        return field._description_selection(self.env)

    def _get_putaway_location(
        self, product, quantity=0, package=None, packaging=None, qty_by_location=None
    ):
        # Without this filter a rule with a product kind and no product or
        # category would be taken by the standard matching as one for any product.
        rules = self.filtered(
            lambda rule: not rule.product_kind
            or rule.product_kind == product.product_kind
        )
        return super(StockPutawayRule, rules)._get_putaway_location(
            product,
            quantity=quantity,
            package=package,
            packaging=packaging,
            qty_by_location=qty_by_location,
        )
