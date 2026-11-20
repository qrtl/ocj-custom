# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


def migrate(cr, version):
    """Turn prorated billing on for the partners that predate the default.

    Proration became the rule (on by default); a value saved before that is
    the old default, not a decision that the customer is billed in full. The
    two month settings are new columns and already take their default.
    """
    cr.execute(
        "UPDATE res_partner SET prorated_billing = TRUE "
        "WHERE prorated_billing IS NOT TRUE"
    )
