# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_sales_receipt(models.Model):
    _name = 'tbl_sales_receipt'
    _inherit = ['mail.thread']

    company_id = fields.Many2one(store=True)
    name = fields.Char(readonly=True, copy=False) # The name is attributed upon post()
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('submit', 'Submit')], readonly=True, default='draft', copy=False, string="Status")


    payment_type = fields.Selection([('inbound', 'Receive Money')], string='Payment Type', required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method", default=1,
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    payment_method_code = fields.Char(related='payment_method_id.code',
        help="Technical field used to adapt the interface to the payment type selected.", readonly=True)

    partner_type = fields.Selection([('customer', 'Customer')])
    partner_id = fields.Many2one('res.partner', string='Partner')

    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    pay_detail = fields.One2many('tbl_msi_pay_detail','pay_details','Invoice Detail')



    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_('The payment amount cannot be negative.'))

    @api.multi
    @api.depends('payment_type', 'journal_id')
    def _compute_hide_payment_method(self):
        for payment in self:
            if not payment.journal_id:
                payment.hide_payment_method = True
                continue
            journal_payment_methods = payment.payment_type == 'inbound'\
                and payment.journal_id.inbound_payment_method_ids\
                or payment.journal_id.outbound_payment_method_ids
            payment.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    def act_get_data(self):
        detail_obj = self.env['tbl_msi_pay_detail']

        self.env.cr.execute('SELECT id, date_due, date_invoice, partner_id, residual, journal_id FROM account_invoice WHERE partner_id = %s and state = %s' ,(self.partner_id.id,'open'))
        for row in self.env.cr.fetchall():
           self.env.cr.execute('SELECT id FROM account_journal WHERE id = %s and type = %s' ,(row[5],'sale'))
           for row2 in self.env.cr.fetchall():
             
                 data_line2 = detail_obj.create({
                    'pay_details': self.id,
                    'name': row[0],
                    'partner_id': row[3],
                    'amount': row[4],
                 })

    def action_confirm(self):
      self.state = 'confirm'


    def action_submit(self):
        detail_obj = self.env['account.payment']


        self.state = 'submit'



        data_line2 = detail_obj.create({
                    'payment_type': self.payment_type,
                    'partner_type': self.partner_type,
                    'partner_id': self.partner_id.id,
                    'amount': self.amount,
                    'journal_id': self.journal_id.id,
                    'payment_method_id': 1,

        })




class tbl_msi_pay_detail(models.Model):
    _name = 'tbl_msi_pay_detail'

    pay_details = fields.Many2one('account.payment','Detail Payment')
    name = fields.Many2one('account.invoice','Invoice', readonly=True)
    partner_id = fields.Many2one('res.partner','Customer', readonly=True)
    amount = fields.Float('Amount', readonly=True)
    amount_bayar = fields.Float('Amount Bayar')

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.partner_id = self.name.partner_id.id




class tbl_supplier_request(models.Model):
    _name = 'tbl_supplier_request'
    _inherit = ['mail.thread']

    company_id = fields.Many2one(store=True)
    name = fields.Char(readonly=True, copy=False) # The name is attributed upon post()
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('submit', 'Submit')], readonly=True, default='draft', copy=False, string="Status")


    payment_type = fields.Selection([('outbound', 'Send Money')], string='Payment Type', required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method", default=1,
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    payment_method_code = fields.Char(related='payment_method_id.code',
        help="Technical field used to adapt the interface to the payment type selected.", readonly=True)

    partner_type = fields.Selection([('supplier', 'Vendor')])
    partner_id = fields.Many2one('res.partner', string='Partner')

    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    pay_detail = fields.One2many('tbl_msi_pay_detail','pay_details','Invoice Detail')



    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_('The payment amount cannot be negative.'))

    @api.multi
    @api.depends('payment_type', 'journal_id')
    def _compute_hide_payment_method(self):
        for payment in self:
            if not payment.journal_id:
                payment.hide_payment_method = True
                continue
            journal_payment_methods = payment.payment_type == 'inbound'\
                and payment.journal_id.inbound_payment_method_ids\
                or payment.journal_id.outbound_payment_method_ids
            payment.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    def act_get_data(self):
        detail_obj = self.env['tbl_msi_pay_detail']

        self.env.cr.execute('SELECT id, date_due, date_invoice, partner_id, residual, journal_id FROM account_invoice WHERE partner_id = %s and state = %s' ,(self.partner_id.id,'open'))
        for row in self.env.cr.fetchall():
           self.env.cr.execute('SELECT id FROM account_journal WHERE id = %s and type = %s' ,(row[5],'sale'))
           for row2 in self.env.cr.fetchall():
             
                 data_line2 = detail_obj.create({
                    'pay_details': self.id,
                    'name': row[0],
                    'partner_id': row[3],
                    'amount': row[4],
                 })

    def action_confirm(self):
      self.state = 'confirm'


    def action_submit(self):
        detail_obj = self.env['account.payment']


        self.state = 'submit'



        data_line2 = detail_obj.create({
                    'payment_type': self.payment_type,
                    'partner_type': self.partner_type,
                    'partner_id': self.partner_id.id,
                    'amount': self.amount,
                    'journal_id': self.journal_id.id,
                    'payment_method_id': 1,

        })




