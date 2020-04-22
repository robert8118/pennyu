# -*- coding: utf-8 -*- 
# Part of Odoo. See LICENSE file for full copyright and licensing details. 
import math
from odoo import api, fields, models 
from datetime import datetime
from odoo.exceptions import UserError, RedirectWarning, ValidationError

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        ailo = self.env['account.invoice.line']
        for move_line_dict in res:
            if move_line_dict.get('invl_id'):
                iline = ailo.browse(move_line_dict['invl_id'])
                accounts = iline.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=self.fiscal_position_id)
                #if accounts['discount_output'] or accounts['discount_input']:
                #    move_line_dict.update({'price': iline.price_undiscount})
                if self.type in ('in_invoice', 'out_refund') and accounts['discount_input'] and iline.discount:
                    move_line_dict.update({'price': iline.price_undiscount})
                elif self.type in ('out_invoice', 'in_refund') and accounts['discount_output'] and iline.discount:
                    move_line_dict.update({'price': iline.price_undiscount})
        #if self.type in ('out_invoice', 'out_refund'):
        for i_line in self.invoice_line_ids:
            if i_line.discount:
                res.extend(self._discount_move_lines(i_line, self.type))
        return res
    
    @api.model
    def _discount_move_lines(self, i_line, type):
        """Return the additional move lines for sales invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id
        price_discount_untaxed = i_line.price_discount_untaxed
        if inv.currency_id != company_currency:
            currency = inv.currency_id
            amount_currency = i_line._get_price(company_currency, price_discount_untaxed)
        else:
            currency = False
            amount_currency = False

        return self.env['product.product']._discount_move_lines(type, i_line.name, i_line.product_id, i_line.uom_id, 1, price_discount_untaxed, currency=currency, amount_currency=amount_currency, fiscal_position=inv.fiscal_position_id, account_analytic=i_line.account_analytic_id, analytic_tags=i_line.analytic_tag_ids)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
        
#     @api.one
#     @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
#         'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
#         'invoice_id.date_invoice', 'invoice_id.date')
    def _get_price_undiscount(self):
        for line in self:
            currency = line.invoice_id and line.invoice_id.currency_id or None
            line.price_undiscount = line.quantity * line.price_unit
            line.price_discount_untaxed = line.price_undiscount * ((line.discount or 0.0) / 100.0)
            #price = line.price_undiscount - line.price_discount_total
            #price_unit = line.price_unit
            taxes = taxes_unit = False
            if line.invoice_line_tax_ids:
                taxes = line.invoice_line_tax_ids.compute_all(line.price_discount_untaxed, currency, 1.0, product=line.product_id, partner=line.invoice_id.partner_id)
                taxes_unit = line.invoice_line_tax_ids.compute_all(line.price_unit, currency, 1.0, product=line.product_id, partner=line.invoice_id.partner_id)
            line.price_unit_undiscount_untaxed = taxes_unit['total_excluded'] if taxes_unit else line.price_unit
            line.price_undiscount_untaxed = line.quantity * line.price_unit_undiscount_untaxed
            line.price_discount_untaxed = taxes['total_excluded'] if taxes else line.price_discount_untaxed
            #line.price_undiscount_tax = line.price_discount_total - line.price_undiscount_untaxed
            price_undiscount_signed = line.price_undiscount_untaxed#line.price_undiscount - line.price_subtotal
            if line.invoice_id.currency_id and line.invoice_id.currency_id != line.invoice_id.company_id.currency_id:
                price_undiscount_signed = line.invoice_id.currency_id.with_context(date=line.invoice_id._get_currency_rate_date()).compute(price_undiscount_signed, line.invoice_id.company_id.currency_id)
            line.price_untaxed = line.price_subtotal
            line.price_undiscount_signed = price_undiscount_signed
        
    price_undiscount = fields.Monetary(string='Undiscount Amount', compute='_get_price_undiscount', store=False)
    price_unit_undiscount_untaxed = fields.Monetary(string='Price Untaxed', compute='_get_price_undiscount', store=False)
    price_undiscount_untaxed = fields.Monetary(string='Undiscount Tax Basis', compute='_get_price_undiscount', store=False)
    price_untaxed = fields.Monetary(string='Tax Basis', compute='_get_price_undiscount', store=False)
    #price_undiscount_tax = fields.Monetary(string='Undiscount Tax', compute='_get_price_undiscount', store=False, readonly=True)
    #price_undiscount_total = fields.Monetary(string='Undiscount Tax Basis', compute='_get_price_undiscount', store=False)
    price_undiscount_signed = fields.Monetary(string='Undiscount Amount Signed', compute='_get_price_undiscount', store=False)
    price_discount_untaxed = fields.Monetary(string='Disc Untaxed', compute='_get_price_undiscount', store=False)
#     @api.one
#     @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
#         'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
#         'invoice_id.date_invoice', 'invoice_id.date')
#     def _get_price_undiscount(self):
#         currency = self.invoice_id and self.invoice_id.currency_id or None
#         self.price_undiscount = self.quantity * self.price_unit
#         self.price_discount_total = self.price_undiscount * ((self.discount or 0.0) / 100.0)
#         price = self.price_undiscount - self.price_discount_total
#         taxes = False
#         if self.invoice_line_tax_ids:
#             taxes = self.invoice_line_tax_ids.compute_all(price, currency, 1.0, product=self.product_id, partner=self.invoice_id.partner_id)
#         self.price_undiscount_untaxed = taxes['total_excluded'] if taxes else price
#         
#         self.price_undiscount_total = price_undiscount_signed = self.price_discount_total#self.price_undiscount - self.price_subtotal
#         if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
#             price_undiscount_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_undiscount_signed, self.invoice_id.company_id.currency_id)
#         self.price_undiscount_signed = price_undiscount_signed
#         
#     price_undiscount = fields.Monetary(string='Undiscount Amount', compute='_get_price_undiscount', store=False, readonly=True)
#     price_undiscount_untaxed = fields.Monetary(string='Tax Basis', compute='_get_price_undiscount', store=False, readonly=True)
#     price_undiscount_total = fields.Monetary(string='Undiscount Total', compute='_get_price_undiscount', store=False, readonly=True)
#     price_undiscount_signed = fields.Monetary(string='Undiscount Amount Signed', compute='_get_price_undiscount', store=False, readonly=True)
#     price_discount_total = fields.Monetary(string='Disc Amount', compute='_get_price_undiscount', store=False, readonly=True)