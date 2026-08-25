# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    equipment_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Billed Equipment",
        domain="[('product_kind', 'in', ('equipment', 'accessory'))]",
        help="The equipment or accessory this rental fee bills. An equipment "
        "or accessory may have several rental fee products - e.g. a base fee "
        "and a fee for a specific accessory bundle - so this link is what "
        "ties a fee back to what it is charged for.",
    )
    rental_fee_product_tmpl_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="equipment_tmpl_id",
        string="Rental Fee Products",
        help="Service products used to bill the rental of this equipment or "
        "accessory. Used in the Navi in Flow integration.",
    )

    @api.constrains("equipment_tmpl_id", "type")
    def _check_equipment_tmpl_id(self):
        # The product type is the discriminator here; is_storable is deliberately
        # not checked, as it only means "track inventory" and can be turned on by
        # a user default even for services (core clears it on recompute anyway).
        for template in self.filtered("equipment_tmpl_id"):
            if template.equipment_tmpl_id == template:
                raise ValidationError(
                    self.env._("A product cannot be its own billed equipment.")
                )
            if template.type != "service":
                raise ValidationError(
                    self.env._(
                        "%(product)s bills the rental of an equipment or "
                        "accessory, so it must be a service.",
                        product=template.display_name,
                    )
                )
