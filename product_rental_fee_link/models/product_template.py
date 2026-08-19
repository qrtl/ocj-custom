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
    rental_fee_for_product_tmpl_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="rental_fee_product_tmpl_id",
        string="Rental Fee For",
        help="Equipment products whose rental this product bills. The inverse "
        "of Rental Fee Product, so a fee product can be read from the equipment "
        "that points at it instead of the link being followed one way only.",
    )
    rented_equipment_classification_id = fields.Many2one(
        comodel_name="product.equipment.classification",
        string="Rented Equipment Classification",
        compute="_compute_rented_equipment_classification_id",
        store=True,
        help="Classification of the equipment this rental fee bills, taken from "
        "the equipment itself so it does not have to be entered twice. Empty "
        "unless the equipment pointing at this product agree on one "
        "classification, since there is then no single value to report.",
    )

    # Stored, so it can be searched: an integration selecting fee products needs
    # this in a domain. The dotted dependency is deliberate here - the value
    # mirrors the equipment and has to follow it, unlike a field merely
    # defaulted from a parent.
    @api.depends(
        "rental_fee_for_product_tmpl_ids",
        "rental_fee_for_product_tmpl_ids.equipment_classification_id",
    )
    def _compute_rented_equipment_classification_id(self):
        for template in self:
            classifications = (
                template.rental_fee_for_product_tmpl_ids.equipment_classification_id
            )
            template.rented_equipment_classification_id = (
                classifications if len(classifications) == 1 else False
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
