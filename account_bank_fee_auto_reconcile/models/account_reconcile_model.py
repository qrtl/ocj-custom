# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models

# Odoo names the model it creates for a journal's fees after this prefix, and
# recognises it by that name again when it looks for a fee model to apply.
FEE_MODEL_XML_ID_PREFIX = "account.account_reco_model_fee_"


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    @api.depends("trigger")
    def _compute_can_be_proposed(self):
        res = super()._compute_can_be_proposed()
        # A fee model reaches the transactions through a dedicated route that
        # only fires when what is left to allocate is small compared to the
        # amount received. Keeping it out of can_be_proposed is what confines it
        # to that route: as a proposable model it carries no matching condition
        # of its own, so a transaction that could not be matched to an invoice
        # would have its whole amount written off to the fee account.
        for model in self._get_bank_fee_models():
            model.can_be_proposed = False
        return res

    def _get_bank_fee_models(self):
        """Return the records among self that a journal uses for its bank fees."""
        records = self.filtered(lambda model: isinstance(model.id, int))
        if not records:
            return records
        external_ids = records._get_external_ids()
        return records.filtered(
            lambda model: any(
                xml_id.startswith(FEE_MODEL_XML_ID_PREFIX)
                for xml_id in external_ids.get(model.id, [])
            )
        )
