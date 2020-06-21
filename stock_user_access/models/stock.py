from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    user_ids = fields.Many2many(
        'res.users', 'rel_warehouse_user', 'user_id', 'warehouse_id', string='Allowed Users')
