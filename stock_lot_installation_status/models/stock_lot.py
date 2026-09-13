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
    first_installation_date = fields.Datetime(
        tracking=True,
        help="Date and time of the first installation. Kept across later "
        "installations; the service life is counted from it.",
    )

    def _installation_status_dates(self, status, vals):
        """Dates to stamp for a transition to ``status``, caller's values kept.

        Per record: first_installation_date depends on this lot. create()
        calls it on the empty recordset, where it reads as unset.
        """
        now = fields.Datetime.now()
        res = {}
        if "installation_status_change_date" not in vals:
            res["installation_status_change_date"] = now
        if status != "installed":
            return res
        completed = vals.get("installation_completed_date", now)
        if "installation_completed_date" not in vals:
            res["installation_completed_date"] = completed
        if "first_installation_date" not in vals and not self.first_installation_date:
            res["first_installation_date"] = completed
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
        res = True
        for lot in self:
            # Only a real transition refreshes the dates, so a re-write of the
            # current status does not overwrite the installation history.
            if lot.installation_status == status:
                res = super(StockLot, lot).write(vals)
            else:
                res = super(StockLot, lot).write(
                    {**vals, **lot._installation_status_dates(status, vals)}
                )
        return res
