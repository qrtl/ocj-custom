# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Location Tracking Restriction",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["kanda999"],
    "license": "LGPL-3",
    "summary": "Limit the products a location accepts to serial- or lot-tracked ones",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/stock_location_views.xml",
    ],
}
