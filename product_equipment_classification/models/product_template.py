# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    equipment_classification_id = fields.Many2one(
        comodel_name="product.equipment.classification",
        string="Equipment Classification",
    )
    equipment_classification_sub_id = fields.Many2one(
        comodel_name="product.equipment.classification.sub",
        string="Equipment Sub-Classification",
    )
