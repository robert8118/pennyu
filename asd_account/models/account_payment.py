# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    inv_categ = fields.Selection([
        ('cod', 'COD'),
        ('tempo', 'Tempo'),
    ], string='Invoice Category')

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        res = super(AccountPayment, self)._get_move_vals()
        res.update({
                'inv_categ': self.inv_categ,
            })
        return res