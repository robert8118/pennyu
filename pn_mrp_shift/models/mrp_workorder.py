from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    mo_shift = fields.Char('Shift', related='production_id.mo_shift.name', readonly=True)
