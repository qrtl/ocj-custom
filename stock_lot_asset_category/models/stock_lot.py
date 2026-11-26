# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = ["stock.lot", "stock.lot.asset.category.lock.mixin"]
    _asset_category_field = "asset_category_id"

    asset_category_id = fields.Many2one(
        comodel_name="stock.lot.asset.category",
        string="Asset Category",
        compute="_compute_asset_category_id",
        store=True,
        readonly=False,
        ondelete="restrict",
        copy=False,
        tracking=True,
        help="Who owns this serial/lot number. Defaults to the product's "
        "asset category and can be changed per serial/lot number.",
    )

    # Not on product_id.lot_asset_category_id: a new product default must not
    # rewrite the serials that already exist.
    @api.depends("product_id")
    def _compute_asset_category_id(self):
        for lot in self:
            lot.asset_category_id = lot.product_id.lot_asset_category_id
