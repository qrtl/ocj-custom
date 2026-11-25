# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    obc_export_excluded = fields.Boolean(
        "Exclude from OBC Export",
        help="Journal entries of this journal are never exported to OBC.",
    )
    obc_aggregation = fields.Selection(
        selection=[("day", "Per Day"), ("month", "Per Month")],
        string="OBC Aggregation",
        default="day",
        required=True,
        help="Journal items are summed into one OBC entry per day, or into one "
        "entry dated the last day of the month.",
    )
