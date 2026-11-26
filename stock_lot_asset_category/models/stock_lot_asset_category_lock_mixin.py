# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError


class StockLotAssetCategoryLockMixin(models.AbstractModel):
    _name = "stock.lot.asset.category.lock.mixin"
    _description = "Stock Lot Asset Category Lock Mixin"
    _asset_category_field = None

    asset_category_locked = fields.Boolean(compute="_compute_asset_category_locked")

    @api.depends_context("uid")
    def _compute_asset_category_locked(self):
        can_assign = self.env["stock.lot.asset.category"]._can_assign()
        for rec in self:
            rec.asset_category_locked = not can_assign and bool(
                rec._origin[self._asset_category_field]
            )

    def write(self, vals):
        fname = self._asset_category_field
        if fname in vals and not self.env["stock.lot.asset.category"]._can_assign():
            if any(rec[fname] and rec[fname].id != vals[fname] for rec in self):
                raise AccessError(
                    self.env._(
                        "You are not allowed to change the asset category of a "
                        "product or of a serial/lot number once it is set."
                    )
                )
        return super().write(vals)
