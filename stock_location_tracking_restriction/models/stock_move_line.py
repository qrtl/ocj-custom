# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.exceptions import UserError

from .stock_location import ACCEPTED_TRACKINGS


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        res = super().write(vals)
        # Changing the destination of a done line moves its stock right away,
        # without going through _action_done().
        if "location_dest_id" in vals:
            self.filtered(
                lambda ml: ml.state == "done"
            )._check_product_tracking_restriction()
        return res

    def _check_product_tracking_restriction(self):
        # Lines with no quantity are dropped by _action_done() and move nothing.
        lines = self.filtered(lambda ml: ml.product_uom_id.compare(ml.quantity, 0) > 0)
        errors = []
        for location in lines.location_dest_id:
            restriction = location._get_product_tracking_restriction()
            if not restriction:
                continue
            products = lines.filtered(
                lambda ml, location=location, restriction=restriction: (
                    ml.location_dest_id == location
                    and ml.product_id.tracking not in ACCEPTED_TRACKINGS[restriction]
                )
            ).product_id
            for product in products:
                if restriction == "tracked":
                    message = self.env._(
                        "%(product)s is not tracked by serial or lot number and "
                        "cannot be put in %(location)s.",
                        product=product.display_name,
                        location=location.display_name,
                    )
                else:
                    message = self.env._(
                        "%(product)s is tracked by serial or lot number and "
                        "cannot be put in %(location)s.",
                        product=product.display_name,
                        location=location.display_name,
                    )
                errors.append(message)
        if errors:
            raise UserError("\n".join(errors))

    def _action_done(self):
        self._check_product_tracking_restriction()
        return super()._action_done()
