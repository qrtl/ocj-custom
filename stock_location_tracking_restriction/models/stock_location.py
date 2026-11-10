# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    product_tracking_restriction = fields.Selection(
        selection=[
            ("tracked", "Serial- or Lot-Tracked Only"),
            ("quantity", "Quantity-Tracked Only"),
        ],
        string="Accepted Products",
        help="Limit the products that can be put in this location and its "
        "sublocations by how they are tracked. A sublocation with its own "
        "setting follows that setting instead. Stock already in the location "
        "is not affected.",
    )

    def _get_product_tracking_restriction(self):
        """Return the restriction that applies to the location: its own, or
        else that of its nearest parent that has one."""
        self.ensure_one()
        # parent_path lists the ids from the root down to the location itself.
        ancestor_ids = [int(i) for i in self.parent_path.split("/")[:-1]]
        for ancestor in reversed(self.browse(ancestor_ids)):
            if ancestor.product_tracking_restriction:
                return ancestor.product_tracking_restriction
        return False
