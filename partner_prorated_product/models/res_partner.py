# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # The equipment is the second axis of the rule: proration is agreed per
    # customer and per piece of equipment, so one customer can be prorated on
    # a ventilator and billed in full on a concentrator. Left empty, the
    # customer's prorated billing applies to everything they rent.
    prorated_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="res_partner_prorated_product_tmpl_rel",
        column1="partner_id",
        column2="product_tmpl_id",
        string="Prorated Equipment",
        domain=[("product_kind", "=", "equipment")],
        help="The equipment this customer is billed pro rata for. Empty means "
        "every rental, once prorated billing is on.",
    )

    @api.model
    def _commercial_fields(self):
        # The list qualifies the company's prorated billing, so it follows the
        # switch down to the company's contacts.
        return super()._commercial_fields() + ["prorated_product_tmpl_ids"]

    def _is_prorated_for_equipment(self, equipment):
        """Whether renting `equipment` to this customer is billed pro rata.

        `equipment` is the product templates a rental fee charges for: one
        for a single piece of equipment, several for a set, none for a fee
        that bills no equipment. A set is prorated when any of its equipment
        is, since the fee is one line and cannot be split.
        """
        self.ensure_one()
        if not self.prorated_billing:
            return False
        if not self.prorated_product_tmpl_ids:
            return True
        return bool(equipment & self.prorated_product_tmpl_ids)
