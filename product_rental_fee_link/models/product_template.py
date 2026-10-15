# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# What a rental fee set may contain. Consumables are billed on their own, so
# they are not part of the combination a set is identified by.
RENTAL_SET_COMPONENT_KINDS = ("equipment", "accessory")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # The components are templates: equipment and accessories are maintained,
    # imported and referred to by their product, and a variant says nothing
    # about which set it belongs to that its product does not.
    rental_set_component_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_rental_set_rel",
        column1="fee_product_tmpl_id",
        column2="component_tmpl_id",
        string="Set Components",
        # Archiving a member does not change what the set bills. The kinds are
        # limited in the form and the constraint, not by a field domain, which
        # would hide a reclassified member from the set instead of refusing it.
        context={"active_test": False},
        help="Equipment and accessories this rental fee product bills as one "
        "set - e.g. a concentrator together with a demand valve and a flow "
        "meter.",
    )
    rental_set_key = fields.Char(
        compute="_compute_rental_set_key",
        store=True,
        index=True,
        string="Set Key",
        help="The components as an order-independent key. It is what turns "
        "looking up a combination into an indexed equality search.",
    )
    rental_set_fee_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_rental_set_rel",
        column1="component_tmpl_id",
        column2="fee_product_tmpl_id",
        string="Rental Fee Sets",
        help="Rental fee products whose set contains this product.",
    )

    @api.depends("rental_set_component_ids")
    def _compute_rental_set_key(self):
        for template in self:
            template.rental_set_key = self._rental_set_key(
                template.rental_set_component_ids.ids
            )

    def unlink(self):
        # Deleting a member drops its relation rows in SQL, which recomputes
        # nothing: the fees' keys must follow by hand.
        fees = self.with_context(active_test=False).rental_set_fee_tmpl_ids - self
        res = super().unlink()
        fees.modified(["rental_set_component_ids"])
        return res

    @api.model
    def _rental_set_key(self, product_tmpl_ids):
        """Return the stored key for a combination of component ids, or False.

        Order and repetition carry no meaning - a set is what it contains - so
        both are normalized away. A caller's combination goes through this same
        method, which is what keeps the two sides from disagreeing about what
        "the same set" is.
        """
        unique_ids = sorted(set(product_tmpl_ids))
        return ",".join(str(tmpl_id) for tmpl_id in unique_ids) or False

    @api.model
    def _find_by_rental_set(self, product_tmpl_ids):
        """Return the rental fee products billing exactly `product_tmpl_ids`.

        An empty combination matches nothing, rather than every product that
        happens to have no components. Several products may bill the same
        combination (a second-unit fee, say), and all of them are returned.
        """
        key = self._rental_set_key(product_tmpl_ids)
        if not key:
            return self.browse()
        return self.search([("rental_set_key", "=", key)])

    @api.model
    def _find_rental_sets_within(self, product_tmpl_ids):
        """Return the rental fee products whose set is part of `product_tmpl_ids`.

        This is what answers a combination no set matches exactly: the sets it
        covers. Which of them to propose is the caller's decision.
        """
        components = self.browse(product_tmpl_ids)
        return self.search(
            [("rental_set_component_ids", "in", components.ids)]
        ).filtered(lambda fee: fee.rental_set_component_ids <= components)

    @api.constrains(
        "rental_set_component_ids", "rental_set_fee_tmpl_ids", "product_kind"
    )
    def _check_rental_set_component_ids(self):
        # A set is checked from either side: a member's kind or membership can
        # change without the fee being written.
        templates = self.with_context(active_test=False)
        fees = templates | templates.rental_set_fee_tmpl_ids
        for template in fees.filtered("rental_set_component_ids"):
            if template.product_kind != "rental_fee":
                raise ValidationError(
                    self.env._(
                        "%(product)s is not a rental fee, so it cannot bill a set "
                        "of equipment.",
                        product=template.display_name,
                    )
                )
            wrong_kind = template.rental_set_component_ids.filtered(
                lambda p: p.product_kind not in RENTAL_SET_COMPONENT_KINDS
            )
            if wrong_kind:
                raise ValidationError(
                    self.env._(
                        "%(product)s is neither equipment nor an accessory, so "
                        "a rental fee set cannot contain it.",
                        product=wrong_kind[0].display_name,
                    )
                )
