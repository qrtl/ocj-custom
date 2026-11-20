# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

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

    @api.model_create_multi
    def create(self, vals_list):
        if any("asset_category_id" in vals for vals in vals_list):
            self.env["stock.lot.asset.category"]._check_assign_access()
        return super().create(vals_list)

    def write(self, vals):
        if "asset_category_id" in vals:
            self.env["stock.lot.asset.category"]._check_assign_access()
        return super().write(vals)
