from odoo import api, fields, models


class StockWarehouseExtend(models.Model):
    _inherit = 'stock.warehouse'

    product_categs_to_manufacture = fields.Many2many('product.category', string='Product category(s) to manufacture')
