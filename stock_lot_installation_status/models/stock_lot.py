# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    installation_status = fields.Selection(
        selection=[
            ("not_installed", "Not Installed"),
            ("installed", "Installed"),
        ],
        default="not_installed",
        tracking=True,
        help="Installation status of this serial/lot number.",
    )
    installation_status_change_date = fields.Datetime(
        readonly=True,
        tracking=True,
        help="Date and time when the installation status was last changed.",
    )
    installation_completed_date = fields.Datetime(
        string="Installation Completion Date",
        readonly=True,
        tracking=True,
        help="Date and time when the installation status was changed to Installed.",
    )

    def _apply_installation_status_dates(self, vals):
        # Only auto-populate the date fields when the caller is not already
        # editing them in the same call (manual edits take priority).
        now = fields.Datetime.now()
        if "installation_status_change_date" not in vals:
            vals["installation_status_change_date"] = now
        if (
            vals["installation_status"] == "installed"
            and "installation_completed_date" not in vals
        ):
            vals["installation_completed_date"] = now

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "installation_status" in vals:
                self._apply_installation_status_dates(vals)
        return super().create(vals_list)

    def write(self, vals):
        if "installation_status" in vals:
            self._apply_installation_status_dates(vals)
        return super().write(vals)
