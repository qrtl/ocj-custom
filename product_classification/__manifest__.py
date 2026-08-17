# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Product Classification",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["yostashiro"],
    "license": "LGPL-3",
    "summary": "Classify products (equipment / consumable) with manufacturer "
    "and classification master data",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/product_equipment_classification_data.xml",
        "views/product_equipment_classification_views.xml",
        "views/product_middle_category_views.xml",
        "views/product_minor_category_views.xml",
        "views/product_manufacturer_views.xml",
        "views/product_template_views.xml",
    ],
}
