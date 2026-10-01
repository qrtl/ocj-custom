# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_TABLE = "product_template_rental_fee_rel"


def migrate(cr, version):
    """Carry the equipment link over to the set, then drop it.

    The link said a service *may* bill an equipment; the set says what it
    bills and nothing else. A link is therefore a set of one, which is what
    every row on the instance holds anyway - the many2many's extra reach was
    never used. A row that cannot be read that way is left behind rather than
    guessed at: it is named in the log, and the fee product simply has no set
    until someone enters one.
    """
    if not version:
        return
    cr.execute("SELECT to_regclass(%s)", [OLD_TABLE])
    if not cr.fetchone()[0]:
        return
    cr.execute(
        "SELECT rental_fee_product_tmpl_id, equipment_tmpl_id "
        "FROM product_template_rental_fee_rel"
    )
    pairs = cr.fetchall()
    env = api.Environment(cr, SUPERUSER_ID, {})
    Template = env["product.template"]
    components_by_fee = {}
    for fee_id, equipment_id in pairs:
        components_by_fee.setdefault(fee_id, []).append(equipment_id)
    for fee_id, equipment_ids in components_by_fee.items():
        fee = Template.browse(fee_id).exists()
        equipment = Template.browse(equipment_ids).exists()
        if not fee or not equipment:
            continue
        if fee.rental_set_component_ids:
            continue
        # A template with several variants does not say which one the set
        # contains, and the link never had to: it pointed at the template.
        ambiguous = equipment.filtered(lambda x: len(x.product_variant_ids) != 1)
        if ambiguous:
            _logger.warning(
                "%s: not converted, %s has no single variant to put in the set",
                fee.display_name,
                ambiguous[0].display_name,
            )
            continue
        components = equipment.product_variant_id
        key = Template._rental_set_key(components.ids)
        taken = Template.search([("rental_set_key", "=", key)], limit=1)
        if taken:
            _logger.warning(
                "%s: not converted, %s already bills that set",
                fee.display_name,
                taken.display_name,
            )
            continue
        try:
            # A savepoint per row, flushed inside it: a row the constraints
            # refuse must cost only itself, not the rows already converted.
            with cr.savepoint():
                fee.rental_set_component_ids = components
                env.flush_all()
        except Exception as error:  # noqa: BLE001 - a bad row must not stop the upgrade
            env.invalidate_all()
            _logger.warning("%s: not converted (%s)", fee.display_name, error)
    cr.execute("DROP TABLE IF EXISTS product_template_rental_fee_rel")
    _logger.info(
        "Converted %s equipment links into rental sets", len(components_by_fee)
    )
