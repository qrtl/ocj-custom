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
            ("rental_fee", "Rental Fee"),
        ],
        help="What the product is: one of the goods - equipment, an accessory "
        "or a consumable - or the fee charged for renting equipment, which is a "
        "service rather than goods. Used in the Navi in Flow integration.",
    )
    manufacturer_id = fields.Many2one(
        comodel_name="product.manufacturer",
        string="Manufacturer",
        help="Manufacturer of the product. Used in the Navi in Flow integration.",
    )
    equipment_classification_id = fields.Many2one(
        comodel_name="product.equipment.classification",
        string="Equipment Classification",
        help="Primary classification of an equipment or accessory product, or "
        "of the equipment a rental fee is charged for. Used in the Navi in Flow "
        "integration.",
    )
    middle_category_id = fields.Many2one(
        comodel_name="product.middle.category",
        string="Middle Category",
        domain="[('categ_id', 'parent_of', categ_id)]",
        help="Middle-level product category. Only the middle categories under "
        "the product category or one of its parents can be selected.",
    )
    minor_category_id = fields.Many2one(
        comodel_name="product.minor.category",
        string="Minor Category",
        domain="[('middle_category_id', '=?', middle_category_id)]",
        help="Minor-level product category. Once a middle category is set, only "
        "the minor categories under it can be selected.",
    )

    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        # Mirror the 'parent_of' domain of the field: the middle category stays
        # only while its product category is the product's or one of its parents.
        middle_categ = self.middle_category_id.categ_id
        if self.middle_category_id and not (
            middle_categ
            and (self.categ_id.parent_path or "").startswith(middle_categ.parent_path)
        ):
            self.middle_category_id = False

    @api.onchange("middle_category_id")
    def _onchange_middle_category_id(self):
        if (
            self.minor_category_id
            and self.minor_category_id.middle_category_id != self.middle_category_id
        ):
            self.minor_category_id = False

    @api.constrains("product_kind", "equipment_classification_id")
    def _check_equipment_classification(self):
        # A product of these kinds with no classification is silently left out of
        # the product master feed, so the omission only surfaces when the
        # counterpart asks why an item is missing. A rental fee is included
        # because the classification is what the fee is charged against, and the
        # feed cannot report a rental without it. The constraint runs only when
        # one of its own fields is written, which keeps existing products editable
        # for unrelated fields while the classification data is being filled in.
        for template in self:
            if (
                template.product_kind in ("equipment", "accessory", "rental_fee")
                and not template.equipment_classification_id
            ):
                raise ValidationError(
                    self.env._(
                        "%(product)s is an equipment, an accessory or a rental "
                        "fee, so it needs an equipment classification.",
                        product=template.display_name,
                    )
                )
