# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "stock.lot.asset.category.lock.mixin"]
    _asset_category_field = "lot_asset_category_id"

    lot_asset_category_id = fields.Many2one(
        comodel_name="stock.lot.asset.category",
        string="Default Asset Category",
        ondelete="restrict",
        copy=False,
        help="Asset category given to new serial/lot numbers of this product. "
        "Changing it does not change the existing ones.",
    )
