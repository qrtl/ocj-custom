# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    obc_export_id = fields.Many2one(
        "account.move.obc.export",
        string="OBC Export",
        copy=False,
        readonly=True,
        index="btree_not_null",
        ondelete="set null",
    )

    def button_draft(self):
        exported = self.filtered("obc_export_id")
        if exported:
            raise UserError(
                self.env._(
                    "Following records have been exported to OBC and cannot be "
                    "reset to draft. Delete the OBC export first.\n%(names)s",
                    names="\n".join(exported.mapped("display_name")),
                )
            )
        return super().button_draft()
