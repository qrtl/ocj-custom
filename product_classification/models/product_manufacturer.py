# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductManufacturer(models.Model):
    _name = "product.manufacturer"
    _description = "Product Manufacturer"
    _order = "sequence, code, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        help="External code used for integration. A numeric code is preferred."
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        "unique(code)",
        "The code of a manufacturer must be unique.",
    )
