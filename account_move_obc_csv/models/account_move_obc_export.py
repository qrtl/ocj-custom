# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveObcExport(models.Model):
    _name = "account.move.obc.export"
    _description = "OBC Export"
    _order = "date_to desc, id desc"
    _check_company_auto = True

    name = fields.Char(readonly=True, copy=False, default="/")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    date_from = fields.Date(
        required=True, default=lambda self: self._default_dates()[0]
    )
    date_to = fields.Date(required=True, default=lambda self: self._default_dates()[1])
    move_ids = fields.One2many(
        "account.move", "obc_export_id", string="Journal Entries", readonly=True
    )
    move_count = fields.Integer(compute="_compute_move_count")

    _date_check = models.Constraint(
        "CHECK(date_from <= date_to)",
        "The start date must not be later than the end date.",
    )

    @api.model
    def _default_dates(self):
        """Return the first and last day of the previous month."""
        date_to = fields.Date.context_today(self).replace(day=1) - timedelta(days=1)
        return date_to.replace(day=1), date_to

    @api.depends("move_ids")
    def _compute_move_count(self):
        for export in self:
            export.move_count = len(export.move_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("account.move.obc.export")
                    or "/"
                )
        return super().create(vals_list)

    def action_export(self):
        """Take the journal entries of the period, once, and download the CSV."""
        self.ensure_one()
        if not self.move_ids:
            moves = self.env["account.move"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "posted"),
                    ("date", ">=", self.date_from),
                    ("date", "<=", self.date_to),
                    ("journal_id.obc_export_excluded", "=", False),
                    ("obc_export_id", "=", False),
                ]
            )
            if not moves:
                raise UserError(
                    self.env._("There is no journal entry to export in the period.")
                )
            moves.obc_export_id = self
        report = self.env.ref("account_move_obc_csv.report_obc_csv")
        return report.report_action(self, config=False)

    def action_view_moves(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_journal_line"
        )
        action["domain"] = [("obc_export_id", "=", self.id)]
        action["context"] = {}
        return action
