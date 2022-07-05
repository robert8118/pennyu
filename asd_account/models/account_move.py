from shutil import move
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    inv_categ = fields.Selection([
        ('cod', 'COD'),
        ('tempo', 'Tempo'),
    ], string='Invoice Category')