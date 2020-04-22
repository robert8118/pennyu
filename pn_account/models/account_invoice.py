# -*- coding: utf-8 -*-
"""pn_account/account_invoice"""
from odoo import api, models, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    """inherit model account.invoice"""
    _inherit = 'account.invoice'

    @api.multi
    def total_terbilang(self, amount_total):
        """function to converting amount total into word"""
        unit = ["","Satu","Dua","Tiga","Empat",
                "Lima","Enam","Tujuh","Delapan",
                "Sembilan","Sepuluh","Sebelas"]
        result = " "
        total_terbilang = self.total_terbilang
        for line in self:
            n = int(amount_total)
            if n >= 0 and n <= 11:
                result = result + unit[n]
            elif n < 20:
                result = total_terbilang(n % 10) + " Belas"
            elif n < 100:
                result = total_terbilang(n / 10) + " Puluh" + total_terbilang(n % 10)
            elif n < 200:
                result = " Seratus" + total_terbilang(n - 100)
            elif n < 1000:
                result = total_terbilang(n / 100) + " Ratus" + total_terbilang(n % 100)
            elif n < 2000:
                result = " Seribu" + total_terbilang(n - 1000)
            elif n < 1000000:
                result = total_terbilang(n / 1000) + " Ribu" + total_terbilang(n % 1000)
            elif n < 1000000000:
                result = total_terbilang(n / 1000000) + " Juta" + total_terbilang(n % 1000000)
            else:
                result = total_terbilang(n / 1000000000) + " Miliar" + total_terbilang(n % 1000000000)
            return result

    @api.multi
    def currency_word(self):
        """function to converting currency into word"""
        result = " "
        for cr in self:
            if cr.currency_id.name == 'USD':
                result = " Dollar"
            elif cr.currency_id.name == 'EUR':
                result = " Euro"
            elif cr.currency_id.name == 'JPY':
                result = " Yen"
            elif cr.currency_id.name == 'IDR':
                result = " Rupiah"
            else:
                result = " "
            return result

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """extend function for fill some data to refund"""
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        if invoice.payment_term_id:
            values['payment_term_id'] = invoice.payment_term_id.id
        elif invoice.partner_id.property_payment_term_id:
            values['payment_term_id'] = invoice.partner_id.property_payment_term_id.id
        return values

    @api.model
    def create(self, vals):
        '''extend function create to add warning if payment term
        customer is different with payment term invoice'''
        res = super(AccountInvoice, self).create(vals)
        if 'payment_term_id' in vals:
            partner_id = res.partner_id
            payment_term_id = partner_id.property_payment_term_id
            if payment_term_id and payment_term_id.id != res.payment_term_id.id:
                raise Warning("Cannot change Payment Term!")
        return res

    @api.multi
    def write(self, vals):
        '''extend function write to add warning if payment term
        customer is different with payment term invoice'''
        res = super(AccountInvoice, self).write(vals)
        if 'payment_term_id' in vals:
            for inv in self:
                partner_id = inv.partner_id
                payment_term_id = partner_id.property_payment_term_id
                if payment_term_id and payment_term_id.id != inv.payment_term_id.id:
                    raise Warning("Cannot change Payment Term!")
        return res
