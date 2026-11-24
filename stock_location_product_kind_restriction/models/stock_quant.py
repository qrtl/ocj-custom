# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.exceptions import UserError

ACCEPTED_PRODUCT_KINDS = {
    "equipment": ("equipment", "accessory"),
    "consumable": ("consumable",),
}


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _update_available_quantity(
        self, product_id, location_id, quantity=False, **kwargs
    ):
        if quantity and product_id.uom_id.compare(quantity, 0) > 0:
            self._check_product_kind_restriction(product_id, location_id)
        return super()._update_available_quantity(
            product_id, location_id, quantity=quantity, **kwargs
        )

    def _check_product_kind_restriction(self, product, location):
        if not product.product_kind:
            return
        restriction = location._get_product_kind_restriction()
        if (
            not restriction
            or product.product_kind in ACCEPTED_PRODUCT_KINDS[restriction]
        ):
            return
        label = dict(
            location._fields["product_kind_restriction"]._description_selection(
                self.env
            )
        )[restriction]
        raise UserError(
            self.env._(
                "%(product)s cannot be put in %(location)s "
                "(Accepted Products: %(accepted)s).",
                product=product.display_name,
                location=location.display_name,
                accepted=label,
            )
        )
