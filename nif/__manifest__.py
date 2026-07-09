# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Navi in Flow",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Master data and field extensions for the Navi in Flow integration",
    "installable": True,
    "application": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/product_equipment_classification_data.xml",
        "views/nif_menus.xml",
        "views/product_equipment_classification_views.xml",
        "views/product_equipment_classification_sub_views.xml",
        "views/product_manufacturer_views.xml",
        "views/product_template_views.xml",
    ],
}
