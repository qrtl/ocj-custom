# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockLotQualityStatus(models.Model):
    _name = "stock.lot.quality.status"
    _description = "Stock Lot Quality Status"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(help="Optional short code for referencing this status.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    category = fields.Selection(
        [
            ("usable", "Usable Stock"),
            ("usable_unshippable", "Usable Stock (Not Shippable)"),
            ("excluded", "Excluded"),
        ],
        string="Major Category",
        help="Stock-activity grouping used as the aggregation axis for inventory "
        "and accounting reports.",
    )
    shippability = fields.Selection(
        [
            ("yes", "Shippable"),
            ("conditional", "Conditional"),
            ("no", "Not Shippable"),
        ],
        help="Whether stock with this status can be shipped to patients.",
    )
    shippability_note = fields.Char(
        help="Free-text qualifier for the shippability "
        "(e.g. ship A-grade first, repair vendor only, maintenance branch only)."
    )
    shipping_priority = fields.Integer(
        help="Picking order among shippable statuses (lower is picked first). "
        "0 means the status is not part of the shipping order.",
    )
    is_default = fields.Boolean(
        string="Default for New Lots",
        help="The status assigned to newly created lots/serials when none is set. "
        "Only one status can be the default.",
    )
    description = fields.Text(translate=True)

    @api.constrains("is_default")
    def _check_single_default(self):
        if (
            self.filtered("is_default")
            and self.search_count([("is_default", "=", True)]) > 1
        ):
            raise ValidationError(
                self.env._(
                    "Only one quality status can be set as the default for new lots."
                )
            )
