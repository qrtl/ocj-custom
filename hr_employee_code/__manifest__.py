# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR Employee Code",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "website": "https://www.quartile.co",
    "author": "Quartile",
    "maintainers": ["smorita7749"],
    "license": "LGPL-3",
    "summary": "Add a unique employee code field for external system matching",
    "installable": True,
    "depends": ["hr"],
    "data": [
        "views/hr_employee_views.xml",
    ],
}
