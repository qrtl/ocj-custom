# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _synchronize_quant(self, quantity, location, *args, **kwargs):
        # Core puts quantity back into the source when a done line is edited,
        # and moves untracked stock onto the lot there; neither brings stock in.
        if location == self.location_id and location != self.location_dest_id:
            self = self.with_context(skip_product_kind_restriction=True)
        return super()._synchronize_quant(quantity, location, *args, **kwargs)
