# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


# The component side of the set relation. It lives on the variant because that
# is the record a combination names: serials, stock lines and the equipment-
# model interface all carry the variant, so a set built from anything else
# would need a hop to be compared with what a caller sends.
class ProductProduct(models.Model):
    _inherit = "product.product"

    rental_set_fee_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_rental_set_component_rel",
        column1="component_product_id",
        column2="fee_product_tmpl_id",
        string="Rental Fee Sets",
        help="Rental fee products that bill this variant as part of a set.",
    )
