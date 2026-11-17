# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    product_kind_restriction = fields.Selection(
        selection=[
            ("equipment", "Equipment and Accessories Only"),
            ("consumable", "Consumables Only"),
        ],
        string="Accepted Products",
        help="Limit the products that can be put in this location and its "
        "sublocations by their product kind. Products with no product kind are "
        "accepted anywhere. A sublocation with its own setting follows that "
        "setting instead. Stock already in the location is not affected.",
    )

    def _get_product_kind_restriction(self):
        self.ensure_one()
        ancestor_ids = [int(i) for i in self.parent_path.split("/")[:-1]]
        for ancestor in reversed(self.browse(ancestor_ids)):
            if ancestor.product_kind_restriction:
                return ancestor.product_kind_restriction
        return False
