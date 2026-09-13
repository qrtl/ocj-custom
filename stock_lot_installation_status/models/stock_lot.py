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

    def _installation_status_dates(self, status, vals):
        # Stamp the dates the caller is not already setting itself, so that a
        # manually provided date always wins over the automatic one.
        now = fields.Datetime.now()
        res = {}
        if "installation_status_change_date" not in vals:
            res["installation_status_change_date"] = now
        if status == "installed" and "installation_completed_date" not in vals:
            res["installation_completed_date"] = now
        return res

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            status = vals.get("installation_status")
            if status:
                vals = {**vals, **self._installation_status_dates(status, vals)}
            new_vals_list.append(vals)
        return super().create(new_vals_list)

    def write(self, vals):
        if "installation_status" not in vals:
            return super().write(vals)
        status = vals["installation_status"]
        # Only an actual transition may refresh the dates: re-writing the
        # status a lot already carries (mass update, repeated import) must not
        # overwrite the historical installation date.
        changed = self.filtered(lambda lot: lot.installation_status != status)
        res = True
        unchanged = self - changed
        if unchanged:
            res = super(StockLot, unchanged).write(vals)
        if changed:
            res = super(StockLot, changed).write(
                {**vals, **self._installation_status_dates(status, vals)}
            )
        return res
