# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Where earlier versions kept the relation, newest first, as a query returning
# (fee template, component template) pairs. Only the first one present is read:
# each replaced the one after it, so an older source left on the database
# holds what was already carried over, or no longer meant.
SOURCES = [
    # The set, held on variants.
    (
        "product_template_rental_set_component_rel",
        "SELECT rel.fee_product_tmpl_id, pp.product_tmpl_id "
        "FROM product_template_rental_set_component_rel rel "
        "JOIN product_product pp ON pp.id = rel.component_product_id",
    ),
    # The many2many link from fee to equipment.
    (
        "product_template_rental_fee_rel",
        "SELECT rental_fee_product_tmpl_id, equipment_tmpl_id "
        "FROM product_template_rental_fee_rel",
    ),
    # The many2one link on the equipment.
    (
        None,
        "SELECT rental_fee_product_tmpl_id, id FROM product_template "
        "WHERE rental_fee_product_tmpl_id IS NOT NULL",
    ),
]


def _table_exists(cr, table):
    cr.execute("SELECT to_regclass(%s)", [table])
    return bool(cr.fetchone()[0])


def _column_exists(cr, table, column):
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s",
        [table, column],
    )
    return bool(cr.fetchone())


def _read_pairs(cr):
    for table, query in SOURCES:
        if table and not _table_exists(cr, table):
            continue
        if not table and not _column_exists(
            cr, "product_template", "rental_fee_product_tmpl_id"
        ):
            continue
        cr.execute(query)
        return cr.fetchall()
    return []


def migrate(cr, version):
    """Carry the sets over to template components, then drop the old tables.

    A set read from variants becomes the set of their products; a link from an
    earlier version becomes a set of the equipment it linked. The key is
    rebuilt for every product, since one stored from variant ids names other
    records. A row the constraints refuse is named in the log rather than
    guessed at, and the fee product simply has no set until someone enters one.
    """
    if not version:
        return
    pairs = _read_pairs(cr)
    cr.execute(
        "UPDATE product_template SET rental_set_key = NULL "
        "WHERE rental_set_key IS NOT NULL"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    Template = env["product.template"].with_context(active_test=False)
    env.invalidate_all()
    components_by_fee = {}
    for fee_id, component_id in pairs:
        components_by_fee.setdefault(fee_id, set()).add(component_id)
    converted = 0
    for fee_id, component_ids in components_by_fee.items():
        fee = Template.browse(fee_id).exists()
        components = Template.browse(list(component_ids)).exists()
        if not fee or not components:
            continue
        try:
            # A savepoint per row, flushed inside it: a row the constraints
            # refuse must cost only itself, not the rows already converted.
            with cr.savepoint():
                fee.rental_set_component_ids = components
                env.flush_all()
            converted += 1
        except Exception as error:  # noqa: BLE001 - a bad row must not stop the upgrade
            env.invalidate_all()
            _logger.warning("%s: not converted (%s)", fee.display_name, error)
    cr.execute("DROP TABLE IF EXISTS product_template_rental_set_component_rel")
    cr.execute("DROP TABLE IF EXISTS product_template_rental_fee_rel")
    _logger.info("Converted %s rental sets to product components", converted)
