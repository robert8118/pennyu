# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    payment_double_validation = fields.Selection([
        ('one_step', 'Confirm Payments in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a Payment')
        ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for Payments")
    payment_double_validation_amount = fields.Monetary(string='Double validation Amount', default=1000,
        help="Minimum amount for which a double validation is required")
        
    payment_triple_validation = fields.Selection([
        ('two_step', 'Confirm Payments in two step'),
        ('three_step', 'Get 3 levels of approvals to confirm a Payment')
        ], string="Levels of Approvals", default='two_step',
        help="Provide a triple validation mechanism for Payments")
    payment_triple_validation_amount = fields.Monetary(string='Triple validation Amount', default=5000,
        help="Minimum amount for which a triple validation is required")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
