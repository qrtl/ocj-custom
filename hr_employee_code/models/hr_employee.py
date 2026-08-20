# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_code = fields.Char(copy=False)

    _employee_code_uniq = models.Constraint(
        "unique (employee_code)", "The employee code must be unique."
    )
