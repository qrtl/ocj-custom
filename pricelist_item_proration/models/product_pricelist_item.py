# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# The method the counterpart applies. Odoo does not compute a prorated amount
# itself -- it holds the parameters and the consumer does the arithmetic -- so
# these are carried, not acted on.
PRORATION_METHODS = [
    ("1", "Daily rate x days"),
    ("2", "Monthly / 30 x days"),
    ("3", "Monthly / days in month x days"),
    ("4", "Monthly x 12 / 365 x days"),
    ("5", "Monthly x 12 / 365 x days, leap year aware"),
]
DEFAULT_PRORATION_METHOD = "3"
ROUNDINGS = [
    ("1", "Round down"),
    ("2", "Round up"),
    ("3", "Round half up"),
]


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # Set per customer and product rather than per product: the same customer
    # can be prorated on one piece of equipment and not on another, which is
    # why the pricelist item is the receptacle and the product is not.
    is_prorated = fields.Boolean(
        string="Prorated",
        help="Whether a partial period is charged pro rata rather than in full.",
    )
    proration_method = fields.Selection(
        selection=PRORATION_METHODS,
        default=DEFAULT_PRORATION_METHOD,
        help="How a partial period is converted into an amount. Odoo does not "
        "apply it; the value is carried to whoever bills.",
    )
    proration_rounding = fields.Selection(
        selection=ROUNDINGS,
        help="How the prorated amount is rounded to whole currency units.",
    )

    @api.constrains("is_prorated", "proration_method", "proration_rounding")
    def _check_proration(self):
        """Both parameters are required once proration is on.

        A prorated price missing either one cannot be computed by the consumer,
        and the gap would only surface as a wrong invoice.
        """
        for item in self:
            if item.is_prorated and not (
                item.proration_method and item.proration_rounding
            ):
                raise ValidationError(
                    self.env._(
                        "A prorated price needs both a proration method and a "
                        "rounding rule."
                    )
                )
