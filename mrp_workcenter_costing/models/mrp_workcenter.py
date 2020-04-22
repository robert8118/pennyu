# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    costs_man_hour = fields.Float(string='Labour Rate per hour', default="0.0")
    costs_man_account_credit = fields.Many2one('account.account', string="Credit Account")
    costs_man_account_debit = fields.Many2one('account.account', string="Debit Account")

    costs_electricity_hour = fields.Float(string='Electricity Rate per hour', default="0.0")
    costs_electricity_account_credit = fields.Many2one('account.account', string="Credit Account")
    costs_electricity_account_debit = fields.Many2one('account.account', string="Debit Account")

    costs_gas_hour = fields.Float(string='Gas Rate per hour', default="0.0")
    costs_gas_account_credit = fields.Many2one('account.account', string="Credit Account")
    costs_gas_account_debit = fields.Many2one('account.account', string="Debit Account")

    costs_other_hour = fields.Float(string='Other Rate per hour', default="0.0")
    costs_other_account_credit = fields.Many2one('account.account', string="Credit Account")
    costs_other_account_debit = fields.Many2one('account.account', string="Debit Account")


    company_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.id) 
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id) 




