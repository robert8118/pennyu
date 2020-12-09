from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many('stock.warehouse', 'rel_warehouse_user', 'warehouse_id', 'user_id',
                                     string='Allowed Warehouses')
    work_center_ids = fields.Many2many('mrp.workcenter', string='Allowed Work Center')
