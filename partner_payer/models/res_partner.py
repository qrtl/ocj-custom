# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    payer_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Payer",
        index="btree_not_null",
        help="Contact that settles the invoices of this customer, when payment "
        "comes from another entity: the head office of a group paying for its "
        "members, for instance. Leave it empty when the customer pays its own "
        "invoices. The invoices are still issued to, and accounted for, this "
        "customer; only the money arrives from the payer.",
    )

    @api.constrains("payer_partner_id")
    def _check_payer_partner_id(self):
        for partner in self:
            payer = partner.payer_partner_id
            if not payer:
                continue
            if payer == partner:
                raise ValidationError(
                    self.env._("%(name)s cannot be its own payer.", name=partner.name)
                )
            # A payer that is itself paid for by someone else would make the
            # group ambiguous: the money of the outer payer would have to reach
            # the invoices of a customer it never appears on. One level is what
            # the reconciliation resolves, so one level is what is allowed.
            if payer.payer_partner_id:
                raise ValidationError(
                    self.env._(
                        "%(payer)s is paid for by %(outer)s, so it cannot be the "
                        "payer of %(name)s. Point both customers at the same payer "
                        "instead.",
                        payer=payer.name,
                        outer=payer.payer_partner_id.name,
                        name=partner.name,
                    )
                )
            # Same reason seen from the other side: a contact others already
            # point at as their payer cannot start being paid for itself.
            if self.search_count([("payer_partner_id", "=", partner.id)], limit=1):
                raise ValidationError(
                    self.env._(
                        "%(name)s is the payer of other customers, so it cannot "
                        "be paid for by %(payer)s.",
                        name=partner.name,
                        payer=payer.name,
                    )
                )

    def _get_paid_for_partner_ids(self):
        """Return this contact and every contact it settles the invoices of.

        The result is the set of contacts whose open items a payment from this
        contact may be looking to settle.
        """
        self.ensure_one()
        paid_for = self.search([("payer_partner_id", "=", self.id)])
        return (self | paid_for).ids
