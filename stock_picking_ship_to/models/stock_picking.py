# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ship_to_name = fields.Char(
        string="Ship-to Name",
        compute="_compute_ship_to",
        store=True,
        readonly=False,
    )
    ship_to_address = fields.Char(
        string="Ship-to Address",
        compute="_compute_ship_to",
        store=True,
        readonly=False,
        help="The whole address on one line.",
    )
    ship_to_phone = fields.Char(
        string="Ship-to Phone",
        compute="_compute_ship_to",
        store=True,
        readonly=False,
    )

    @api.model
    def _ship_to_address(self, partner):
        parts = (partner.state_id.name, partner.city, partner.street, partner.street2)
        return "".join(part for part in parts if part) or False

    @api.depends("partner_id")
    def _compute_ship_to(self):
        for picking in self:
            partner = picking.partner_id
            # A nameless address would show its type label ("Company, Delivery").
            picking.ship_to_name = (
                partner.display_name
                if partner.name
                else partner.commercial_partner_id.name
            ) or False
            picking.ship_to_address = picking._ship_to_address(partner)
            picking.ship_to_phone = partner.phone or False
