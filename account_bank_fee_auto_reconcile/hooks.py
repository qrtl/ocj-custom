# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .models.account_reconcile_model import FEE_MODEL_XML_ID_PREFIX


def post_init_hook(env):
    """Recompute can_be_proposed on the fee models that already exist.

    A stored compute is not replayed on install, and a fee model created
    together with its XMLID was computed before that XMLID existed, so the
    models already in the database have to be refreshed once.
    """
    module, _, name_prefix = FEE_MODEL_XML_ID_PREFIX.partition(".")
    data = env["ir.model.data"].search(
        [
            ("module", "=", module),
            ("name", "=like", f"{name_prefix}%"),
            ("model", "=", "account.reconcile.model"),
        ]
    )
    models = env["account.reconcile.model"].browse(data.mapped("res_id")).exists()
    if models:
        env.add_to_compute(models._fields["can_be_proposed"], models)
        models.flush_recordset(["can_be_proposed"])
