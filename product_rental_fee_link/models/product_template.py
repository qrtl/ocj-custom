# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_fee_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_rental_fee_rel",
        column1="equipment_tmpl_id",
        column2="rental_fee_product_tmpl_id",
        string="Rental Fee Products",
        domain=[("type", "=", "service")],
        help="Service products used to bill the rental of this equipment or "
        "accessory - e.g. a base fee and a separate fee for a specific "
        "accessory bundle. Used in the Navi in Flow integration.",
    )
    equipment_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_rental_fee_rel",
        column1="rental_fee_product_tmpl_id",
        column2="equipment_tmpl_id",
        string="Billed Equipment",
        domain=[("product_kind", "in", ("equipment", "accessory"))],
        help="Equipment or accessory products whose rental this service bills.",
    )

    @api.constrains("rental_fee_product_tmpl_ids")
    def _check_rental_fee_product_tmpl_ids(self):
        # The product type is the discriminator here; is_storable is deliberately
        # not checked, as it only means "track inventory" and can be turned on by
        # a user default even for services (core clears it on recompute anyway).
        for template in self.filtered("rental_fee_product_tmpl_ids"):
            if template in template.rental_fee_product_tmpl_ids:
                raise ValidationError(
                    self.env._("A product cannot be its own rental fee product.")
                )
            non_service = template.rental_fee_product_tmpl_ids.filtered(
                lambda p: p.type != "service"
            )
            if non_service:
                raise ValidationError(
                    self.env._(
                        "The rental fee product must be a service, but "
                        "%(product)s is not.",
                        product=non_service[0].display_name,
                    )
                )

    @api.constrains("equipment_tmpl_ids")
    def _check_equipment_tmpl_ids(self):
        for template in self.filtered("equipment_tmpl_ids"):
            if template in template.equipment_tmpl_ids:
                raise ValidationError(
                    self.env._("A product cannot be its own billed equipment.")
                )
            wrong_kind = template.equipment_tmpl_ids.filtered(
                lambda p: p.product_kind not in ("equipment", "accessory")
            )
            if wrong_kind:
                raise ValidationError(
                    self.env._(
                        "%(product)s is neither equipment nor an accessory, so "
                        "a rental fee product cannot bill it.",
                        product=wrong_kind[0].display_name,
                    )
                )
