# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_fee_product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Rental Fee Product",
        domain=[("type", "=", "service")],
        help="Service product used to bill the rental of this equipment. The "
        "rental fee is managed as a product separate from the equipment itself, "
        "so this link is what ties the two together - e.g. to derive the product "
        "codes to send to an external system from the variants of the rental fee "
        "product.",
    )

    @api.constrains("rental_fee_product_tmpl_id", "type")
    def _check_rental_fee_product_tmpl_id(self):
        # The product type is the discriminator here; is_storable is deliberately
        # not checked, as it only means "track inventory" and can be turned on by
        # a user default even for services (core clears it on recompute anyway).
        for template in self.filtered("rental_fee_product_tmpl_id"):
            fee_product = template.rental_fee_product_tmpl_id
            if fee_product == template:
                raise ValidationError(
                    self.env._("A product cannot be its own rental fee product.")
                )
            if fee_product.type != "service":
                raise ValidationError(
                    self.env._(
                        "The rental fee product must be a service, but "
                        "%(product)s is not.",
                        product=fee_product.display_name,
                    )
                )
