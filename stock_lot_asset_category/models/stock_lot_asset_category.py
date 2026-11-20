# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError


class StockLotAssetCategory(models.Model):
    _name = "stock.lot.asset.category"
    _description = "Stock Lot Asset Category"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(help="Optional short code for referencing this category.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        "unique(code)", "The asset category code must be unique."
    )

    @api.model
    def _check_assign_access(self):
        """Raise unless the user may set the asset category of lots."""
        if self.env.su or self.env.user.has_group(
            "stock_lot_asset_category.group_assign_asset_category"
        ):
            return
        raise AccessError(
            self.env._(
                "You are not allowed to set the asset category of a serial/lot number."
            )
        )
