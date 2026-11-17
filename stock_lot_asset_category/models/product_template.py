# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lot_asset_category_id = fields.Many2one(
        comodel_name="stock.lot.asset.category",
        string="Default Asset Category",
        ondelete="restrict",
        copy=False,
        help="Asset category given to new serial/lot numbers of this product. "
        "Changing it does not change the existing ones.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("lot_asset_category_id") for vals in vals_list):
            self.env["stock.lot.asset.category"]._check_assign_access()
        return super().create(vals_list)

    def write(self, vals):
        if "lot_asset_category_id" in vals:
            self.env["stock.lot.asset.category"]._check_assign_access()
        return super().write(vals)
