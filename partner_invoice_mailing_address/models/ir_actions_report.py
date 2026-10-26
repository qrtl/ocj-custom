# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_invoice_mailing_address(self, record):
        if (record._name == "account.move" and record.is_sale_document()) or (
            record._name == "account.billing" and record.bill_type == "out_invoice"
        ):
            return self._get_report_partner(record).invoice_mailing_address
        return False
