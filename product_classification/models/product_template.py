# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_kind = fields.Selection(
        selection=[
            ("equipment", "Equipment"),
            ("accessory", "Accessory"),
            ("consumable", "Consumable"),
        ],
        help="Whether the product is an equipment, an accessory or a "
        "consumable. Used in the Navi in Flow integration.",
    )
    manufacturer_id = fields.Many2one(
        comodel_name="product.manufacturer",
        string="Manufacturer",
        help="Manufacturer of the product. Used in the Navi in Flow integration.",
    )
    equipment_classification_id = fields.Many2one(
        comodel_name="product.equipment.classification",
        string="Equipment Classification",
        help="Primary classification of an equipment or accessory product. "
        "Used in the Navi in Flow integration.",
    )
    middle_category_id = fields.Many2one(
        comodel_name="product.middle.category",
        string="Middle Category",
        help="Middle-level product category.",
    )
    minor_category_id = fields.Many2one(
        comodel_name="product.minor.category",
        string="Minor Category",
        help="Minor-level product category.",
    )

    @api.constrains("product_kind", "equipment_classification_id")
    def _check_equipment_classification(self):
        # An equipment or accessory with no classification is silently left out of
        # the product master feed, so the omission only surfaces when the
        # counterpart asks why an item is missing. The constraint runs only when
        # one of its own fields is written, which keeps existing products editable
        # for unrelated fields while the classification data is being filled in.
        for template in self:
            if (
                template.product_kind in ("equipment", "accessory")
                and not template.equipment_classification_id
            ):
                raise ValidationError(
                    self.env._(
                        "%(product)s is an equipment or an accessory, so it needs "
                        "an equipment classification.",
                        product=template.display_name,
                    )
                )
