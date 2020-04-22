# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    """class for inherit account invoice"""
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        """extend function for add discount"""
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        res['discount'] = line.discount
        return res


class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.invoice.line'

    @api.depends('price_unit', 'discount')
    def _compute_net_price(self):
        """function for compute net_price in order line"""
        for line in self:
            tot_disc = (line.discount/100)*line.price_unit
            line.update({
                'display_discount': tot_disc,
            })

    display_discount = fields.Float(string='Discount', compute='_compute_net_price',
        digits=dp.get_precision('Discount'), default=0.0, store=True, readonly=True)
