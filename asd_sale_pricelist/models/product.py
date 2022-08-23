from re import template
from odoo import fields, _, api, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    min_amount = fields.Float('Min. Amount')