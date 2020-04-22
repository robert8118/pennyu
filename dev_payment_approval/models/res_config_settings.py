# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
    
    payment_double_verify = fields.Boolean(string="Second Approval", default=lambda self: self.env.user.company_id.payment_double_validation == 'two_step')
    payment_double_validation = fields.Selection(related='company_id.payment_double_validation', string="Levels of Approvals *")
    payment_double_validation_amount = fields.Monetary(related='company_id.payment_double_validation_amount', string="Minimum Amount", currency_field='company_currency_id')
    
    
    payment_triple_verify = fields.Boolean(string="Third Approval", default=lambda self: self.env.user.company_id.payment_triple_validation == 'three_step')
    payment_triple_validation = fields.Selection(related='company_id.payment_triple_validation', string="Levels of Approvals *")
    payment_triple_validation_amount = fields.Monetary(related='company_id.payment_triple_validation_amount', string="Minimum Amount", currency_field='company_currency_id')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.payment_double_validation = 'two_step' if self.payment_double_verify else 'one_step'
        self.payment_triple_validation = 'three_step' if self.payment_triple_verify else 'two_step'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
