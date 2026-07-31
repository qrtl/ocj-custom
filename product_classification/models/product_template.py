# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


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
    equipment_classification_sub_id = fields.Many2one(
        comodel_name="product.equipment.classification.sub",
        string="Equipment Sub-Classification",
        help="Sub-classification for auxiliary equipment or accessories. "
        "Used in the Navi in Flow integration.",
    )
    consumable_classification_id = fields.Many2one(
        comodel_name="product.consumable.classification",
        string="Consumable Classification",
        help="Classification of a consumable product.",
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
