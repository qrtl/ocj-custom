# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        # Inherited fields reach the template one write per field, so the
        # classification constraint would see the kind before the classification.
        template_vals = {
            fname: vals.pop(fname)
            for fname in ("product_kind", "equipment_classification_id")
            if fname in vals
        }
        if template_vals:
            self.product_tmpl_id.write(template_vals)
        return super().write(vals)
