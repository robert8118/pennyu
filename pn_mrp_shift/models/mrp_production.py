from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mo_shift = fields.Many2one('mrp.shift', 'Shift')
