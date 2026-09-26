# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# What a rental fee set may contain. Consumables are billed on their own, so
# they are not part of the combination a set is identified by.
RENTAL_SET_COMPONENT_KINDS = ("equipment", "accessory")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # The components are variants, not templates: what an external system holds
    # and asks with is the id delivered by the equipment-model interface, which
    # is a `product.product`. Storing the set at that granularity means the
    # incoming combination and the stored one are the same kind of value, with
    # no template hop that could be wrong without anyone seeing it.
    rental_set_component_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_template_rental_set_component_rel",
        column1="fee_product_tmpl_id",
        column2="component_product_id",
        string="Set Components",
        domain=[("product_kind", "in", RENTAL_SET_COMPONENT_KINDS)],
        help="Equipment and accessories this rental fee product bills as one "
        "set - e.g. a concentrator together with a demand valve and a flow "
        "meter. The combination is exact: a lookup returns this product only "
        "when it asks for these components and no others.",
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
        compute="_compute_rental_set_fee_tmpl_ids",
        string="Rental Fee Sets",
        help="Rental fee products whose set contains this product. The link "
        "itself is held on the variant, since that is what a lookup asks "
        "about; this gathers the sets of every variant of the product.",
    )

    @api.depends("rental_set_component_ids")
    def _compute_rental_set_key(self):
        for template in self:
            template.rental_set_key = self._rental_set_key(
                template.rental_set_component_ids.ids
            )

    def _compute_rental_set_fee_tmpl_ids(self):
        for template in self:
            template.rental_set_fee_tmpl_ids = (
                template.product_variant_ids.rental_set_fee_tmpl_ids
            )

    @api.model
    def _rental_set_key(self, product_ids):
        """Return the stored key for a combination of component ids, or False.

        Order and repetition carry no meaning - a set is what it contains - so
        both are normalized away. A caller's combination goes through this same
        method, which is what keeps the two sides from disagreeing about what
        "the same set" is.
        """
        unique_ids = sorted(set(product_ids))
        return ",".join(str(product_id) for product_id in unique_ids) or False

    @api.model
    def _find_by_rental_set(self, product_ids):
        """Return the rental fee products billing exactly `product_ids`.

        Exact, not "contains": what to charge when only part of a set is
        installed is a billing decision, and nothing on the product says it -
        so the caller asks about each combination it wants priced. An empty
        combination matches nothing, rather than every product that happens to
        have no components.
        """
        key = self._rental_set_key(product_ids)
        if not key:
            return self.browse()
        return self.search([("rental_set_key", "=", key)])

    @api.constrains("rental_set_component_ids", "type")
    def _check_rental_set_owner(self):
        # The type is the discriminator here, as it is for the fee link above:
        # a rental fee is a service, while 品目区分 is still being filled in on
        # the fee products and cannot yet be relied on to select them.
        for template in self.filtered("rental_set_component_ids"):
            if template.type != "service":
                raise ValidationError(
                    self.env._(
                        "%(product)s is not a service, so it cannot bill a set "
                        "of equipment.",
                        product=template.display_name,
                    )
                )

    @api.constrains("rental_set_component_ids")
    def _check_rental_set_component_ids(self):
        for template in self.filtered("rental_set_component_ids"):
            components = template.rental_set_component_ids
            if template in components.product_tmpl_id:
                raise ValidationError(
                    self.env._("A product cannot be a component of its own set.")
                )
            wrong_kind = components.filtered(
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

    @api.constrains("rental_set_component_ids")
    def _check_rental_set_key_unique(self):
        """Keep a combination the name of at most one rental fee product.

        The lookup answers with whatever carries the key, so two products
        sharing one would make the answer depend on search order. Archived
        products stay out of it: `search` skips them here exactly as it does at
        lookup time, so a retired set never blocks the one replacing it.
        """
        for template in self.filtered("rental_set_key"):
            duplicate = self.search(
                [
                    ("rental_set_key", "=", template.rental_set_key),
                    ("id", "!=", template.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    self.env._(
                        "%(product)s already bills this set of equipment. A "
                        "combination identifies one rental fee product.",
                        product=duplicate.display_name,
                    )
                )
