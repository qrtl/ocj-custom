# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_equipment = fields.Boolean()
    is_consumable = fields.Boolean()
    manufacturer_id = fields.Many2one(
        comodel_name="product.manufacturer",
        string="Manufacturer",
    )
    equipment_classification_id = fields.Many2one(
        comodel_name="product.equipment.classification",
        string="Equipment Classification",
    )
    equipment_classification_sub_id = fields.Many2one(
        comodel_name="product.equipment.classification.sub",
        string="Equipment Sub-Classification",
    )

    @api.constrains("is_equipment", "is_consumable")
    def _check_equipment_consumable_exclusive(self):
        for product in self:
            if product.is_equipment and product.is_consumable:
                raise ValidationError(
                    self.env._(
                        "A product cannot be flagged as both equipment and consumable."
                    )
                )
