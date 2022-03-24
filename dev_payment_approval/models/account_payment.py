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
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def post_entry(self):
        for rec in self:
            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        return True
    
    
    @api.multi
    def post(self):
        for payment in self:
            if payment.company_id.payment_double_validation == 'two_step':
                if payment.amount <= (self.env.user.company_id.currency_id.compute(payment.company_id.payment_double_validation_amount, payment.currency_id)) or payment.user_has_groups('dev_payment_approval.double_verification_payment_right'):
                    if payment.company_id.payment_triple_validation == 'three_step':
                        if payment.amount <= (self.env.user.company_id.currency_id.compute(payment.company_id.payment_triple_validation_amount, payment.currency_id)) or payment.user_has_groups('dev_payment_approval.triple_verification_payment_right'):
                            payment.post_entry()
                        else:
                            payment.write({'state': 'second_approval'})
                    else:
                        payment.post_entry()
                else:
                    payment.write({'state': 'first_approval'})
            else:
                payment.post_entry()
    @api.multi
    def second_to_post(self):
        for payment in self:
            if payment.company_id.payment_triple_validation == 'three_step':
                if payment.amount <= (self.env.user.company_id.currency_id.compute(payment.company_id.payment_triple_validation_amount, payment.currency_id)) or payment.user_has_groups('dev_payment_approval.triple_verification_payment_right'):
                    payment.post_entry()
                else:
                    payment.write({'state': 'second_approval'})
            else:
                payment.post_entry()
    
    @api.multi
    def third_to_post(self):
        for payment in self:
            payment.post_entry()
                
    state = fields.Selection([('draft', 'Draft'),
                            ('first_approval', 'First Approval'), 
                            ('second_approval', 'Second Approval'), 
                            ('posted', 'Posted'),
                            ('sent', 'Sent'), 
                            ('reconciled', 'Reconciled'), 
                            ('cancelled', 'Cancelled')], 
                            readonly=True, default='draft', 
                            copy=False, string="Status")
    payment_difference_handling = fields.Selection([('open', 'Keep open')], default='open', string="Payment Difference", copy=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: