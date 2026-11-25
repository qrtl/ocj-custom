# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    obc_department_code = fields.Char(
        "OBC Department Code",
        help="Department code in OBC. Income and expense journal items distributed "
        "to this analytic account are exported with it.",
    )
