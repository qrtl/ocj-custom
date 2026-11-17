# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.exceptions import UserError

ACCEPTED_PRODUCT_KINDS = {
    "equipment": ("equipment", "accessory"),
    "consumable": ("consumable",),
}


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        mls = super().create(vals_list)
        mls.filtered(lambda ml: ml.state == "done")._check_product_kind_restriction()
        return mls

    def write(self, vals):
        res = super().write(vals)
        if "location_dest_id" in vals:
            self.filtered(
                lambda ml: ml.state == "done"
            )._check_product_kind_restriction()
        return res

    def _check_product_kind_restriction(self):
        # Products with no product kind (services, gas cylinders, ...) are left
        # out of the check on purpose: the kind is empty by design for them.
        lines = self.filtered(
            lambda ml: ml.product_id.product_kind
            and ml.product_uom_id.compare(ml.quantity, 0) > 0
        )
        errors = []
        for location in lines.location_dest_id:
            restriction = location._get_product_kind_restriction()
            if not restriction:
                continue
            accepted = ACCEPTED_PRODUCT_KINDS[restriction]
            products = lines.filtered(
                lambda ml, location=location, accepted=accepted: (
                    ml.location_dest_id == location
                    and ml.product_id.product_kind not in accepted
                )
            ).product_id
            for product in products:
                if restriction == "equipment":
                    message = self.env._(
                        "%(product)s is not equipment or an accessory and "
                        "cannot be put in %(location)s.",
                        product=product.display_name,
                        location=location.display_name,
                    )
                else:
                    message = self.env._(
                        "%(product)s is not a consumable and cannot be put in "
                        "%(location)s.",
                        product=product.display_name,
                        location=location.display_name,
                    )
                errors.append(message)
        if errors:
            raise UserError("\n".join(errors))

    def _action_done(self):
        self._check_product_kind_restriction()
        return super()._action_done()
